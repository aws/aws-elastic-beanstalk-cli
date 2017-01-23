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
import time
import re

from cement.utils.misc import minimal_logger
from ebcli.operations import gitops, buildspecops

from ebcli.lib import elasticbeanstalk, iam_role, utils
from ebcli.lib.aws import InvalidParameterValueError
from ebcli.core import io, fileoperations
from ebcli.objects.exceptions import TimeoutError, AlreadyExistsError, \
    NotAuthorizedError
from ebcli.resources.strings import strings, responses, prompts
from ebcli.operations import commonops
import json

LOG = minimal_logger(__name__)

# TODO: Make unit tests for these changes
def make_new_env(env_request, branch_default=False, process_app_version=False,
                 nohang=False, interactive=True, timeout=None, source=None, lambda_subdir=None):
    iam_role.resolve_roles(env_request, interactive)

    # Parse and get Build Configuration from BuildSpec if it exists
    build_config = None
    if fileoperations.build_spec_exists():
        build_config = fileoperations.get_build_configuration()
        LOG.debug("Retrieved build configuration from buildspec: {0}".format(build_config.__str__()))

    # deploy code
    codecommit_setup = gitops.git_management_enabled()
    if not env_request.sample_application and not env_request.version_label:
        if source is not None:
            io.log_info('Creating new application version using remote source')
            io.echo("Starting environment deployment via remote source")
            env_request.version_label = commonops.create_app_version_from_source(
                env_request.app_name, source, process=process_app_version, label=env_request.version_label,
                build_config=build_config)
            process_app_version = True
        elif codecommit_setup:
            io.log_info('Creating new application version using CodeCommit')
            io.echo("Starting environment deployment via CodeCommit")
            env_request.version_label = \
                commonops.create_codecommit_app_version(env_request.app_name, process=process_app_version,
                                                        build_config=build_config)
            process_app_version = True
        else:
            io.log_info('Creating new application version using project code')
            env_request.version_label = \
                commonops.create_app_version(env_request.app_name, process=process_app_version,
                                             build_config=build_config, lambda_subdir=lambda_subdir)

        if build_config is not None:
            buildspecops.stream_build_configuration_app_version_creation(env_request.app_name, env_request.version_label)
        elif process_app_version is True:
            success = commonops.wait_for_processed_app_versions(env_request.app_name,
                                                                [env_request.version_label])
            if not success:
                return

    if env_request.version_label is None or env_request.sample_application:
        env_request.version_label = \
            commonops.create_dummy_app_version(env_request.app_name)

    # Create env
    if env_request.key_name:
        commonops.upload_keypair_if_needed(env_request.key_name)

    io.log_info('Creating new environment')
    result, request_id = create_env(env_request,
                                    interactive=interactive)

    env_name = result.name  # get the (possibly) updated name

    # Edit configurations
    ## Get default environment
    default_env = commonops.get_current_branch_environment()
    ## Save env as branch default if needed
    if not default_env or branch_default:
        commonops.set_environment_for_current_branch(env_name)
        if codecommit_setup:
            io.echo("Setting up default branch")
            gitops.set_branch_default_for_current_environment(gitops.get_default_branch())
            gitops.set_repo_default_for_current_environment(gitops.get_default_repository())

    # Print status of env
    commonops.print_env_details(result, health=False)

    if nohang:
        return

    io.echo('Printing Status:')
    try:
        commonops.wait_for_success_events(request_id,
                                          timeout_in_minutes=timeout)
    except TimeoutError:
        io.log_error(strings['timeout.error'])


def create_env(env_request, interactive=True):
    # If a template is being used, we want to try using just the template
    if env_request.template_name:
        platform = env_request.platform
        env_request.platform = None
    else:
        platform = None
    while True:
        try:
            return elasticbeanstalk.create_environment(env_request)

        except InvalidParameterValueError as e:
            if e.message == responses['app.notexists'].replace(
                        '{app-name}', '\'' + env_request.app_name + '\''):
                # App doesnt exist, must be a new region.
                ## Lets create the app in the region
                commonops.create_app(env_request.app_name)
            elif e.message == responses['create.noplatform']:
                if platform:
                    env_request.platform = platform
                else:
                    raise
            elif interactive:
                LOG.debug('creating env returned error: ' + e.message)
                if re.match(responses['env.cnamenotavailable'], e.message):
                    io.echo(prompts['cname.unavailable'])
                    cname = io.prompt_for_cname()
                elif re.match(responses['env.nameexists'], e.message):
                    io.echo(strings['env.exists'])
                    current_environments = commonops.get_all_env_names()
                    unique_name = utils.get_unique_name(env_request.env_name,
                                                        current_environments)
                    env_request.env_name = io.prompt_for_environment_name(
                        default_name=unique_name)
                elif e.message == responses['app.notexists'].replace(
                            '{app-name}', '\'' + env_request.app_name + '\''):
                    # App doesnt exist, must be a new region.
                    ## Lets create the app in the region
                    commonops.create_app(env_request.app_name)
                else:
                    raise
            else:
                raise

        # Try again with new values

