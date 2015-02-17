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

"""
Apply botocore fixes as monkey patches.
This allows us to upgrade botocore easily. Do not have to do manual merges.
It also maintains flexibility for if/when we no longer bundle botocore.
"""

import botocore.credentials
from botocore.credentials import EnvProvider, SharedCredentialProvider, \
    ConfigProvider, OriginalEC2Provider, BotoProvider, \
    InstanceMetadataProvider, InstanceMetadataFetcher, CredentialResolver


def fix_botocore_credential_loading():

    def create_credential_resolver(session):
        """Create a default credential resolver.

        This creates a pre-configured credential resolver
        that includes the default lookup chain for
        credentials.

        """
        profile_name = session.get_config_variable('profile')
        credential_file = session.get_config_variable('credentials_file')
        config_file = session.get_config_variable('config_file')
        metadata_timeout = session.get_config_variable('metadata_service_timeout')
        num_attempts = session.get_config_variable('metadata_service_num_attempts')
        providers = []
        if profile_name is None:
            providers += [
                EnvProvider(),
                ]
            profile_name = 'default'

        providers += [
            # The new config file has precedence over the legacy
            # config file.
            SharedCredentialProvider(
                creds_filename=credential_file,
                profile_name=profile_name
            ),
            # The new config file has precedence over the legacy
            # config file.
            ConfigProvider(config_filename=config_file, profile_name=profile_name),
            OriginalEC2Provider(),
            BotoProvider(),
            InstanceMetadataProvider(
                iam_role_fetcher=InstanceMetadataFetcher(
                    timeout=metadata_timeout,
                    num_attempts=num_attempts)
            )
        ]
        resolver = CredentialResolver(providers=providers)
        return resolver

    botocore.credentials.create_credential_resolver = \
        create_credential_resolver


def apply_patches():
    fix_botocore_credential_loading()