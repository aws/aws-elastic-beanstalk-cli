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
import mock
from pytest_socket import  disable_socket, enable_socket
import unittest

from ebcli.lib import cloudformation

from .. import mock_responses


class TestCloudFormation(unittest.TestCase):
    def setUp(self):
        disable_socket()

    def tearDown(self):
        enable_socket()

    @mock.patch('ebcli.lib.cloudformation.aws.make_api_call')
    def test_wait_until_stack_exists__stack_does_not_exist(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_STACKS_RESPONSE

        with self.assertRaises(cloudformation.CFNTemplateNotFound) as exception:
            cloudformation.wait_until_stack_exists('non_existent_stack', timeout=0)

        self.assertEqual(
            exception.exception.message,
            "Could not find CFN stack, 'non_existent_stack'."
        )

    @mock.patch('ebcli.lib.cloudformation.aws.make_api_call')
    def test_wait_until_stack_exists__stack_exists(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_STACKS_RESPONSE

        cloudformation.wait_until_stack_exists('stack_name')

    @mock.patch('ebcli.lib.cloudformation.aws.make_api_call')
    def test_get_template(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.GET_TEMPLATE_RESPONSE

        self.assertEqual(
            mock_responses.GET_TEMPLATE_RESPONSE,
            cloudformation.get_template('mystackname')
        )
