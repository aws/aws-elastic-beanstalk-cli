# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
from pytest_socket import enable_socket, disable_socket
import unittest

from ebcli.operations import cloneops
from ebcli.objects.environment import Environment

from .. import mock_responses


class TestCloneOps(unittest.TestCase):
    def setUp(self):
        disable_socket()

    def tearDown(self):
        enable_socket()

    @mock.patch('ebcli.operations.cloneops.elasticbeanstalk.clone_environment')
    def test_clone_env(
            self,
            clone_environment_mock
    ):
        clone_request_mock = mock.MagicMock()

        environment_mock = Environment.json_to_environment_object(mock_responses.CREATE_ENVIRONMENT_RESPONSE)
        clone_environment_mock.return_value = (environment_mock, 'request-id')

        self.assertEqual(
            (environment_mock, 'request-id'),
            cloneops.clone_env(clone_request_mock)
        )

    @mock.patch('ebcli.operations.cloneops.elasticbeanstalk.clone_environment')
    @mock.patch('ebcli.operations.cloneops.io.prompt_for_cname')
    @mock.patch('ebcli.operations.cloneops.io.echo')
    def test_clone_env__cname_is_unavailable(
            self,
            echo_mock,
            prompt_for_cname_mock,
            clone_environment_mock
    ):
        clone_request_mock = mock.MagicMock()
        prompt_for_cname_mock.return_value = 'my-environment-cname'

        environment_mock = Environment.json_to_environment_object(mock_responses.CREATE_ENVIRONMENT_RESPONSE)
        clone_environment_mock.side_effect = [
            cloneops.InvalidParameterValueError('DNS name (in-use-cname.com) is not available.'),
            (environment_mock, 'request-id')
        ]

        self.assertEqual(
            (environment_mock, 'request-id'),
            cloneops.clone_env(clone_request_mock)
        )

        echo_mock.assert_called_once_with('The CNAME you provided is already in use.\n')

    @mock.patch('ebcli.operations.cloneops.elasticbeanstalk.clone_environment')
    @mock.patch('ebcli.operations.cloneops.io.prompt_for_cname')
    @mock.patch('ebcli.operations.cloneops.io.echo')
    @mock.patch('ebcli.operations.cloneops.elasticbeanstalk.get_environment_names')
    @mock.patch('ebcli.operations.cloneops.utils.get_unique_name')
    @mock.patch('ebcli.operations.cloneops.io.prompt_for_environment_name')
    def test_clone_env__environment_name_is_unavailable(
            self,
            prompt_for_environment_name_mock,
            get_unique_name_mock,
            get_environment_names_mock,
            echo_mock,
            prompt_for_cname_mock,
            clone_environment_mock
    ):
        clone_request_mock = mock.MagicMock()
        clone_request_mock.app_name = 'my-application'
        clone_request_mock.env_name = 'unavailable-environment-name'
        prompt_for_cname_mock.return_value = 'my-environment-cname'
        get_environment_names_mock.return_value = ['environment-1', 'environment-2']
        get_unique_name_mock.return_value = 'environment-3'
        prompt_for_environment_name_mock.return_value = 'my-environment'

        environment_mock = Environment.json_to_environment_object(mock_responses.CREATE_ENVIRONMENT_RESPONSE)
        clone_environment_mock.side_effect = [
            cloneops.InvalidParameterValueError('Environment unavailable-environment-name already exists.'),
            (environment_mock, 'request-id')
        ]

        self.assertEqual(
            (environment_mock, 'request-id'),
            cloneops.clone_env(clone_request_mock)
        )

        echo_mock.assert_called_once_with('An environment with that name already exists.')
        get_environment_names_mock.assert_called_once_with('my-application')
        get_unique_name_mock.assert_called_once_with(
            'unavailable-environment-name',
            ['environment-1', 'environment-2']
        )
        self.assertEqual('my-environment', clone_request_mock.env_name)

    @mock.patch('ebcli.operations.cloneops.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.operations.cloneops.clone_env')
    @mock.patch('ebcli.operations.cloneops.commonops.wait_for_success_events')
    def test_make_cloned_env(
            self,
            wait_for_success_events_mock,
            clone_env_mock,
            get_environment_mock
    ):
        clone_request_mock = mock.MagicMock()
        environment_mock = mock.MagicMock()
        environment_mock.version_label = 'version-label-1'
        result_mock = mock.MagicMock()
        get_environment_mock.return_value = environment_mock
        clone_env_mock.return_value = result_mock, 'request-id'

        cloneops.make_cloned_env(clone_request_mock)

        result_mock.print_env_details.assert_called_once_with(
            cloneops.io.echo,
            cloneops.elasticbeanstalk.get_environments,
            cloneops.elasticbeanstalk.get_environment_resources,
            health=False
        )
        wait_for_success_events_mock.assert_called_once_with(
            'request-id', timeout_in_minutes=None
        )
        self.assertEqual('version-label-1', clone_request_mock.version_label)
