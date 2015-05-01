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

from mock import patch, Mock
from unittest import TestCase

from ebcli.operations import localops
from tests.containers import dummy



class TestLocalops(TestCase):
    @patch('ebcli.operations.localops.fileoperations')
    def test_setenv_delete_and_overwrite(self, fileoperations):
        setenv_envvars = {'a': '1', 'b': '2'}
        var_list = ['a=', 'b=3', 'c=55']
        expected_envvars = {'b': '3', 'c': '55'}

        self._test_setenv(setenv_envvars, var_list, expected_envvars, fileoperations)

    @patch('ebcli.operations.localops.fileoperations')
    def test_setenv_delete_only(self, fileoperations):
        setenv_envvars = {'a': '1', 'b': '2'}
        var_list = ['a=', 'b=']
        expected_envvars = {}

        self._test_setenv(setenv_envvars, var_list, expected_envvars, fileoperations)

    @patch('ebcli.operations.localops.fileoperations')
    def test_setenv_overwrite_only(self, fileoperations):
        setenv_envvars = {'a': '1', 'b': '2'}
        var_list = ['a=6', 'b=7']
        expected_envvars = {'a': '6', 'b': '7'}

        self._test_setenv(setenv_envvars, var_list, expected_envvars, fileoperations)


    def _test_setenv(self, setenv_envvars, var_list, expected_envvars, fileoperations):
        fileoperations._get_yaml_dict.return_value = setenv_envvars

        localops.setenv(var_list, dummy.PATH_CONFIG)

        fileoperations.write_json_dict.assert_called_once_with(json_data=expected_envvars,
                                                               fullpath=dummy.SETENV_PATH)
