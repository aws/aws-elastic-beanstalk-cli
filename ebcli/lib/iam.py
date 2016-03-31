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

from cement.utils.misc import minimal_logger

from ..lib import aws
from ..objects.exceptions import ServiceError, AlreadyExistsError

LOG = minimal_logger(__name__)


def _make_api_call(operation_name, **operation_options):
    return aws.make_api_call('iam', operation_name, **operation_options)


def get_instance_profiles():
    result = _make_api_call('list_instance_profiles')
    return result['InstanceProfiles']


def get_roles():
    result = _make_api_call('list_roles')
    return result['Roles']


def create_instance_profile(profile_name):
    _make_api_call('create_instance_profile',
                   InstanceProfileName=profile_name)


def get_instance_profile_names():
    profiles = get_instance_profiles()
    lst = []
    for profile in profiles:
        lst.append(profile['InstanceProfileName'])

    return lst


def get_role_names():
    roles = get_roles()
    lst = []
    for role in roles:
        lst.append(role['RoleName'])

    return lst


def add_role_to_profile(profile, role):
    _make_api_call('add_role_to_instance_profile',
                   InstanceProfileName=profile,
                   RoleName=role)


def create_role_with_policy(role_name, trust_document, policy_arns):
    """
    This is a higher level function that creates a role, a policy, and attaches
    everything together
    :param role_name: Name of role to create
    :param trust_document: Policy for trusted entities assuming role
    :param policy: User policy that defines allowable actions
    """
    _create_role(role_name, trust_document)
    for arn in policy_arns:
        attach_role_policy(role_name, arn)


def create_policy(policy_name, policy):
    result = _make_api_call('create_policy',
                            PolicyName=policy_name,
                            PolicyDocument=policy)
    return result['Policy']['Arn']


def attach_role_policy(role_name, policy_arn):
    result = _make_api_call('attach_role_policy',
                            RoleName=role_name,
                            PolicyArn=policy_arn)


def _create_role(role, document):
    _make_api_call('create_role',
                   RoleName=role,
                   AssumeRolePolicyDocument=document)


def upload_server_certificate(cert_name, cert, private_key, chain=None):
    kwargs = dict(
        ServerCertificateName=cert_name,
        CertificateBody=cert,
        PrivateKey=private_key
    )
    if chain:
        kwargs['CertificateChain'] = chain

    result = _make_api_call('upload_server_certificate',
                            **kwargs)
    return result['ServerCertificateMetadata']


def get_managed_policy_document(arn):
    policy = _make_api_call('get_policy',
                            PolicyArn=arn)
    policy_version = policy['Policy']['DefaultVersionId']
    details = _make_api_call('get_policy_version',
                             PolicyArn=arn,
                             VersionId=policy_version)
    return details['PolicyVersion']['Document']