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

import unittest
from ebcli.objects.tier import Tier
from ebcli.objects.exceptions import NotFoundError


class TestNoSourceControl(unittest.TestCase):

    def test_parse_tier_base_web(self):
        expected = Tier('WebServer', 'Standard', '1.0')
        self.assertEqual(Tier.parse_tier('webserver'), expected)

    def test_parse_tier_base_webserver_version1_0(self):
        expected = Tier('WebServer', 'Standard', '1.0')
        self.assertEqual(Tier.parse_tier('webserver-1.0'), expected)

    def test_parse_tier_base_web_version1_0(self):
        expected = Tier('WebServer', 'Standard', '1.0')
        self.assertEqual(Tier.parse_tier('web-1.0'), expected)

    def test_parse_tier_base_worker(self):
        expected = Tier('Worker', 'SQS/HTTP', '')
        self.assertEqual(Tier.parse_tier('worker'), expected)

    def test_parse_tier_base_worker_version1_1(self):
        expected = Tier('Worker', 'SQS/HTTP', '1.1')
        self.assertEqual(Tier.parse_tier('worker-1.1'), expected)

    def test_parse_tier_base_worker_version1_0(self):
        expected = Tier('Worker', 'SQS/HTTP', '1.0')
        self.assertEqual(Tier.parse_tier('worker-1.0'), expected)

    def test_parse_tier_base_worker_full(self):
        expected = Tier('Worker', 'SQS/HTTP', '1.0')
        self.assertEqual(Tier.parse_tier('worker-sqs/http-1.0'), expected)

    def test_parse_tier_base_worker_nonexistant_version(self):
        expected = Tier('Worker', 'SQS/HTTP', '12.24')
        self.assertEqual(Tier.parse_tier('worker-12.24'), expected)

    def test_parse_tier_bad(self):
        self.assertRaises(NotFoundError, Tier.parse_tier, 'foobar')

    def test_parse_tier_bad_with_version(self):
        self.assertRaises(NotFoundError, Tier.parse_tier, 'foobar-2.5')