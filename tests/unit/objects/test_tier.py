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

import unittest
from ebcli.objects.tier import Tier
from ebcli.objects.exceptions import NotFoundError


class TestTier(unittest.TestCase):

    def test_from_raw_string__webserver(self):
        for customer_input in [
            'WebServer',
            'WebServer/Standard'
        ]:
            tier = Tier.from_raw_string(customer_input)
            self.assertEqual('WebServer', tier.name)
            self.assertEqual('Standard', tier.type)
            self.assertEqual('1.0', tier.version)

    def test_from_raw_string__worker(self):
        for customer_input in [
            'Worker',
            'Worker/SQS/HTTP'
        ]:
            tier = Tier.from_raw_string(customer_input)
            self.assertEqual('Worker', tier.name)
            self.assertEqual('SQS/HTTP', tier.type)
            self.assertEqual('', tier.version)

    def test_from_raw_string__invalid_input(self):
        with self.assertRaises(NotFoundError):
            Tier.from_raw_string('invalid/input')
