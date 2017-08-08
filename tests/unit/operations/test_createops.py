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

from ebcli.objects.exceptions import InvalidOptionsError
from ebcli.operations import createops

class TestCreateOps(unittest.TestCase):

    def test_get_and_validate_tags__tags_is_empty(self):
        tags = ''

        self.assertEqual([], createops.get_and_validate_tags(tags))

    def test_get_and_validate_tags__more_than_47_tags_provided__raises_invalid_options_error(self):
        tags_strings = []
        for i in range(0, 48):
            tags_strings.append('key{0}=value{0}'.format(i))

        tags = ','.join(tags_strings)

        with self.assertRaises(InvalidOptionsError) as context_manager:
            createops.get_and_validate_tags(tags)

        print(context_manager.exception.message)
        self.assertEqual(
            'Elastic Beanstalk supports a maximum of 50 tags.',
            context_manager.exception.message
        )

    def test_get_and_validate_tags__47_tags_provided__valid(self):
        tags_strings = []
        expected_tags = []

        for i in range(0, 46):
            tags_strings.append('key{0}=value{0}'.format(i))
            expected_tags.append({
                'Key': 'key{0}'.format(i),
                'Value': 'value{0}'.format(i)
            })

        tags = ','.join(tags_strings)

        self.assertEqual(expected_tags, createops.get_and_validate_tags(tags))
