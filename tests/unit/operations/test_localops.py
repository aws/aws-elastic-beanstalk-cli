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

from unittest import TestCase

from mock import patch

from ebcli.containers.envvarcollector import EnvvarCollector
from ebcli.operations import localops
from ebcli.operations.localops import LocalState
from tests.unit.containers import dummy

LOCAL_STATE_PATH = '/.elasticbeanstalk/.localstate'


class TestLocalops(TestCase):
    @patch('ebcli.operations.localops.LocalState')
    def test_setenv_delete_and_overwrite(self, LocalState):
        setenv_env = EnvvarCollector({'a': '1', 'b': '2'})
        var_list = ['a=', 'b=3', 'c=55']
        expected_envvars = {'b': '3', 'c': '55'}
        self._test_setenv(setenv_env, var_list, expected_envvars, LocalState)

    @patch('ebcli.operations.localops.LocalState')
    def test_setenv_delete_only(self, LocalState):
        setenv_env = EnvvarCollector({'a': '1', 'b': '2'})
        var_list = ['a=', 'b=']
        expected_envvars = {}
        self._test_setenv(setenv_env, var_list, expected_envvars, LocalState)

    @patch('ebcli.operations.localops.LocalState')
    def test_setenv_overwrite_only(self, LocalState):
        setenv_env = EnvvarCollector({'a': '1', 'b': '2'})
        var_list = ['a=6', 'b=7']
        expected_envvars = {'a': '6', 'b': '7'}
        self._test_setenv(setenv_env, var_list, expected_envvars, LocalState)

    def _test_setenv(self, setenv_env, var_list, expected_envvars, LocalState):
        LocalState.get_envvarcollector.return_value = setenv_env

        localops.setenv(var_list, dummy.PATH_CONFIG)

        call_args = LocalState.save_envvarcollector.call_args[0]
        called_env, called_path = call_args

        self.assertDictEqual(expected_envvars, called_env.map)
        self.assertSetEqual(set(), called_env.to_remove)
        self.assertEqual(dummy.PATH_CONFIG.local_state_path(), called_path)


class TestLocalState(TestCase):
    def setUp(self):
        self.envvarcollector = EnvvarCollector({'a': 'b', 'c': 'd'})
        self.localstate = LocalState(self.envvarcollector)

    def test_constructor(self):
        self.assertEqual(self.envvarcollector, self.localstate.envvarcollector)

    @patch('ebcli.operations.localops.cPickle')
    @patch('ebcli.operations.localops.fileoperations')
    def test_loads(self, fileoperations, cPickle):
        fileoperations.read_from_data_file.return_value = b'foo'
        cPickle.loads.return_value = self.localstate

        self.assertEqual(self.localstate, LocalState.loads(LOCAL_STATE_PATH))
        cPickle.loads.assert_called_once_with(b'foo')

    @patch('ebcli.operations.localops.LocalState.loads')
    def test_get_envvarcollector(self, loads):
        loads.return_value = self.localstate

        self.assertEqual(self.envvarcollector,
                         LocalState.get_envvarcollector(LOCAL_STATE_PATH))
