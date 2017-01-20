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
import unittest

from ebcli.core.ebcore import EB
from ebcli.objects.solutionstack import SolutionStack
from ebcli.resources.strings import strings, prompts


class TestCodeSource(unittest.TestCase):
    solution = SolutionStack('64bit Amazon Linux 2015.03 v2.0.6 running PHP 5.5')
    app_name = 'ebcli-intTest-app'

    def setUp(self):
        self.patcher_io = mock.patch('ebcli.controllers.codesource.io')
        self.mock_io = self.patcher_io.start()

    def tearDown(self):
        self.patcher_io.stop()

    @mock.patch('ebcli.controllers.codesource.gitops')
    def test_case_insensative_input(self, mock_gitops):
        # run cmd
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['codesource',
                            'LoCaL'])
        self.app.setup()
        self.app.run()
        self.app.close()

        self.mock_io.echo.assert_called_once_with(strings['codesource.localmsg'])

    @mock.patch('ebcli.controllers.codesource.gitops')
    @mock.patch('ebcli.controllers.codesource.utils.io')
    def test_interactive_choices_codecommit(self, mock_utils_io, mock_gitops):
        mock_utils_io.prompt.side_effect = [
            '1',  # select CodeCommit
        ]

        # run cmd
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['codesource'])
        self.app.setup()
        self.app.run()
        self.app.close()

        self.mock_io.echo.assert_called_with(prompts['codesource.codesourceprompt'])

        io_calls = [mock.call('2)', 'Local'), mock.call('1)', 'CodeCommit')]
        mock_utils_io.echo.assert_has_calls(io_calls, any_order=True)
