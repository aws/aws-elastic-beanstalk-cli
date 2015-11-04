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

from ..core import fileoperations, io
from ..core.abstractcontroller import AbstractBaseController
from ..lib import utils, elasticbeanstalk, aws
from ..objects import solutionstack, region as regions
from ..objects.exceptions import NotInitializedError, NoRegionError, \
    InvalidProfileError
from ..operations import commonops, initializeops, sshops
from ..resources.strings import strings, flag_text


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
        ]
        usage = 'eb init <application_name> [options ...]'
        epilog = strings['init.epilog']

    def do_command(self):
        # get arguments
        self.interactive = self.app.pargs.interactive
        self.region = self.app.pargs.region
        self.noverify = self.app.pargs.no_verify_ssl
        self.flag = False
        if self.app.pargs.platform:
            self.flag = True
        self.modules = self.app.pargs.modules

        # The user specifies directories to initialize
        if self.modules and len(self.modules) > 0:
            self.initialize_multiple_directories()
            return

        default_env = self.get_old_values()
        fileoperations.touch_config_folder()

        if self.interactive:
            self.region = self.get_region()
        else:
            self.region = self.get_region_from_inputs()
        aws.set_region(self.region)

        self.set_up_credentials()

        self.solution = self.get_solution_stack()
        self.app_name = self.get_app_name()
        if self.noverify:
            fileoperations.write_config_setting('global',
                                                'no-verify-ssl', True)

        if not default_env and not self.interactive:
            # try to get default env from config file if exists
            try:
                default_env = commonops.get_current_branch_environment()
            except NotInitializedError:
                default_env = None
        elif self.interactive:
            default_env = None

        if self.flag:
            default_env = '/ni'

        # Create application
        sstack, key = commonops.create_app(self.app_name,
                                           default_env=default_env)

        if not self.solution:
            self.solution = sstack

        platform_set = False
        if not self.solution or \
                (self.interactive and not self.app.pargs.platform):
            if fileoperations.env_yaml_exists():
                env_yaml_platform = fileoperations.get_platform_from_env_yaml()
                if env_yaml_platform:
                    platform = solutionstack.SolutionStack(env_yaml_platform).version
                    self.solution = platform
                    platform_set = True

            if not platform_set:
                result = commonops.prompt_for_solution_stack()
                self.solution = result.version

        initializeops.setup(self.app_name, self.region, self.solution)

        if 'IIS' not in self.solution:
            self.keyname = self.get_keyname(default=key)

            if self.keyname == -1:
                self.keyname = None

            fileoperations.write_config_setting('global', 'default_ec2_keyname',
                                                self.keyname)

    def check_credentials(self, profile):
        given_profile = self.app.pargs.profile
        try:
            # Note, region is None unless explicitly set
            ## or read from old eb
            initializeops.credentials_are_valid()
            return profile
        except NoRegionError:
            self.region = self.get_region()
            aws.set_region(self.region)
            return profile
        except InvalidProfileError:
            if given_profile:
                # Provided profile is invalid, raise exception
                raise
            else:
                # eb-cli profile doesnt exist, revert to default
                # try again
                profile = None
                aws.set_profile(profile)
                return self.check_credentials(profile)

    def set_up_credentials(self):
        given_profile = self.app.pargs.profile
        if given_profile:
            ## Profile already set at abstractController
            profile = given_profile
        else:
            profile = 'eb-cli'
            aws.set_profile(profile)

        profile = self.check_credentials(profile)

        if not initializeops.credentials_are_valid():
            initializeops.setup_credentials()
        else:
            fileoperations.write_config_setting('global', 'profile',
                                                profile)

    def get_app_name(self):
        # Get app name from command line arguments
        app_name = self.app.pargs.application_name

        # Get app name from config file, if exists
        if not app_name:
            try:
                app_name = fileoperations.get_application_name(default=None)
            except NotInitializedError:
                app_name = None

        if not app_name and self.flag:
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

    def get_region_from_inputs(self):
        # Get region from command line arguments
        region = self.app.pargs.region

        # Get region from config file
        if not region:
            try:
                region = commonops.get_default_region()
            except NotInitializedError:
                region = None

        return region

    def get_region(self):
        # Get region from command line arguments
        region = self.get_region_from_inputs()

        # Ask for region
        if (not region) and self.flag:
            # Choose defaults
            region_list = regions.get_all_regions()
            region = region_list[2].name

        if not region or \
                (self.interactive and not self.app.pargs.region):
            io.echo()
            io.echo('Select a default region')
            region_list = regions.get_all_regions()
            result = utils.prompt_for_item_in_list(region_list, default=3)
            region = result.name

        return region

    def get_solution_stack(self):
        # Get solution stack from command line arguments
        solution_string = self.app.pargs.platform

        # Get solution stack from config file, if exists
        if not solution_string:
            try:
                solution_string = commonops.get_default_solution_stack()
            except NotInitializedError:
                solution_string = None

        if solution_string:
            commonops.get_solution_stack(solution_string)

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

        if self.flag and not self.interactive:
            return keyname

        if keyname is None or \
                (self.interactive and not self.app.pargs.keyname):
            # Prompt for one
            keyname = sshops.prompt_for_ec2_keyname()

        elif keyname != -1:
            commonops.upload_keypair_if_needed(keyname)

        return keyname

    def complete_command(self, commands):
        self.complete_region(commands)
        #Note, completing solution stacks is only going to work
        ## if they already have their keys set up with region
        if commands[-1] in ['-s', '--solution']:
            io.echo(*elasticbeanstalk.get_available_solution_stacks())

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
                        self.region = self.get_region()
                    else:
                        self.region = self.get_region_from_inputs()
                    aws.set_region(self.region)

                self.set_up_credentials()

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

                if self.flag:
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
                if not solution or \
                        (self.interactive and not self.app.pargs.platform):
                    if fileoperations.env_yaml_exists():
                        env_yaml_platform = fileoperations.get_platform_from_env_yaml()
                        if env_yaml_platform:
                            platform = solutionstack.SolutionStack(env_yaml_platform).version
                            solution = platform
                            io.echo(strings['init.usingenvyamlplatform'].replace('{platform}', platform))
                            platform_set = True

                    if not platform_set:
                        result = commonops.prompt_for_solution_stack()
                        solution = result.version

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
    app_list = commonops.get_application_names()
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