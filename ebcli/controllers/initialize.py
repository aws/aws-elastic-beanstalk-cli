# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import sys
import os.path

from cement.utils.misc import minimal_logger

from ebcli.core import fileoperations, io
from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.lib import utils, elasticbeanstalk, codecommit, aws
from ebcli.objects.sourcecontrol import SourceControl
from ebcli.objects import solutionstack, region as regions
from ebcli.objects.platform import PlatformVersion
from ebcli.objects.exceptions import(
    CommandError,
    InvalidProfileError,
    NoRegionError,
    NotInitializedError,
    ServiceError,
    ValidationError,
)
from ebcli.operations import (
	commonops,
	gitops,
	initializeops,
	platformops,
	solution_stack_ops,
	sshops
)
from ebcli.resources.strings import strings, flag_text, prompts

LOG = minimal_logger(__name__)

class InitController(AbstractBaseController):
    class Meta:
        label = 'init'
        description = strings['init.info']
        arguments = [
            (['application_name'], dict(
                help=flag_text['init.name'], nargs='?', default=[])),
            (['-m', '--modules'], dict(help=flag_text['init.module'], nargs='*')),
            (['-p', '--platform'], dict(help=flag_text['init.platform'])),
            (['-k', '--keyname'], dict(help=flag_text['init.keyname'])),
            (['-i', '--interactive'], dict(
                action='store_true', help=flag_text['init.interactive'])),
            (['--source'], dict(help=flag_text['init.source'])),
        ]
        usage = 'eb init <application_name> [options ...]'
        epilog = strings['init.epilog']

    def do_command(self):
        # get arguments
        self.interactive = self.app.pargs.interactive
        self.region = self.app.pargs.region
        self.noverify = self.app.pargs.no_verify_ssl
        self.force_non_interactive = False

        # Determine if the customer is avoiding interactive mode by setting the platform flag
        if self.app.pargs.platform:
            self.force_non_interactive = True

        # The user specifies directories to initialize
        self.modules = self.app.pargs.modules
        if self.modules and len(self.modules) > 0:
            self.initialize_multiple_directories()
            return

        source_location, branch, repository = None, None, None
        if self.app.pargs.source:
            source_location, repository, branch = utils.parse_source(self.app.pargs.source)

        default_env = self.get_old_values()
        fileoperations.touch_config_folder()

        self.region = set_region_for_application(self.interactive, self.region, self.force_non_interactive)

        self.region = set_up_credentials(self.app.pargs.profile, self.region, self.interactive)

        self.solution = self.get_solution_stack()
        self.app_name = self.get_app_name()
        if self.noverify:
            fileoperations.write_config_setting('global',
                                                'no-verify-ssl', True)

        default_env = set_default_env(default_env, self.interactive, self.force_non_interactive)

        sstack, key = create_app_or_use_existing_one(self.app_name, default_env)
        self.solution = self.solution or sstack

        if fileoperations.env_yaml_exists():
            self.solution = self.solution or extract_solution_stack_from_env_yaml()
        self.solution = self.solution or solution_stack_ops.get_solution_stack_from_customer().platform_shorthand

        handle_buildspec_image(self.solution, self.force_non_interactive)

        # Setup code commit integration
        # Ensure that git is setup
        source_control = SourceControl.get_source_control()
        try:
            source_control_setup = source_control.is_setup()
            if source_control_setup is None:
                source_control_setup = False
        except CommandError:
            source_control_setup = False

        default_branch_exists = not not (gitops.git_management_enabled() and not self.interactive)

        if source_location and not codecommit.region_supported(self.region):
            io.log_warning(strings['codecommit.badregion'])

        # Prompt customer to opt into CodeCommit unless one of the follows holds:
        if self.force_non_interactive:
            prompt_codecommit = False
        elif not codecommit.region_supported(self.region):
            prompt_codecommit = False
        elif source_location and source_location.lower() != 'codecommit':
            # Do not prompt if customer has already specified a code source to
            # associate the EB workspace with
            prompt_codecommit = False
        elif default_branch_exists:
            # Do not prompt if customer has already configured the EB application
            # in the present working directory with Git
            prompt_codecommit = False
        elif not source_control_setup:
            if source_location:
                io.echo(strings['codecommit.nosc'])
            prompt_codecommit = False
        else:
            prompt_codecommit = True

        # Prompt for interactive CodeCommit
        if prompt_codecommit:
            try:
                if not source_location:
                    io.validate_action(prompts['codecommit.usecc'], "y")

                # Setup git config settings for code commit credentials
                source_control.setup_codecommit_cred_config()

                # Get user specified repository
                remote_url = None
                if repository is None:
                    repository = get_repository_interactive()
                else:
                    try:
                        setup_codecommit_remote_repo(repository, source_control)
                    except ServiceError as ex:
                        if source_location:
                            create_codecommit_repository(repository)
                            setup_codecommit_remote_repo(repository, source_control)
                        else:
                            io.log_error(strings['codecommit.norepo'])
                            raise ex

                # Get user specified branch
                if branch is None:
                    branch = get_branch_interactive(repository)
                else:
                    try:
                        codecommit.get_branch(repository, branch)
                    except ServiceError as ex:
                        if source_location:
                            create_codecommit_branch(source_control, branch)
                        else:
                            io.log_error(strings['codecommit.nobranch'])
                            raise ex
                    source_control.setup_existing_codecommit_branch(branch, remote_url)

            except ValidationError:
                LOG.debug("Denied option to use CodeCommit, continuing initialization")

        # Initialize the whole setup
        initializeops.setup(self.app_name, self.region, self.solution, dir_path=None, repository=repository, branch=branch)

        if 'IIS' not in self.solution:
            self.keyname = self.get_keyname(default=key)

            if self.keyname == -1:
                self.keyname = None

            fileoperations.write_config_setting('global', 'default_ec2_keyname',
                                                self.keyname)

        # Default to including git submodules when creating zip files through `eb create`/`eb deploy`.
        fileoperations.write_config_setting('global', 'include_git_submodules', True)

    def get_app_name(self):
        # Get app name from command line arguments
        app_name = self.app.pargs.application_name

        # Get app name from config file, if exists
        if not app_name:
            try:
                app_name = fileoperations.get_application_name(default=None)
            except NotInitializedError:
                app_name = None

        if not app_name and self.force_non_interactive:
            # Choose defaults
            app_name = fileoperations.get_current_directory_name()

        # Ask for app name
        if not app_name or \
                (self.interactive and not self.app.pargs.application_name):
            app_name = _get_application_name_interactive()

        if sys.version_info[0] < 3 and isinstance(app_name, unicode):
            try:
                app_name.encode('utf8').encode('utf8')
                app_name = app_name.encode('utf8')
            except UnicodeDecodeError:
                pass

        return app_name

    def get_solution_stack(self):
        # Get solution stack from command line arguments
        solution_string = self.app.pargs.platform

        # Get solution stack from config file, if exists
        if not solution_string:
            try:
                solution_string = solution_stack_ops.get_default_solution_stack()
            except NotInitializedError:
                solution_string = None

        # Validate that the platform exists
        if solution_string:
            solution_stack_ops.find_solution_stack_from_string(solution_string)

        return solution_string

    def get_keyname(self, default=None):
        keyname = self.app.pargs.keyname

        if not keyname:
            keyname = default

        # Get keyname from config file, if exists
        if not keyname:
            try:
                keyname = commonops.get_default_keyname()
            except NotInitializedError:
                keyname = None

        if self.force_non_interactive and not self.interactive:
            return keyname

        if keyname is None or \
                (self.interactive and not self.app.pargs.keyname):
            # Prompt for one
            keyname = sshops.prompt_for_ec2_keyname()

        elif keyname != -1:
            commonops.upload_keypair_if_needed(keyname)

        return keyname

    def get_old_values(self):
        if fileoperations.old_eb_config_present() and \
                not fileoperations.config_file_present():
            old_values = fileoperations.get_values_from_old_eb()
            region = old_values['region']
            access_id = old_values['access_id']
            secret_key = old_values['secret_key']
            solution_stack = old_values['platform']
            app_name = old_values['app_name']
            default_env = old_values['default_env']

            io.echo(strings['init.getvarsfromoldeb'])
            if self.region is None:
                self.region = region
            if not self.app.pargs.application_name:
                self.app.pargs.application_name = app_name
            if self.app.pargs.platform is None:
                self.app.pargs.platform = solution_stack

            initializeops.setup_credentials(access_id=access_id,
                                         secret_key=secret_key)
            return default_env

        return None

    def initialize_multiple_directories(self):
        application_created = False
        self.app_name = None
        cwd = os.getcwd()
        for module in self.modules:
            if os.path.exists(module) and os.path.isdir(module):
                os.chdir(module)
                fileoperations.touch_config_folder()

                # Region should be set once for all modules
                if not self.region:
                    if self.interactive:
                        self.region = get_region(self.region, self.interactive, self.force_non_interactive)
                    else:
                        self.region = get_region_from_inputs(self.app.pargs.region)
                    aws.set_region(self.region)

                self.region = set_up_credentials(self.app.pargs.profile, self.region, self.interactive)

                solution = self.get_solution_stack()

                # App name should be set once for all modules
                if not self.app_name:
                    # Switching back to the root dir will suggest the root dir name
                    # as the application name
                    os.chdir(cwd)
                    self.app_name = self.get_app_name()
                    os.chdir(module)

                if self.noverify:
                    fileoperations.write_config_setting('global',
                                                        'no-verify-ssl', True)

                default_env = None

                if self.force_non_interactive:
                    default_env = '/ni'

                if not application_created:
                    sstack, key = commonops.create_app(self.app_name,
                                                       default_env=default_env)
                    application_created = True
                else:
                    sstack, key = commonops.pull_down_app_info(self.app_name,
                                                               default_env=default_env)

                io.echo('\n--- Configuring module: {0} ---'.format(module))

                if not solution:
                    solution = sstack

                platform_set = False
                # TODO: Do not require a solution stack if one has already been set by this point
                if not solution or \
                        (self.interactive and not self.app.pargs.platform):
                    if fileoperations.env_yaml_exists():
                        env_yaml_platform = fileoperations.get_platform_from_env_yaml()
                        if env_yaml_platform:
                            platform = solutionstack.SolutionStack(env_yaml_platform).platform_shorthand
                            solution = platform
                            io.echo(strings['init.usingenvyamlplatform'].replace('{platform}', platform))
                            platform_set = True

                    if not platform_set:
                        solution = solution_stack_ops.get_solution_stack_from_customer()

                initializeops.setup(self.app_name, self.region,
                                    solution)

                if 'IIS' not in solution:
                    keyname = self.get_keyname(default=key)

                    if keyname == -1:
                        self.keyname = None

                    fileoperations.write_config_setting('global', 'default_ec2_keyname',
                                                        keyname)
                os.chdir(cwd)


def _get_application_name_interactive():
    app_list = elasticbeanstalk.get_application_names()
    file_name = fileoperations.get_current_directory_name()
    new_app = False
    if len(app_list) > 0:
        io.echo()
        io.echo('Select an application to use')
        new_app_option = '[ Create new Application ]'
        app_list.append(new_app_option)
        try:
            default_option = app_list.index(file_name) + 1
        except ValueError:
            default_option = len(app_list)
        app_name = utils.prompt_for_item_in_list(app_list,
                                                 default=default_option)
        if app_name == new_app_option:
            new_app = True

    if len(app_list) == 0 or new_app:
        io.echo()
        io.echo('Enter Application Name')
        unique_name = utils.get_unique_name(file_name, app_list)
        app_name = io.prompt_for_unique_name(unique_name, app_list)

    return app_name


# Code Commit repository setup methods
def get_repository_interactive():
    source_control = SourceControl.get_source_control()
    # Give list of code commit repositories to use
    new_repo = False
    repo_list = codecommit.list_repositories()["repositories"]

    current_repository = source_control.get_current_repository()
    current_repository = current_repository or fileoperations.get_current_directory_name()

    # If there are existing repositories prompt the user to pick one
    # otherwise set default as the file name
    if len(repo_list) > 0:
        repo_list = list(map(lambda r: r["repositoryName"], repo_list))
        io.echo()
        io.echo('Select a repository')
        new_repo_option = '[ Create new Repository ]'
        repo_list.append(new_repo_option)

        try:
            default_option = repo_list.index(current_repository) + 1
        except ValueError:
            default_option = len(repo_list)
        repo_name = utils.prompt_for_item_in_list(repo_list,
                                                 default=default_option)
        if repo_name == new_repo_option:
            new_repo = True

    # Create a new repository if the user specifies or there are no existing repositories
    if len(repo_list) == 0 or new_repo:
        io.echo()
        io.echo('Enter Repository Name')
        unique_name = utils.get_unique_name(current_repository, repo_list)
        repo_name = io.prompt_for_unique_name(unique_name, repo_list)

        create_codecommit_repository(repo_name)

    return repo_name


def create_codecommit_repository(repo_name):
    # Create the repository if we get here
    codecommit.create_repository(repo_name, "Created with EB CLI")
    io.echo("Successfully created repository: {0}".format(repo_name))


def setup_codecommit_remote_repo(repository, source_control):
    result = codecommit.get_repository(repository)
    remote_url = result['repositoryMetadata']['cloneUrlHttp']
    source_control.setup_codecommit_remote_repo(remote_url=remote_url)


def create_codecommit_branch(source_control, branch_name):
    current_commit = source_control.get_current_commit()

    # Creating the branch requires that we setup the remote branch first
    # to ensure the code commit branch is synced with the local branch
    if current_commit is None:
        # TODO: Test on windows for weird empty returns with the staged files
        staged_files = source_control.get_list_of_staged_files()
        if not staged_files:
            source_control.create_initial_commit()
        else:
            LOG.debug("Cannot create placeholder commit because there are staged files: {0}".format(staged_files))
            io.echo("Could not set create a commit with staged files; cannot setup CodeCommit branch without a commit")
            return None

    source_control.setup_new_codecommit_branch(branch_name=branch_name)
    io.echo("Successfully created branch: {0}".format(branch_name))


def get_branch_interactive(repository):
    source_control = SourceControl.get_source_control()
    # Give list of code commit branches to use
    new_branch = False
    branch_list = codecommit.list_branches(repository)["branches"]
    current_branch = source_control.get_current_branch()

    # If there are existing branches prompt the user to pick one
    if len(branch_list) > 0:
        io.echo('Select a branch')
        new_branch_option = '[ Create new Branch with local HEAD ]'
        branch_list.append(new_branch_option)
        try:
            default_option = branch_list.index(current_branch) + 1
        except ValueError:
            default_option = len(branch_list)
        branch_name = utils.prompt_for_item_in_list(branch_list,
                                                    default=default_option)
        if branch_name == new_branch_option:
            new_branch = True

    # Create a new branch if the user specifies or there are no existing branches

    if len(branch_list) == 0 or new_branch:
        new_branch = True
        io.echo()
        io.echo('Enter Branch Name')
        io.echo('***** Must have at least one commit to create a new branch with CodeCommit *****')
        unique_name = utils.get_unique_name(current_branch, branch_list)
        branch_name = io.prompt_for_unique_name(unique_name, branch_list)

    # Setup git to push to this repo
    result = codecommit.get_repository(repository)
    remote_url = result['repositoryMetadata']['cloneUrlHttp']
    source_control.setup_codecommit_remote_repo(remote_url=remote_url)

    if len(branch_list) == 0 or new_branch:
        LOG.debug("Creating a new branch")
        try:
            create_codecommit_branch(source_control, branch_name)
        except ServiceError:
            io.echo("Could not set CodeCommit branch with the current commit, run with '--debug' to get the full error")
            return None
    elif not new_branch:
        LOG.debug("Setting up an existing branch")
        succesful_branch = source_control.setup_existing_codecommit_branch(branch_name, remote_url)
        if not succesful_branch:
            io.echo("Could not set CodeCommit branch, run with '--debug' to get the full error")
            return None

    return branch_name


def check_credentials(profile, given_profile, given_region, interactive, force_non_interactive):
    try:
        # Note, region is None unless explicitly set or read from old eb
        initializeops.credentials_are_valid()
        return profile, given_region
    except NoRegionError:
        region = get_region(None, interactive, force_non_interactive)
        aws.set_region(region)
        return profile, region
    except InvalidProfileError as e:
        if given_profile:
            # Provided profile is invalid, raise exception
            raise e
        else:
            # eb-cli profile doesnt exist, revert to default
            # try again
            profile = None
            aws.set_profile(profile)
            return check_credentials(profile, given_profile, given_region, interactive, force_non_interactive)


def create_app_or_use_existing_one(app_name, default_env):
    if elasticbeanstalk.application_exist(app_name):
        return commonops.pull_down_app_info(app_name, default_env=default_env)
    else:
        return commonops.create_app(app_name, default_env=default_env)


def set_up_credentials(given_profile, given_region, interactive, force_non_interactive=False):
    if given_profile:
        # Profile already set at abstractController
        profile = given_profile
    else:
        profile = 'eb-cli'
        aws.set_profile(profile)

    profile, region = check_credentials(profile, given_profile, given_region, interactive, force_non_interactive)

    if not initializeops.credentials_are_valid():
        initializeops.setup_credentials()
    else:
        fileoperations.write_config_setting('global', 'profile', profile)

    return region


def extract_solution_stack_from_env_yaml():
    env_yaml_platform = fileoperations.get_platform_from_env_yaml()
    if env_yaml_platform:
        platform = solutionstack.SolutionStack(env_yaml_platform).platform_shorthand
        return platform


def get_region_from_inputs(region):
    # Get region from config file
    if not region:
        try:
            region = commonops.get_default_region()
        except NotInitializedError:
            region = None

    return region


def get_region(region_argument, interactive, force_non_interactive=False):
    # Get region from command line arguments
    region = get_region_from_inputs(region_argument)

    # Ask for region
    if (not region) and force_non_interactive:
        # Choose defaults
        region_list = regions.get_all_regions()
        region = region_list[2].name

    if not region or (interactive and not region_argument):
        io.echo()
        io.echo('Select a default region')
        region_list = regions.get_all_regions()
        result = utils.prompt_for_item_in_list(region_list, default=3)
        region = result.name

    return region


def handle_buildspec_image(solution, force_non_interactive):
    if not fileoperations.build_spec_exists():
        return

    build_spec = fileoperations.get_build_configuration()
    if not force_non_interactive and build_spec and build_spec.image is None:
        LOG.debug("Buildspec file is present but image is does not exist. Attempting to fill best guess.")
        platform_image = initializeops.get_codebuild_image_from_platform(solution)

        if type(platform_image) is dict:
            io.echo(strings['codebuild.latestplatform'].replace('{platform}', solution))
        else:
            io.echo(prompts['codebuild.getplatform'].replace('{platform}', solution))
            selected = utils.prompt_for_index_in_list([image['description'] for image in platform_image][0])
            platform_image = [image for image in platform_image if selected == image['description']][0]
        fileoperations.write_buildspec_config_header('Image', platform_image['name'])


def set_default_env(default_env, interactive, force_non_interactive):
    if default_env:
        return default_env

    if force_non_interactive:
        return '/ni'

    if not interactive:
        try:
            return commonops.get_current_branch_environment()
        except NotInitializedError:
            pass


def set_region_for_application(interactive, region, force_non_interactive):
    if interactive or (not region and not force_non_interactive):
        region = get_region(region, interactive, force_non_interactive)
    else:
        region = get_region_from_inputs(region)
    aws.set_region(region)

    return region
