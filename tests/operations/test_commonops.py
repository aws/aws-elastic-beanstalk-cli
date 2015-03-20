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

import os
import shutil
import mock
import unittest

from mock import Mock

from ebcli.core import fileoperations
from ebcli.operations import commonops

class TestCommonOperations(unittest.TestCase):
    def setUp(self):
        # set up test directory
        if not os.path.exists('testDir'):
            os.makedirs('testDir')
        os.chdir('testDir')

        # set up mock elastic beanstalk directory
        if not os.path.exists(fileoperations.beanstalk_directory):
            os.makedirs(fileoperations.beanstalk_directory)

        #set up mock home dir
        if not os.path.exists('home'):
            os.makedirs('home')

        # change directory to mock home
        fileoperations.aws_config_folder = 'home' + os.path.sep
        fileoperations.aws_config_location \
            = fileoperations.aws_config_folder + 'config'

        # Create local
        fileoperations.create_config_file('ebcli-test', 'us-east-1',
                                          'my-solution-stack')

    def tearDown(self):
        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            shutil.rmtree('testDir')

    def test_is_success_string(self):
        self.assertTrue(commonops._is_success_string('Environment health has been set to GREEN'))
        self.assertTrue(commonops._is_success_string('Successfully launched environment: my-env'))
        self.assertTrue(commonops._is_success_string('Pulled logs for environment instances.'))
        self.assertTrue(commonops._is_success_string('terminateEnvironment completed successfully.'))

    @mock.patch('ebcli.operations.commonops.SourceControl')
    def test_return_global_default_if_no_branch_default(self, mock):
        sc_mock = Mock()
        sc_mock.get_current_branch.return_value = 'none'
        mock.get_source_control.return_value = sc_mock

        result = commonops.get_config_setting_from_branch_or_default('default_region')
        assert sc_mock.get_current_branch.called, 'Should have been called'
        self.assertEqual(result, 'us-east-1')

        fileoperations.write_config_setting('global', 'default_region', 'brazil')
        fileoperations.write_config_setting('global', 'profile', 'monica')
        fileoperations.write_config_setting('global', 'moop', 'meep')
        fileoperations.write_config_setting('branch-defaults', 'my-branch', {'profile': 'chandler',
            'environment': 'my-env', 'boop': 'beep'})

        result = commonops.get_current_branch_environment()
        self.assertEqual(result, None)

        #get defualt profile name
        result = commonops.get_default_profile()
        self.assertEqual(result, 'monica')

        result = commonops.get_config_setting_from_branch_or_default('moop')
        self.assertEqual(result, 'meep')


    @mock.patch('ebcli.operations.commonops.SourceControl')
    def test_return_branch_default_if_set(self, mock):
        sc_mock = Mock()
        sc_mock.get_current_branch.return_value = 'my-branch'
        mock.get_source_control.return_value = sc_mock

        fileoperations.write_config_setting('global', 'default_region', 'brazil')
        fileoperations.write_config_setting('global', 'profile', 'monica')
        fileoperations.write_config_setting('global', 'moop', 'meep')
        fileoperations.write_config_setting('branch-defaults', 'my-branch', {'profile': 'chandler',
            'environment': 'my-env', 'boop': 'beep'})

        #get defualt region name
        result = commonops.get_default_region()
        self.assertEqual(result, 'brazil')

        #get branch-specific default environment name
        result = commonops.get_current_branch_environment()
        self.assertEqual(result, 'my-env')

        #get branch-specific default profile name
        result = commonops.get_default_profile()
        self.assertEqual(result, 'chandler')

        #get branch-specific generic default
        result = commonops.get_config_setting_from_branch_or_default('boop')
        self.assertEqual(result, 'beep')

