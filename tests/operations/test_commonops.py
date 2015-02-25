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

from ebcli.operations import commonops


class TestOperations(unittest.TestCase):

    def test_is_success_string(self):
        self.assertTrue(commonops._is_success_string('Environment health has been set to GREEN'))
        self.assertTrue(commonops._is_success_string('Successfully launched environment: my-env'))
        self.assertTrue(commonops._is_success_string('Pulled logs for environment instances.'))
        self.assertTrue(commonops._is_success_string('terminateEnvironment completed successfully.'))
