# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

from cement.utils.misc import minimal_logger

from ebcli.core import io
from ebcli.lib import iam
from ebcli.objects.exceptions import NotAuthorizedError, AlreadyExistsError
from ebcli.resources.strings import prompts

import json

LOG = minimal_logger(__name__)

DEFAULT_LAMBDA_ROLE_NAME = 'aws-elasticbeanstalk-lambda-role'
DEFAULT_ROLE_NAME = 'aws-elasticbeanstalk-ec2-role'
DEFAULT_SERVICE_ROLE_NAME = 'aws-elasticbeanstalk-service-role'

# Managed policy arns
# TODO: BJS won't work
DEFAULT_LAMBDA_ROLE_POLICIES = [
    'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
]
DEFAULT_ROLE_POLICIES = [
    'arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier',
    'arn:aws:iam::aws:policy/AWSElasticBeanstalkMulticontainerDocker',
    'arn:aws:iam::aws:policy/AWSElasticBeanstalkWorkerTier'
]
DEFAULT_SERVICE_ROLE_POLICIES = [
    'arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkEnhancedHealth',
    'arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkService'
]

def get_default_lambda_role():
    role = DEFAULT_LAMBDA_ROLE_NAME
    document = '{"Version": "2008-10-17","Statement": [{"Action":' \
               ' "sts:AssumeRole","Principal": {"Service": ' \
               '"lambda.amazonaws.com"},"Effect": "Allow","Sid": ""}]}'
    try:
        iam.create_role_with_policy(role, document, DEFAULT_LAMBDA_ROLE_POLICIES)
    except AlreadyExistsError:
        pass
    except NotAuthorizedError:
        # Not a root account. Just assume role exists
        io.log_info('No IAM privileges: assuming default '
                    'lambda role exists.')
    return role


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
        iam.create_role_with_policy(role, document, DEFAULT_ROLE_POLICIES)
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
    role_name = DEFAULT_SERVICE_ROLE_NAME

    try:
        iam.create_role_with_policy(role_name, trust_document,
                                    DEFAULT_SERVICE_ROLE_POLICIES)
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
                    for policy_arn in DEFAULT_SERVICE_ROLE_POLICIES:
                        document = iam.get_managed_policy_document(policy_arn)
                        io.echo(json.dumps(document, indent=4))
                    io.get_input(prompts['general.pressenter'])

            # Create the service role if it does not exist
            role = create_default_service_role()

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
