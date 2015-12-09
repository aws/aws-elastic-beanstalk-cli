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
import time

from cement.utils.misc import minimal_logger

from ..lib import elasticbeanstalk, iam, utils
from ..lib.aws import InvalidParameterValueError
from ..core import io
from ..objects.exceptions import TimeoutError, AlreadyExistsError, \
    NotAuthorizedError, NotSupportedError
from ..resources.strings import strings, responses, prompts
from . import commonops

LOG = minimal_logger(__name__)
DEFAULT_ROLE_NAME = 'aws-elasticbeanstalk-ec2-role'
DEFAULT_SERVICE_ROLE_NAME = 'aws-elasticbeanstalk-service-role'


def make_new_env(env_request, branch_default=False, process_app_version=False,
                 nohang=False, interactive=True, timeout=None):
    resolve_roles(env_request, interactive)

    # deploy code
    if not env_request.sample_application and not env_request.version_label:
        io.log_info('Creating new application version using project code')
        env_request.version_label = \
            commonops.create_app_version(env_request.app_name, process=process_app_version)
        if process_app_version is True:
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
            io.log_info('Created default instance profile.')
            role = get_default_role()
            iam.add_role_to_profile(profile, role)
        except AlreadyExistsError:
            pass
    except NotAuthorizedError:
        # Not a root account. Just assume role exists
        io.log_info('No IAM privileges: assuming default '
                    'instance profile exists.')
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


def get_service_role():
    try:
        roles = iam.get_role_names()
        if DEFAULT_SERVICE_ROLE_NAME not in roles:
            return None
    except NotAuthorizedError:
        # No permissions to list roles
        # Assume role exists, we will handle error at a deeper level
        pass

    return DEFAULT_SERVICE_ROLE_NAME


def create_default_service_role():
    """
    Create the default service role
    """
    io.log_info('Creating service role {} with default permissions.'
                .format(DEFAULT_SERVICE_ROLE_NAME))
    trust_document = _get_default_service_trust_document()
    json_policy = _get_default_service_role_policy()
    role_name = DEFAULT_SERVICE_ROLE_NAME
    policy_name = 'awsebcli_aws-elasticbeanstalk-service-role_{}'\
        .format(int(time.time()))
    try:
        iam.create_role_with_policy(role_name, trust_document,
                                    policy_name, json_policy)
    except NotAuthorizedError as e:
        # NO permissions to create or do something
        raise NotAuthorizedError(prompts['create.servicerole.nopermissions']
                                 .format(DEFAULT_SERVICE_ROLE_NAME, e))

    return DEFAULT_SERVICE_ROLE_NAME


def resolve_roles(env_request, interactive):
    """
    Resolves instance-profile and service-role
    :param env_request: environment request
    :param interactive: boolean
    """
    LOG.debug('Resolving roles')

    if env_request.instance_profile is None and \
            env_request.template_name is None:
        # Service supports no profile, however it is not good/recommended
        # Get the eb default profile
        env_request.instance_profile = get_default_profile()


    if (env_request.platform.has_healthd_support() and  # HealthD enabled
            (env_request.service_role is None) and
            (env_request.template_name is None)):
        role = get_service_role()
        if role is None:
            if interactive:
                io.echo()
                io.echo(prompts['create.servicerole.info'])
                input = io.get_input(prompts['create.servicerole.view'],
                                     default='')

                if input.strip('"').lower() == 'view':
                    io.echo(_get_default_service_role_policy())
                    io.get_input(prompts['general.pressenter'])

                role = create_default_service_role()
            else:
                raise NotSupportedError(prompts['create.servicerole.required'])

        env_request.service_role = role


def _get_default_service_trust_document():
    """
    Just a string representing the service role policy.
    Includes newlines for pretty printing :)
    """
    return \
'''{
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "",
        "Effect": "Allow",
        "Principal": {
            "Service": "elasticbeanstalk.amazonaws.com"
        },
        "Action": "sts:AssumeRole",
        "Condition": {
            "StringEquals": {
                "sts:ExternalId": "elasticbeanstalk"
            }
        }
    }]
}'''


def _get_default_service_role_policy():
    """
    Just a string representing the service role policy.
    Includes newlines for pretty printing :)
    """
    return \
'''{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": [
            "elasticloadbalancing:DescribeInstanceHealth",
            "ec2:DescribeInstances",
            "ec2:DescribeInstanceStatus",
            "ec2:GetConsoleOutput",
            "ec2:AssociateAddress",
            "ec2:DescribeAddresses",
            "ec2:DescribeSecurityGroups",
            "sqs:GetQueueAttributes",
            "sqs:GetQueueUrl",
            "autoscaling:DescribeAutoScalingGroups",
            "autoscaling:DescribeAutoScalingInstances",
            "autoscaling:DescribeScalingActivities",
            "autoscaling:DescribeNotificationConfigurations"
        ],
        "Resource": ["*"]
    }]
}'''