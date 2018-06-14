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

    @patch('ebcli.core.ebrun.io.echo')
    def test_rescue_EBCLIException__without_verbose_or_debug_flag(
            self,
            echo_mock
    ):
        dummy_ebcli_app = MagicMock()
        dummy_ebcli_app.setup = MagicMock(side_effect=TestEbRun.MyDummyEBCLIException('My Exception Message'))
        ebrun.run_app(dummy_ebcli_app)

        echo_mock.assert_called_with(io.bold(io.color('red', 'ERROR: {}'.format('MyDummyEBCLIException - My Exception Message'))))

    @patch('ebcli.core.ebrun.io.echo')
    @patch('traceback.format_exc')
    def test_rescue_EBCLIException__with_verbose_flag(
            self,
            traceback_mock,
            echo_mock
    ):
        dummy_ebcli_app = MagicMock()
        dummy_ebcli_app.setup = MagicMock(side_effect=TestEbRun.MyDummyEBCLIException('My Exception Message'))
        with patch.object(sys, 'argv', ['--verbose']):
            sys.argv.append('--verbose')

            ebrun.run_app(dummy_ebcli_app)

            echo_mock.side_effect = [
                traceback_mock,
                'INFO: My Exception Message'
            ]

    @patch('ebcli.core.ebrun.io.echo')
    @patch('traceback.format_exc')
    def test_rescue_EBCLIException__with_debug_flag(
            self,
            traceback_mock,
            echo_mock
    ):
        dummy_ebcli_app = MagicMock()
        dummy_ebcli_app.setup = MagicMock(side_effect=TestEbRun.MyDummyEBCLIException('My Exception Message'))
        with patch.object(sys, 'argv', ['--debug']):
            ebrun.run_app(dummy_ebcli_app)

            echo_mock.side_effect = [
                traceback_mock,
                'INFO: My Exception Message'
            ]

    @patch('ebcli.core.ebrun.io.echo')
    def test_rescue_generic_exception(
            self,
            echo_mock
    ):
        dummy_ebcli_app = MagicMock()
        dummy_ebcli_app.setup = MagicMock(side_effect=TestEbRun.MyDummyGenericException('My Exception Message'))

        ebrun.run_app(dummy_ebcli_app)

        echo_mock.assert_called_with(
            io.bold(io.color('red', 'ERROR: {}'.format('MyDummyGenericException - My Exception Message')))
        )

    @patch('ebcli.core.ebrun.io.echo')
    @patch('traceback.format_exc')
    def test_rescue_generic_exception__debug_mode(
            self,
            traceback_mock,
            echo_mock
    ):
        dummy_ebcli_app = MagicMock()
        dummy_ebcli_app.setup = MagicMock(side_effect=TestEbRun.MyDummyGenericException('My Exception Message'))
        with patch.object(sys, 'argv', ['--debug']):
            ebrun.run_app(dummy_ebcli_app)

            echo_mock.side_effect = [
                traceback_mock,
                'INFO: My Exception Message'
            ]

    @patch('ebcli.core.ebrun.io.echo')
    @patch('traceback.format_exc')
    def test_rescue_generic_exception__verbose_mode(
            self,
            traceback_mock,
            echo_mock
    ):
        dummy_ebcli_app = MagicMock()
        dummy_ebcli_app.setup = MagicMock(side_effect=TestEbRun.MyDummyGenericException('My Exception Message'))
        with patch.object(sys, 'argv', ['--verbose']):

            ebrun.run_app(dummy_ebcli_app)

            echo_mock.side_effect = [
                traceback_mock,
                'INFO: My Exception Message'
            ]

    @patch('ebcli.core.ebrun.io.echo')
    def test_rescue_generic_exception__no_args(
            self,
            echo_mock
    ):
        dummy_ebcli_app = MagicMock()
        dummy_ebcli_app.setup = MagicMock(side_effect=TestEbRun.MyDummyGenericException(''))

        ebrun.run_app(dummy_ebcli_app)

        echo_mock.assert_called_with(
            io.bold(
                io.color(
                    'red',
                    'ERROR: MyDummyGenericException'
                )
            )
        )

    @patch('ebcli.core.ebrun.io.echo')
    def test_rescue_AttributeError(
            self,
            echo_mock
    ):
        dummy_ebcli_app = MagicMock()
        dummy_ebcli_app.setup = MagicMock(side_effect=AttributeError('This is my error', 'This is my error as well'))

        ebrun.run_app(dummy_ebcli_app)

        echo_mock.assert_called_with(
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
