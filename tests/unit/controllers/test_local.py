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

from ebcli.controllers import config
from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
from ebcli.objects.platform import PlatformVersion


class TestLocal(unittest.TestCase):
    platform = PlatformVersion(
        'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5'
    )

    def setUp(self):
        disable_socket()
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        os.chdir('testDir')

        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            self.platform.name
        )

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

        enable_socket()


class TestLocalRun(TestLocal):
    @mock.patch('ebcli.controllers.local.factory.make_container')
    def test_local_run(
            self,
            make_container_mock
    ):
        app = EB(argv=['local', 'run'])
        app.setup()
        app.run()

        make_container_mock.assert_called_once_with(
            None,
            None,
            False
        )

    @mock.patch('ebcli.controllers.local.factory.make_container')
    def test_local_run__with_arguments(
            self,
            make_container_mock
    ):
        app = EB(
            argv=[
                'local', 'run',
                '--envvars', 'ENV_URL="www.localhost.com"',
                '--port', '5000',
                '--allow-insecure-ssl'
            ])

        app.setup()
        app.run()

        make_container_mock.assert_called_once_with(
            'ENV_URL="www.localhost.com"',
            5000,
            True
        )


class TestLocalLogs(TestLocal):
    @mock.patch('ebcli.controllers.local.log.print_logs')
    def test_local_run(
            self,
            print_logs_mock
    ):
        app = EB(argv=['local', 'logs'])
        app.setup()
        app.run()

        print_logs_mock.assert_called_once()


class TestLocalOpen(TestLocal):
    @mock.patch('ebcli.controllers.local.factory.make_container')
    @mock.patch('ebcli.controllers.local.ContainerViewModel.from_container')
    @mock.patch('ebcli.controllers.local.localops.open_webpage')
    def test_local_run(
            self,
            open_webpage_mock,
            from_container_mock,
            make_container_mock
    ):
        container_mock = mock.MagicMock()
        make_container_mock.return_value = container_mock
        container_view_model_mock = mock.MagicMock()
        from_container_mock.return_value = container_view_model_mock

        app = EB(argv=['local', 'open'])
        app.setup()
        app.run()

        open_webpage_mock.assert_called_once_with(container_view_model_mock)


class TestLocalStatus(TestLocal):
    @mock.patch('ebcli.controllers.local.compat.setup')
    @mock.patch('ebcli.controllers.local.factory.make_container')
    @mock.patch('ebcli.controllers.local.ContainerViewModel.from_container')
    @mock.patch('ebcli.controllers.local.localops.print_container_details')
    def test_local_run(
            self,
            print_container_details_mock,
            from_container_mock,
            make_container_mock,
            setup_mock
    ):
        setup_mock.side_effect = None
        container_mock = mock.MagicMock()
        make_container_mock.return_value = container_mock
        container_view_model_mock = mock.MagicMock()
        from_container_mock.return_value = container_view_model_mock

        app = EB(argv=['local', 'status'])
        app.setup()
        app.run()

        print_container_details_mock.assert_called_once_with(container_view_model_mock)


class TestLocalSetEnv(TestLocal):
    @mock.patch('ebcli.controllers.local.localops.setenv')
    def test_local_run(
            self,
            setenv_mock
    ):
        app = EB(argv=['local', 'setenv', 'ENV_URL="www.localhost.com",HOME=/home/ubuntu/'])
        app.setup()
        app.run()

        setenv_mock.assert_called_once_with(
            ['ENV_URL="www.localhost.com",HOME=/home/ubuntu/']
        )


class TestLocalPrintEnv(TestLocal):
    @mock.patch('ebcli.controllers.local.localops.get_and_print_environment_vars')
    def test_local_run(
            self,
            get_and_print_environment_vars_mock
    ):
        app = EB(argv=['local', 'printenv'])
        app.setup()
        app.run()

        get_and_print_environment_vars_mock.assert_called_once()
