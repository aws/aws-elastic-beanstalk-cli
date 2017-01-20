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
from botocore.credentials import Credentials
import mock
import unittest

from ebcli.objects.solutionstack import SolutionStack
from ebcli.lib import codecommit


class TestCodeCommit(unittest.TestCase):
    solution = SolutionStack('64bit Amazon Linux 2015.03 v2.0.6 running PHP 5.5')
    app_name = 'ebcli-intTest-app'

    def setUp(self):
        self.patcher_io = mock.patch('ebcli.controllers.codesource.io')
        self.patcher_aws = mock.patch('ebcli.lib.codecommit.aws')
        self.mock_io = self.patcher_io.start()
        self.mock_codecommit_aws = self.patcher_aws.start()

    def tearDown(self):
        self.patcher_io.stop()
        self.patcher_aws.stop()


    def test_region_not_supported(self):
        region_supported = codecommit.region_supported('fake_region')
        self.assertFalse(region_supported, "Expected fake region to not be supported, but it was")

    def test_region_supported(self):
        region_supported = codecommit.region_supported('us-east-1')
        self.assertTrue(region_supported, "Expected us-east-1 to be supported but it's not")

    def test_create_signed_url(self):
        # Set static variables
        access_key = "access_key"
        secret_key = "secret_key"
        remote_url = "https://git-codecommit.us-east-1.amazonaws.com/v1/repos/foo-repo"
        region = "us-east-1"
        credentials = Credentials(access_key=access_key, secret_key=secret_key)

        # Setup mocked methods
        self.mock_codecommit_aws.get_credentials.return_value = credentials
        self.mock_codecommit_aws.get_region_name.return_value = region

        with mock.patch('ebcli.lib.codecommit.SigV4Auth') as MockSigV4Class:
            mock_signer = MockSigV4Class.return_value
            mock_signer.string_to_sign.return_value = "{0}::{1}".format(access_key, secret_key)
            mock_signer.signature.return_value = "{0}::{1}".format(access_key, secret_key)

            # Execute and assert method
            expected_url = "https://{0}:{1}@{2}".format(
                access_key, codecommit._sign_codecommit_url(credentials, region, remote_url), remote_url.split("//")[1])

            signed_url = codecommit.create_signed_url(remote_url)

        self.assertEqual(expected_url, signed_url, "Expected '{0}' but got: {1}".format(expected_url, signed_url))
