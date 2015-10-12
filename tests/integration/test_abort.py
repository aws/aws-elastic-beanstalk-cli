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

from .baseinttest import BaseIntegrationTest

from ebcli.core import fileoperations
from ebcli.operations import commonops
from ebcli.resources.strings import prompts
from ebcli.objects.exceptions import NotFoundError

from . import mockservice


class TestAbort(BaseIntegrationTest):

    def setUp(self):
        super(TestAbort, self).setUp()
        # Create all app stuff
        fileoperations.create_config_file('myEBCLItest', 'us-west-2',
                                          'my-stack-stack')
        commonops.set_environment_for_current_branch('my-env')

        mockservice.enqueue('elasticbeanstalk',
                            'AbortEnvironmentUpdate',
                            standard_abort())

    def test_abort_standard(self):
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeEnvironments',
                            describe_env_all_abortable())
        self.run_command('abort')

    def test_abort_multiple(self):
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeEnvironments',
                            describe_env_all_abortable())

        self.run_command('abort')
        self.assertTrue(mockservice.called_with(
            'elasticbeanstalk', 'AbortEnvironmentUpdate',
            {'Action': u'AbortEnvironmentUpdate',
             'EnvironmentName': 'single-env',
             'Version': u'2010-12-01'}))
        self.mock_input.assert_called_with('(default is 1)', 1)  # Test we prompted for env

    def test_abort_single(self):
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeEnvironments',
                            describe_env_one_abortable())

        self.run_command('abort')
        self.assertTrue(mockservice.called_with(
            'elasticbeanstalk', 'AbortEnvironmentUpdate',
            {'Action': u'AbortEnvironmentUpdate',
             'EnvironmentName': 'single-env',
             'Version': u'2010-12-01'}))
        self.mock_input.assert_not_called()  # Test we didn't prompt

    def test_abort_none(self):
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeEnvironments',
                            describe_env_none_abortable())

        try:
            self.run_command('abort')
            self.fail('Should have thrown exception')
        except NotFoundError:
            # Expected
            pass
        self.assertEqual(len(mockservice.get_calls('elasticbeanstalk',
                                                   'AbortEnvironmentUpdate')),
                         0)
        self.mock_input.assert_not_called()  # Test we didn't prompt'


    def test_abort_provided(self):
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeEnvironments',
                            describe_env_all_abortable())

        self.run_command('abort', 'bad-env')
        self.assertTrue(mockservice.called_with(
            'elasticbeanstalk', 'AbortEnvironmentUpdate',
            {'Action': u'AbortEnvironmentUpdate',
             'EnvironmentName': 'bad-env',
             'Version': u'2010-12-01'}))
        self.mock_input.assert_not_called()  # Test we didn't prompt for env


def standard_abort():
    return {'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '3793f8c6-c776-11e4-a3e6-03b427448903'}}


def describe_env_all_abortable():
    default = mockservice.stadard_describe_environments()
    envs = default['Environments']
    for e in envs:
        e['AbortableOperationInProgress'] = True
    return default


def describe_env_one_abortable():
    default = mockservice.stadard_describe_environments()
    envs = default['Environments']
    for e in envs:
        e['AbortableOperationInProgress'] = False
    envs[0]['AbortableOperationInProgress'] = True
    return default


def describe_env_none_abortable():
    default = mockservice.stadard_describe_environments()
    envs = default['Environments']
    for e in envs:
        e['AbortableOperationInProgress'] = False
    return default