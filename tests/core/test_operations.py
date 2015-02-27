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

from ebcli.core import operations


class TestOperations(unittest.TestCase):

    def test_is_success_string(self):
        self.assertTrue('Environment health has been set to GREEN')
        self.assertTrue('Successfully launched environment: my-env')
        self.assertTrue('Pulled logs for environment instances')
        self.assertTrue('terminateEnvironment completed successfully')

    @mock.patch('ebcli.core.operations.io')
    def test_get_boolean_response_bad(self, mock_io):
        # populate with all bad responses
        # Last response must be valid in order to terminate loop
        response_list = ['a', '1', 'Ys', 'x', '', 'nah', '?', 'y']
        mock_io.prompt.side_effect = response_list
        result = operations.get_boolean_response()

        #test
        self.assertTrue(result)
        self.assertEqual(mock_io.prompt.call_count, len(response_list))

    @mock.patch('ebcli.core.operations.io')
    def test_get_boolean_response_true(self, mock_io):
        mock_io.prompt.side_effect = ['y', 'Y', 'YES', 'yes', 'Yes']
        result1 = operations.get_boolean_response()  # test with y
        result2 = operations.get_boolean_response()  # test with Y
        result3 = operations.get_boolean_response()  # test with YES
        result4 = operations.get_boolean_response()  # test with yes
        result5 = operations.get_boolean_response()  # test with Yes
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertTrue(result3)
        self.assertTrue(result4)
        self.assertTrue(result5)

    @mock.patch('ebcli.core.operations.io')
    def test_get_boolean_response_false(self, mock_io):
        mock_io.prompt.side_effect = ['n', 'N', 'NO', 'no', 'No']
        result1 = operations.get_boolean_response()  # test with n
        result2 = operations.get_boolean_response()  # test with N
        result3 = operations.get_boolean_response()  # test with NO
        result4 = operations.get_boolean_response()  # test with no
        result5 = operations.get_boolean_response()  # test with No
        self.assertFalse(result1)
        self.assertFalse(result2)
        self.assertFalse(result3)
        self.assertFalse(result4)
        self.assertFalse(result5)