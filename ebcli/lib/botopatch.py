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


def fix_botocore_to_pass_response_date():
    """
    Patch botocore so that it includes the Date of the response in the meta
    data
    """

    from botocore import parsers
    LOG = parsers.LOG
    pformat = parsers.pformat

    def parse(self, response, shape):
        """Parse the HTTP response given a shape.

        :param response: The HTTP response dictionary.  This is a dictionary
            that represents the HTTP request.  The dictionary must have the
            following keys, ``body``, ``headers``, and ``status_code``.

        :param shape: The model shape describing the expected output.
        :return: Returns a dictionary representing the parsed response
            described by the model.  In addition to the shape described from
            the model, each response will also have a ``ResponseMetadata``
            which contains metadata about the response, which contains at least
            two keys containing ``RequestId`` and ``HTTPStatusCode``.  Some
            responses may populate additional keys, but ``RequestId`` will
            always be present.

        """
        LOG.debug('Response headers:\n%s', pformat(dict(response['headers'])))
        LOG.debug('Response body:\n%s', response['body'])
        if response['status_code'] >= 301:
            parsed = self._do_error_parse(response, shape)
        else:
            parsed = self._do_parse(response, shape)
        # Inject HTTPStatusCode key in the response metadata if the
        # response metadata exists.
        if isinstance(parsed, dict) and 'ResponseMetadata' in parsed:
            parsed['ResponseMetadata']['HTTPStatusCode'] = (
                response['status_code'])
            # Here we inject the date
            parsed['ResponseMetadata']['date'] = (
                response['headers']['date']
            )
        return parsed

    parsers.ResponseParser.parse = parse


def apply_patches():
    fix_botocore_credential_loading()
    fix_botocore_to_pass_response_date()