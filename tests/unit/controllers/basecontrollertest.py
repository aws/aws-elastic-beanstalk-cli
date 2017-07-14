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
import os
import sys
import shutil

from cement.utils import test
from ebcli.core import ebcore
from ebcli.core import fileoperations


class BaseControllerTest(test.CementTestCase):

    def setUp(self):
        super(BaseControllerTest, self).setUp()
        self.reset_backend()
        self.patcher_input = mock.patch('ebcli.core.io.get_input')
        self.patcher_operations = mock.patch('ebcli.controllers.' +
                                             self.module_name + '.'
                                             + self.module_name + 'ops')
        self.patcher_commonops = mock.patch('ebcli.controllers.' +
                                            self.module_name + '.commonops')
        self.patcher_output = mock.patch('ebcli.core.io.echo')

        self.mock_input = self.patcher_input.start()
        self.mock_operations = self.patcher_operations.start()
        self.mock_commonops = self.patcher_commonops.start()
        self.mock_output = self.patcher_output.start()

        # set up test directory
        if not os.path.exists('testDir/.git'):
            os.makedirs('testDir/.git')
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

    def tearDown(self):
        self.patcher_operations.stop()
        self.patcher_input.stop()
        self.patcher_output.stop()
        self.patcher_commonops.stop()

        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            if sys.platform.startswith('win'):
                os.system('rmdir /S /Q testDir')
            else:
                shutil.rmtree('testDir')

    def run_command(self, *args):
        ebcore.EB.Meta.exit_on_close = False
        self.app = ebcore.EB(argv=list(args))
        self.app.setup()
        self.app.run()
        self.app.close()