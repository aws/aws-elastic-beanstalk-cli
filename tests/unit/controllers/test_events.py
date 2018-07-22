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
import os
import shutil

import mock
from pytest_socket import disable_socket, enable_socket
import unittest

from ebcli.core.ebcore import EB


class TestDeploy(unittest.TestCase):
    def setUp(self):
        disable_socket()
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        os.chdir('testDir')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

        enable_socket()

    @mock.patch('ebcli.controllers.events.EventsController.get_app_name')
    @mock.patch('ebcli.controllers.events.EventsController.get_env_name')
    @mock.patch('ebcli.controllers.events.eventsops.print_events')
    def test_events(
            self,
            print_events_mock,
            get_env_name_mock,
            get_app_name_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['events'])
        app.setup()
        app.run()

        print_events_mock.assert_called_once_with('my-application', 'environment-1', False)

    @mock.patch('ebcli.controllers.events.EventsController.get_app_name')
    @mock.patch('ebcli.controllers.events.EventsController.get_env_name')
    @mock.patch('ebcli.controllers.events.eventsops.print_events')
    def test_events__follow(
            self,
            print_events_mock,
            get_env_name_mock,
            get_app_name_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['events', '-f'])
        app.setup()
        app.run()

        print_events_mock.assert_called_once_with('my-application', 'environment-1', True)
