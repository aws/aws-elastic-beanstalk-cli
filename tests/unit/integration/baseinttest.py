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

import mock
import sys
import os
import shutil

from cement.utils import test
from botocore.endpoint import Endpoint

from ebcli.core import ebcore, ebrun, fileoperations
from ebcli.lib import aws
from . import mockservice

ebrun.fix_path()


class BaseIntegrationTest(test.CementTestCase):
    app_class = ebcore.EB

    def setUp(self):
        super(BaseIntegrationTest, self).setUp()
        aws._flush()
        aws.set_region('us-east-1')
        self.reset_backend()
        # Set up mock input and output
        self.patcher_input = mock.patch('ebcli.core.io.get_input')
        self.patcher_output = mock.patch('ebcli.core.io.echo')
        self.patcher_warning = mock.patch('ebcli.core.io.log_warning')
        self.mock_input = self.patcher_input.start()
        self.mock_output = self.patcher_output.start()
        self.mock_warning = self.patcher_warning.start()

        # Set up mock endpoints
        endpoint_original = Endpoint
        self.patcher_endpoint = mock.patch('botocore.endpoint.Endpoint')
        self.mock_endpoint = self.patcher_endpoint.start()
        instance = self.mock_endpoint.return_value
        instance.make_request = mockservice.handle_response
        # Mocking our host should force botocore to never call actual service
        # Also required for python3 tests
        instance.host = 'http://someurl.test/something'

        # set up test directory
        if not os.path.exists('testDir/'):
            os.makedirs('testDir/')
        os.chdir('testDir')

        # set up mock elastic beanstalk directory
        if not os.path.exists(fileoperations.beanstalk_directory):
            os.makedirs(fileoperations.beanstalk_directory)

        fileoperations.default_section = 'ebcli_test_default'

        #set up mock home dir
        if not os.path.exists('home'):
            os.makedirs('home')

        # change directory to mock home
        fileoperations.aws_config_folder = 'home' + os.path.sep
        fileoperations.aws_config_location \
            = fileoperations.aws_config_folder + 'config'

    def run_command(self, *args):
        self.app = ebcore.EB(argv=list(args))
        self.app.setup()
        self.app.run()
        self.app.close()

    def tearDown(self):
        # self.patcher_aws.stop()
        self.patcher_input.stop()
        self.patcher_output.stop()
        self.patcher_endpoint.stop()
        self.patcher_warning.stop()

        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            if sys.platform.startswith('win'):
                os.system('rmdir /S /Q testDir')
            else:
                shutil.rmtree('testDir')
        mockservice.reset()
