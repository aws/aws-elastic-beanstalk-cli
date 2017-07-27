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
import datetime

from unittest import TestCase

from ebcli.display.table import Table


class TestDisplay(TestCase):

    def test_ascii_string__successfully_wraps_utf8_string(self):
        original_utf8_string = u'The m\u0192\u2202\u0153\u2211\u0153\u2211\xae\xae\xae'
        wrapped_ascii_string = Table('my_table').ascii_string(original_utf8_string)

        self.assertEqual(original_utf8_string, wrapped_ascii_string)
        self.assertEqual(14, len(wrapped_ascii_string))

    def test_ascii_string__successfully_wraps_ascii_string(self):
        original_ascii_string = 'Hello, world!'
        wrapped_ascii_string = Table('my_table').ascii_string(original_ascii_string)

        self.assertEqual('Hello, world!', wrapped_ascii_string)
        self.assertEqual(13, len(wrapped_ascii_string))

    def test_ascii_string__successfully_wraps_number(self):
        number = 100
        wrapped_number = Table('my_table').ascii_string(number)

        self.assertEqual('100', wrapped_number)
        self.assertEqual(3, len(wrapped_number))

    def test_ascii_string__successfully_wraps_datetime(self):
        expected_datetime = datetime.datetime(2007, 12, 6, 16, 29, 43, 79043)
        wrapped_date_time = Table('my_table').ascii_string(expected_datetime)

        self.assertEqual('2007-12-06 16:29:43.079043', wrapped_date_time)
        self.assertEqual(26, len(wrapped_date_time))
