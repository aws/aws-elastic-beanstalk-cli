# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import os
import shutil
import sys

import mock
import unittest

from ebcli.lib import aws, elasticbeanstalk

from ..test_helper import EnvVarSubstitutor

if sys.platform.startswith('win32'):
    HOME = [
        environ
        for environ in os.environ
        if os.environ[environ] == os.path.expanduser('~')
    ][0]
else:
    HOME = 'HOME'

NOT_FOUND_ERROR_TEMPLATE = '{missing_object} does not exist. '
'It is possible that implementation of related logic and'
'not just the method name has changed in a recent version '
'of `botocore`.'

try:
    from botocore.endpoint import Endpoint
    Endpoint._get_response
except (ModuleNotFoundError, AttributeError):
    raise NotImplementedError(
        NOT_FOUND_ERROR_TEMPLATE.format(missing_object='botocore.endpoint.Endpoint._get_response')
    )

try:
    from botocore.httpsession import URLLib3Session
    URLLib3Session.send
except (ModuleNotFoundError, AttributeError):
    raise NotImplementedError(
        NOT_FOUND_ERROR_TEMPLATE.format(missing_object='botocore.httpsession.URLLib3Session.send')
    )


class CredentialsEnvVarSubstituter(object):
    def __init__(self, access_id, secret_key):
        self.access_id = access_id
        self.secret_key = secret_key

    def __call__(self, func):
        with EnvVarSubstitutor('AWS_ACCESS_KEY_ID', self.access_id):
            with EnvVarSubstitutor('AWS_SECRET_ACCESS_KEY', self.secret_key):
                func()


@unittest.skipIf(
    not not os.environ.get('JENKINS_HOME') and sys.platform.startswith('win32'),
    reason='There are issues being able to find the `~` directory '
           'when run by the Jenkins service on Windows'
)
class TestProfileSelection(unittest.TestCase):
    """
    Class hosts integration tests that interact with botocore to ensure
    the right instance profile will be used. Order is defined in the following
    link:

        https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-configuration.html#eb-cli3-credentials
    """
    def assertCorrectProfileWasUsed(self, _get_response_mock, access_id='access_id'):
        self.assertIn(
            'AWS4-HMAC-SHA256 Credential={}'.format(access_id),
            self._request_header_authorization(_get_response_mock)
        )

    def run(self, result=None):
        aws._flush()
        aws._profile_env_var = 'AWS_EB_PROFILE'
        aws._region_name = 'us-west-2'
        self.root_dir = os.getcwd()
        if os.path.exists('testDir'):
            shutil.rmtree('testDir', ignore_errors=True)
        os.mkdir('testDir')
        os.chdir('testDir')
        try:
            with EnvVarSubstitutor(HOME, os.getcwd()):
                super(TestProfileSelection, self).run(result=result)
        finally:
            aws._flush()
            os.chdir(self.root_dir)
            shutil.rmtree('testDir', ignore_errors=True)

    def _generic_response(self):
        http_object = mock.MagicMock(status_code=200)
        response_object_mock = {
            'PlatformSummaryList': [],
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            }
        }
        return (http_object, response_object_mock), None

    def _generate_profile_with_prefix(
            self,
            credentials_dir=None,
            credentials_file_name='credentials',
            profile='default',
            access_id='access_id',
            secret_key='secret_key'
    ):
        self._generate_profile(
            add_profile_prefix=True,
            credentials_dir=credentials_dir,
            credentials_file_name=credentials_file_name,
            profile=profile,
            access_id=access_id,
            secret_key=secret_key,
        )

    def _generate_profile(
            self,
            add_profile_prefix=False,
            credentials_dir=None,
            credentials_file_name='credentials',
            profile='default',
            access_id='access_id',
            secret_key='secret_key'
    ):
        credentials_dir = credentials_dir or os.path.join(os.environ[HOME], '.aws')
        os.mkdir(credentials_dir)
        credentials_file = os.path.join(credentials_dir, credentials_file_name)
        with open(credentials_file, 'w') as file:
            file.write(
                """[{profile_prefix}{profile}]
aws_access_key_id = {access_id}
aws_secret_access_key = {secret_key}
""".format(
                    profile_prefix='profile ' if add_profile_prefix else '',
                    profile=profile,
                    access_id=access_id,
                    secret_key=secret_key,
                )
            )

    def _request_header_authorization(self, _get_response_mock):
        aws_prepared_request = _get_response_mock.call_args[0][0]
        request_headers = aws_prepared_request.headers
        return str(request_headers['Authorization'])

    @mock.patch('botocore.endpoint.Endpoint._get_response')
    def test_environment_variables_used(
            self,
            _get_response_mock
    ):
        """
            - `--profile` is not passed and is not set in config.yml
            - environment variables `AWS_SECRET_ACCESS_KEY` and `AWS_ACCESS_KEY_ID` are found
        """
        _get_response_mock.return_value = self._generic_response()

        @CredentialsEnvVarSubstituter('access_id', 'secret_key')
        def invoke_api():
            elasticbeanstalk.list_platform_versions()

        self.assertCorrectProfileWasUsed(_get_response_mock)

    @mock.patch('botocore.httpsession.URLLib3Session.send')
    def test_environment_variables_not_found(
            self,
            send_mock
    ):
        """
            - `--profile` is not passed and is not set in config.yml
            - environment variables `AWS_SECRET_ACCESS_KEY` and `AWS_ACCESS_KEY_ID` are not found
            - attempt is made to communicate with IAM to assume role
        """
        @CredentialsEnvVarSubstituter(None, None)
        def invoke_api():
            try:
                elasticbeanstalk.list_platform_versions()
            except Exception:
                pass

        iam_role_verification_request = send_mock.call_args[0][0]
        self.assertIn(
            'latest/meta-data/iam/security-credentials/',
            iam_role_verification_request.url
        )

    def test_aws_eb_profile_environment_variable_found_but_profile_does_not_exist(self):
        """
            - `--profile` is not passed and is not set in config.yml
            - environment variable `AWS_EB_PROFILE` found, but profile does not exist
            - environment variables `AWS_SECRET_ACCESS_KEY` and `AWS_ACCESS_KEY_ID` found but not used
        """
        with EnvVarSubstitutor('AWS_EB_PROFILE', 'some_profile'):
            with self.assertRaises(aws.InvalidProfileError) as context_manager:
                @CredentialsEnvVarSubstituter('access_id', 'secret_key')
                def invoke_api():
                    elasticbeanstalk.list_platform_versions()

            self.assertEqual(
                'The config profile (some_profile) could not be found',
                str(context_manager.exception)
            )

    @mock.patch('botocore.endpoint.Endpoint._get_response')
    def test_aws_eb_profile_environment_variable_found__profile_exists_in_credentials_file(
            self,
            _get_response_mock
    ):
        """
            - `--profile` is not passed and is not set in config.yml
            - environment variable `AWS_EB_PROFILE` found, profile exists in credentials file
            - environment variables `AWS_SECRET_ACCESS_KEY` and `AWS_ACCESS_KEY_ID` found but not used
        """
        self._generate_profile(profile='some_profile')
        with EnvVarSubstitutor('AWS_EB_PROFILE', 'some_profile'):
            _get_response_mock.return_value = self._generic_response()

            @CredentialsEnvVarSubstituter('access_id', 'secret_key')
            def invoke_api():
                elasticbeanstalk.list_platform_versions()

            self.assertCorrectProfileWasUsed(_get_response_mock)

    @mock.patch('botocore.endpoint.Endpoint._get_response')
    def test_aws_eb_profile_environment_variable_found__profile_exists_in_config_file(
            self,
            _get_response_mock
    ):
        """
            - `--profile` is not passed and is not set in config.yml
            - environment variable `AWS_EB_PROFILE` found, profile exists in config file
            - environment variables `AWS_SECRET_ACCESS_KEY` and `AWS_ACCESS_KEY_ID` found but not used
        """
        self._generate_profile_with_prefix(profile='some_profile', credentials_file_name='config')
        with EnvVarSubstitutor('AWS_EB_PROFILE', 'some_profile'):
            _get_response_mock.return_value = self._generic_response()

            @CredentialsEnvVarSubstituter('access_id', 'secret_key')
            def invoke_api():
                elasticbeanstalk.list_platform_versions()

            self.assertCorrectProfileWasUsed(_get_response_mock)

    @mock.patch('botocore.endpoint.Endpoint._get_response')
    def test_default_profile_is_found_in_credentials_file(
            self,
            _get_response_mock
    ):
        """
            - `--profile` is not passed and is not set in config.yml
            - environment variables `AWS_SECRET_ACCESS_KEY` and `AWS_ACCESS_KEY_ID` are not found
            - `default` profile is assumed and found in `$HOME/.aws/credentials` file
        """
        self._generate_profile()
        _get_response_mock.return_value = self._generic_response()

        @CredentialsEnvVarSubstituter(None, None)
        def invoke_api():
            elasticbeanstalk.list_platform_versions()

        self.assertCorrectProfileWasUsed(_get_response_mock)

    @mock.patch('botocore.endpoint.Endpoint._get_response')
    def test_default_profile_is_found_in_config_file__profile_prefix_is_not_added(
            self,
            _get_response_mock
    ):
        """
            - `--profile` is not passed and is not set in config.yml
            - environment variables `AWS_SECRET_ACCESS_KEY` and `AWS_ACCESS_KEY_ID` are not found
            - `default` profile is assumed and found in `$HOME/.aws/config` file; profile is identified as `[default]`
        """
        self._generate_profile(credentials_file_name='config')
        _get_response_mock.return_value = self._generic_response()

        @CredentialsEnvVarSubstituter(None, None)
        def invoke_api():
            elasticbeanstalk.list_platform_versions()

        self.assertCorrectProfileWasUsed(_get_response_mock)

    @mock.patch('botocore.endpoint.Endpoint._get_response')
    def test_default_profile_is_found_in_config_file__profile_prefix_is_added(
            self,
            _get_response_mock
    ):
        """
            - `--profile` is not passed and is not set in config.yml
            - environment variables `AWS_SECRET_ACCESS_KEY` and `AWS_ACCESS_KEY_ID` are not found
            - `default` profile is found in `$HOME/.aws/config` file; profile is identified as `[profile default]`
        """
        self._generate_profile_with_prefix(credentials_file_name='config')
        _get_response_mock.return_value = self._generic_response()

        @CredentialsEnvVarSubstituter(None, None)
        def invoke_api():
            elasticbeanstalk.list_platform_versions()

        self.assertCorrectProfileWasUsed(_get_response_mock)

    def test_profile_is_explicitly_passed_but_is_invalid(self):
        """
            - `--profile` is not passed and is not set in config.yml
            - environment variables `AWS_SECRET_ACCESS_KEY` and `AWS_ACCESS_KEY_ID` are found
            - `some_profile` profile is not found in `$HOME/.aws/credentials`
        """
        aws._profile = 'some_profile'

        with self.assertRaises(aws.InvalidProfileError) as context_manager:
            @CredentialsEnvVarSubstituter('access_id', 'secret_key')
            def invoke_api():
                elasticbeanstalk.list_platform_versions()

        self.assertEqual(
            'The config profile (some_profile) could not be found',
            str(context_manager.exception)
        )

    @mock.patch('botocore.endpoint.Endpoint._get_response')
    def test_profile_is_found_in_credentials_file(
            self,
            _get_response_mock
    ):
        """
            - `--profile` is not passed and is not set in config.yml
            - environment variables `AWS_SECRET_ACCESS_KEY` and `AWS_ACCESS_KEY_ID` are found
            - `some_profile` profile is found in `$HOME/.aws/credentials`
        """
        aws._profile = 'some_profile'
        self._generate_profile(profile='some_profile')
        _get_response_mock.return_value = self._generic_response()

        @CredentialsEnvVarSubstituter('some_other_access_id', 'secret_key')
        def invoke_api():
            elasticbeanstalk.list_platform_versions()

        self.assertCorrectProfileWasUsed(_get_response_mock)

    @mock.patch('botocore.endpoint.Endpoint._get_response')
    def test_profile_is_found_in_config_file(
            self,
            _get_response_mock
    ):
        """
            - `--profile` is not passed and is not set in config.yml
            - environment variables `AWS_SECRET_ACCESS_KEY` and `AWS_ACCESS_KEY_ID` are found
            - `some_profile` profile is found in `$HOME/.aws/config`
        """
        aws._profile = 'some_profile'
        self._generate_profile_with_prefix(credentials_file_name='config', profile='some_profile')

        _get_response_mock.return_value = self._generic_response()

        @CredentialsEnvVarSubstituter('access_id', 'secret_key')
        def invoke_api():
            elasticbeanstalk.list_platform_versions()

        self.assertCorrectProfileWasUsed(_get_response_mock)

    def test_profile_is_found_in_config_file_but_profile_prefix_is_absent(self):
        """
            - `--profile` is not passed and is not set in config.yml
            - environment variables `AWS_SECRET_ACCESS_KEY` and `AWS_ACCESS_KEY_ID` are found
            - `some_profile` profile is found in `$HOME/.aws/config` but profile prefix is absent
        """
        aws._profile = 'some_profile'
        self._generate_profile(credentials_file_name='config', profile='some_profile')

        with self.assertRaises(aws.InvalidProfileError) as context_manager:
            @CredentialsEnvVarSubstituter('access_id', 'secret_key')
            def invoke_api():
                elasticbeanstalk.list_platform_versions()

        self.assertEqual(
            'The config profile (some_profile) could not be found',
            str(context_manager.exception)
        )
