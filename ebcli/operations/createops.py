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

import re

from cement.utils.misc import minimal_logger

from ..lib import elasticbeanstalk, iam, utils
from ..lib.aws import InvalidParameterValueError
from ..core import io
from ..objects.exceptions import TimeoutError, AlreadyExistsError, \
    NotAuthorizedError
from ..resources.strings import strings, responses, prompts
from . import commonops

LOG = minimal_logger(__name__)
DEFAULT_ROLE_NAME = 'aws-elasticbeanstalk-ec2-role'


def make_new_env(env_request, branch_default=False,
                 nohang=False, interactive=True, timeout=None):
    if env_request.instance_profile is None and \
                            env_request.template_name is None:
        # Service supports no profile, however it is not good/recommended
        # Get the eb default profile
        env_request.instance_profile = get_default_profile()

    # deploy code
    if not env_request.sample_application and not env_request.version_label:
        io.log_info('Creating new application version using project code')
        env_request.version_label = \
            commonops.create_app_version(env_request.app_name)

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


def get_default_profile():
    """  Get the default elasticbeanstalk IAM profile,
            Create it if it doesn't exist """

    # get list of profiles
    try:
        profile = DEFAULT_ROLE_NAME
        try:
            iam.create_instance_profile(profile)
            role = get_default_role()
            iam.add_role_to_profile(profile, role)
        except AlreadyExistsError:
            pass
    except NotAuthorizedError:
        # Not a root account. Just assume role exists
        return DEFAULT_ROLE_NAME

    return profile


def get_default_role():
    role = DEFAULT_ROLE_NAME
    document = '{"Version": "2008-10-17","Statement": [{"Action":' \
               ' "sts:AssumeRole","Principal": {"Service": ' \
               '"ec2.amazonaws.com"},"Effect": "Allow","Sid": ""}]}'
    try:
        iam.create_role(role, document)
    except AlreadyExistsError:
        pass
    return role