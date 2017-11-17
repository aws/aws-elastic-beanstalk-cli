# -*- coding: utf-8 -*-

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

import os
import sys
import shutil
import mock
import unittest

from mock import Mock

from ebcli.core.ebglobals import Constants
from ebcli.operations import platformops
from ebcli.resources.strings import strings, responses, prompts
from ebcli.objects.exceptions import ValidationError
from ebcli.objects.environment import Environment
from ebcli.objects.platform import PlatformVersion

class TestPlatformOperations(unittest.TestCase):

    def setUp(self):
        # set up test directory
        if not os.path.exists('testDir'):
            os.makedirs('testDir')
        os.chdir('testDir')

        self.platform_name = 'test-platform'
        self.platform_version = '1.0.0'
        self.platform_arn = 'arn:aws:elasticbeanstalk:us-east-1:647823116501:platform/{0}/{1}'.format(
                self.platform_name,
                self.platform_version)

    def tearDown(self):
        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            if sys.platform.startswith('win'):
                os.system('rmdir /S /Q testDir')
            else:
                shutil.rmtree('testDir')

    @mock.patch('ebcli.operations.platformops.io')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk')
    @mock.patch('ebcli.operations.platformops.commonops')
    def test_delete_no_environments(self, mock_io, mock_elasticbeanstalk, mock_commonops):
        platformops._version_to_arn = Mock(return_value=self.platform_arn)
        mock_elasticbeanstalk.get_environments.return_value = []
        mock_elasticbeanstalk.delete_platform.return_value = { 'ResponseMetadata': { 'RequestId': 'request-id' } }
        
        platformops.delete_platform_version(self.platform_arn, False)

        mock_elasticbeanstalk.get_environments.assert_called_with()
        mock_elasticbeanstalk.delete_platform.assert_called_with(self.platform_arn)

    @mock.patch('ebcli.operations.platformops.io')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk')
    @mock.patch('ebcli.operations.platformops.commonops')
    def test_delete_with_environments(self, mock_io, mock_elasticbeanstalk, mock_commonops):
        platformops._version_to_arn = Mock(return_value=self.platform_arn)
        environments = [ 
                Environment(name='env1', platform=PlatformVersion(self.platform_arn)),
                Environment(name='no match', platform=PlatformVersion('arn:aws:elasticbeanstalk:us-east-1:647823116501:platform/foo/2.0.0')),
                Environment(name='env2', platform=PlatformVersion(self.platform_arn))
        ]

        mock_elasticbeanstalk.get_environments.return_value = environments
        mock_elasticbeanstalk.delete_platform.return_value = { 'ResponseMetadata': { 'RequestId': 'request-id' } }
        
        self.assertRaises(ValidationError, platformops.delete_platform_version, self.platform_arn, False)

        mock_elasticbeanstalk.get_environments.assert_called_with()


