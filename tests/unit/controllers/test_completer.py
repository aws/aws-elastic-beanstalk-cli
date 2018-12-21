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
import shutil

import mock
from pytest_socket import disable_socket, enable_socket
import unittest

from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
from ebcli.objects.solutionstack import SolutionStack


class TestCompleter(unittest.TestCase):
    solution = SolutionStack('64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5')
    app_name = 'ebcli-intTest-app'

    def setUp(self):
        disable_socket()
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        os.chdir('testDir')

        fileoperations.create_config_file(
            self.app_name,
            'us-west-2',
            self.solution.name
        )

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

        enable_socket()

    @mock.patch('ebcli.core.io.echo')
    def test_base_commands(
            self,
            echo_mock
    ):
        self.app = EB(argv=['completer', '--cmplt', ' '])
        self.app.setup()
        self.app.run()

        expected = {
            'logs',
            'terminate',
            'abort',
            'open',
            'use',
            'scale',
            'console',
            'create',
            'platform',
            'init',
            'setenv',
            'swap',
            'events',
            'status',
            'labs',
            'upgrade',
            'ssh',
            'config',
            'list',
            'printenv',
            'local',
            'health',
            'tags'
            }

        self.assertEqual(expected, set(echo_mock.call_args[0]))
