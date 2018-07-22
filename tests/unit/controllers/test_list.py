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

import unittest
from pytest_socket import disable_socket, enable_socket
import mock

from ebcli.core.ebcore import EB


class TestListController(unittest.TestCase):
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

    @mock.patch('ebcli.controllers.list.ListController.get_app_name')
    @mock.patch('ebcli.controllers.list.listops.list_env_names')
    def test_list(
            self,
            list_env_names_mock,
            get_app_name_mock
    ):
        get_app_name_mock.return_value = 'my-application'

        app = EB(argv=['list'])
        app.setup()
        app.run()

        list_env_names_mock.assert_called_with('my-application', False, False)

    @mock.patch('ebcli.controllers.list.ListController.get_app_name')
    @mock.patch('ebcli.controllers.list.listops.list_env_names')
    def test_list__verbose(
            self,
            list_env_names_mock,
            get_app_name_mock
    ):
        get_app_name_mock.return_value = 'my-application'

        app = EB(argv=['list', '--verbose'])
        app.setup()
        app.run()

        list_env_names_mock.assert_called_with('my-application', True, False)

    @mock.patch('ebcli.controllers.list.ListController.get_app_name')
    @mock.patch('ebcli.controllers.list.listops.list_env_names')
    def test_list__all(
            self,
            list_env_names_mock,
            get_app_name_mock
    ):
        get_app_name_mock.return_value = 'my-application'

        app = EB(argv=['list', '--all'])
        app.setup()
        app.run()

        list_env_names_mock.assert_called_with(None, False, True)

    @mock.patch('ebcli.controllers.list.ListController.get_app_name')
    @mock.patch('ebcli.controllers.list.listops.list_env_names')
    def test_list__all__verbose(
            self,
            list_env_names_mock,
            get_app_name_mock
    ):
        get_app_name_mock.return_value = 'my-application'

        app = EB(argv=['list', '--all', '--verbose'])
        app.setup()
        app.run()

        list_env_names_mock.assert_called_with(None, True, True)
