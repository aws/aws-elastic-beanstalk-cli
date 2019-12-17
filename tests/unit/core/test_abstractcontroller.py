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
import sys
import os
import json

import unittest
import mock

from ebcli.core.ebcore import EB
from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.resources.strings import strings

class TestAbstractBaseControllerFunctional(unittest.TestCase):

    def test_eb_command_subcommand_help(self):
        with self.assertRaises(SystemExit):
            app = EB(argv=['config', 'save', '--help'])
            app.setup()
            app.run()


class TestAbstractBaseController(unittest.TestCase):
    def setUp(self):
        self.test_target = AbstractBaseController()

    @mock.patch('ebcli.core.abstractcontroller.__version__', '0.0.0')
    def test_default__validates_workspace(self):
        self.test_target.validate_workspace = mock.Mock()
        self.test_target.do_command = mock.Mock()
        self.test_target.check_for_cli_update = mock.Mock()
        self.test_target.default()
        
        self.test_target.validate_workspace.assert_called_once_with()

    @mock.patch('ebcli.core.abstractcontroller.__version__', '0.0.0')
    def test_default__runs_command(self):
        self.test_target.validate_workspace = mock.Mock()
        self.test_target.do_command = mock.Mock()
        self.test_target.check_for_cli_update = mock.Mock()
        self.test_target.default()

        self.test_target.do_command.assert_called_once_with()

    @mock.patch('ebcli.core.abstractcontroller.__version__', '0.0.0')
    def test_default__checks_for_cli_update(self):
        self.test_target.validate_workspace = mock.Mock()
        self.test_target.do_command = mock.Mock()
        self.test_target.check_for_cli_update = mock.Mock()
        self.test_target.default()

        self.test_target.check_for_cli_update.assert_called_once_with('0.0.0')

    @mock.patch('ebcli.core.abstractcontroller.io.log_alert')
    @mock.patch('ebcli.core.abstractcontroller.cli_update_exists')
    def test_check_for_cli_update__skips_when_label_not_in_whitelist(
        self,
        cli_update_exists_mock,
        log_alert_mock,
    ):
        input_version = '0.0.0'
        cli_update_exists_mock.return_value = False
        self.test_target.Meta.label = 'tags'
        self.test_target.check_for_cli_update(input_version)

        cli_update_exists_mock.assert_not_called()
        log_alert_mock.assert_not_called()


    @mock.patch('ebcli.core.abstractcontroller.io.log_alert')
    @mock.patch('ebcli.core.abstractcontroller.cli_update_exists')
    def test_check_for_cli_update__checks_pip_update_exists(
        self,
        cli_update_exists_mock,
        log_alert_mock,
    ):
        input_version = '0.0.0'
        cli_update_exists_mock.return_value = False
        self.test_target.Meta.label = 'create'
        self.test_target.check_for_cli_update(input_version)

        cli_update_exists_mock.assert_called_once_with(input_version)
        log_alert_mock.not_called()

    @mock.patch('ebcli.core.abstractcontroller.io.log_alert')
    @mock.patch('ebcli.core.abstractcontroller.cli_update_exists')
    def test_check_for_cli_update__alerts_new_version_available_through_pip(
        self,
        cli_update_exists_mock,
        log_alert_mock,
    ):
        input_version = '0.0.0'
        cli_update_exists_mock.return_value = True
        self.test_target.Meta.label = 'create'
        self.test_target.check_install_script_used = mock.Mock(return_value=False)
        self.test_target.check_for_cli_update(input_version)

        expected_message = ('An update to the EB CLI is available. '
                            'Run "pip install --upgrade awsebcli" to '
                            'get the latest version.')

        cli_update_exists_mock.assert_called_once_with(input_version)
        log_alert_mock.assert_called_once_with(expected_message)

    @mock.patch('ebcli.core.abstractcontroller.io.log_alert')
    @mock.patch('ebcli.core.abstractcontroller.cli_update_exists')
    def test_check_for_cli_update__alerts_new_version_available_through_script(
        self,
        cli_update_exists_mock,
        log_alert_mock,
    ):
        input_version = '0.0.0'
        cli_update_exists_mock.return_value = True
        self.test_target.Meta.label = 'create'
        self.test_target.check_install_script_used = mock.Mock(return_value=True)
        self.test_target.check_for_cli_update(input_version)

        expected_message = ('An update to the EB CLI is available. '
                            'See https://github.com/aws/aws-elastic-beanstalk-cli-setup '
                            'to install the latest version.')

        cli_update_exists_mock.assert_called_once_with(input_version)
        log_alert_mock.assert_called_once_with(expected_message)

    @unittest.skipIf(
        condition=sys.platform.startswith('win'),
        reason='file paths are handled differently on Windows'
    )
    @mock.patch('ebcli.core.abstractcontroller.__file__',
        '/User/username/.ebcli-virtual-env/lib/python3.7/site-packages/ebcli/core/abstractcontroller.py')
    def test_check_install_script_used__returns_true_if_install_script_used_unix(self):
        self.assertTrue(self.test_target.check_install_script_used())

    @unittest.skipIf(
        condition=not(sys.platform.startswith('win')),
        reason='file paths are handled differently on Windows'
    )
    @mock.patch('ebcli.core.abstractcontroller.__file__',
        'C:\\User\\username\\.ebcli-virtual-env\\bin\\eb\\ebcli\\core\\abstractcontroller.py')
    def test_check_install_script_used__returns_true_if_install_script_used_windows(self):
        self.assertTrue(self.test_target.check_install_script_used())

    @unittest.skipIf(
        condition=sys.platform.startswith('win'),
        reason='file paths are handled differently on Windows'
    )
    @mock.patch('ebcli.core.abstractcontroller.__file__',
        '/User/username/virtualenv36/bin/eb/ebcli/core/abstractcontroller.py')
    def test_check_install_script_used__returns_false_if_install_script_not_used_unix(self):
        self.assertFalse(self.test_target.check_install_script_used())

    @unittest.skipIf(
        condition=not(sys.platform.startswith('win')),
        reason='file paths are handled differently on Windows'
    )
    @mock.patch('ebcli.core.abstractcontroller.__file__',
        'C:\\Users\\username\\virtualenv36\\bin\\eb\\ebcli\\core\\abstractcontroller.py')
    def test_check_install_script_used__returns_false_if_install_script_not_used_windows(self):
        self.assertFalse(self.test_target.check_install_script_used())
