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
import mock
import unittest

from ebcli.lib import iam

from .. import mock_responses


class TestIAM(unittest.TestCase):
    @mock.patch('ebcli.lib.sns.aws.make_api_call')
    def test_account_id(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.GET_USER_RESPONSE

        self.assertEqual('123123123123', iam.account_id())

        make_api_call_mock.assert_called_once_with('iam', 'get_user')

    @mock.patch('ebcli.lib.iam.get_roles')
    def test_role_exists(self, get_roles_mock):
        # Mock the get_roles function to return a sample list of roles
        mock_roles = [
            {'RoleName': 'aws-elasticbeanstalk-ec2-role'},
            {'RoleName': 'aws-elasticbeanstalk-service-role'}
        ]
        get_roles_mock.return_value = mock_roles

        # Test for a role that exists
        self.assertTrue(iam.role_exists('aws-elasticbeanstalk-ec2-role'))

        # Test for a role that doesn't exist
        self.assertFalse(iam.role_exists('SomeRandomIAMRole'))

        get_roles_mock.assert_called_once()
