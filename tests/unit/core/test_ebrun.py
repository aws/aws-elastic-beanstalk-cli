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

from mock import MagicMock, patch
import unittest

from ebcli.core import ebglobals, ebrun, io
from ebcli.objects.exceptions import EBCLIException


class TestEbRun(unittest.TestCase):

    class MyDummyEBCLIException(EBCLIException):
        pass

    class MyDummyGenericException(Exception):
        pass

    def setUp(self):
        # The following variable gets set by some other test. Lack
        # of unit test independence affects this one also
        ebglobals.app = None

        # temporarily overwrite io.echo to allow for safe mocking
        io._echo = io.echo
        io.echo = MagicMock()

        self.dummy_ebcli_app = MagicMock()
        self.dummy_ebcli_app.setup = MagicMock(side_effect=TestEbRun.MyDummyEBCLIException('My Exception Message'))

    def tearDown(self):
        # restore reference of io.echo
        io.echo = io._echo

    def test_rescue_EBCLIEXception__without_verbose_or_debug_flag(self):
        ebrun.run_app(self.dummy_ebcli_app)

        ebrun.run_app(self.dummy_ebcli_app)

        io.echo.assert_called_with(io.bold(io.color('red', 'ERROR: {}'.format('MyDummyEBCLIException - My Exception Message'))))

    @patch('traceback.format_exc')
    def test_rescue_EBCLIEXception__with_verbose_flag(self, traceback_mock):
        with patch.object(sys, 'argv', ['--verbose']):
            sys.argv.append('--verbose')

            ebrun.run_app(self.dummy_ebcli_app)

            io.echo.side_effect = [
                traceback_mock,
                'INFO: My Exception Message'
            ]

    @patch('traceback.format_exc')
    def test_rescue_EBCLIEXception__with_debug_flag(self, traceback_mock):
        with patch.object(sys, 'argv', ['--debug']):
            ebrun.run_app(self.dummy_ebcli_app)

            io.echo.side_effect = [
                traceback_mock,
                'INFO: My Exception Message'
            ]

    def test_rescue_generic_exception(self):
        self.dummy_ebcli_app.setup = MagicMock(side_effect=TestEbRun.MyDummyGenericException('My Exception Message'))

        ebrun.run_app(self.dummy_ebcli_app)

        io.echo.assert_called_with(
            io.bold(io.color('red', 'ERROR: {}'.format('MyDummyGenericException - My Exception Message')))
        )

    @patch('traceback.format_exc')
    def test_rescue_generic_exception__debug_mode(self, traceback_mock):
        with patch.object(sys, 'argv', ['--debug']):
            self.dummy_ebcli_app.setup = MagicMock(side_effect=TestEbRun.MyDummyGenericException('My Exception Message'))

            ebrun.run_app(self.dummy_ebcli_app)

            io.echo.side_effect = [
                traceback_mock,
                'INFO: My Exception Message'
            ]

    @patch('traceback.format_exc')
    def test_rescue_generic_exception__verbose_mode(self, traceback_mock):
        with patch.object(sys, 'argv', ['--verbose']):
            self.dummy_ebcli_app.setup = MagicMock(side_effect=TestEbRun.MyDummyGenericException('My Exception Message'))

            ebrun.run_app(self.dummy_ebcli_app)

            io.echo.side_effect = [
                traceback_mock,
                'INFO: My Exception Message'
            ]

    def test_rescue_generic_exception__no_args(self):
        self.dummy_ebcli_app.setup = MagicMock(side_effect=TestEbRun.MyDummyGenericException(''))

        ebrun.run_app(self.dummy_ebcli_app)

        io.echo.assert_called_with(
            io.bold(
                io.color(
                    'red',
                    'ERROR: MyDummyGenericException'
                )
            )
        )

    def test_rescue_AttributeError(self):
        self.dummy_ebcli_app.setup = MagicMock(side_effect=AttributeError('This is my error', 'This is my error as well'))

        ebrun.run_app(self.dummy_ebcli_app)

        io.echo.assert_called_with(
            io.bold(
                io.color(
                    'red',
                    "ERROR: {error_type} - ('{argument_1}', '{argument_2}')".format(
                        error_type='AttributeError',
                        linesep=os.linesep,
                        argument_1='This is my error',
                        argument_2='This is my error as well'
                    )
                )
            )
        )
