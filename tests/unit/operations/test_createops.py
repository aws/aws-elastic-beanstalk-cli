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

from ebcli.operations import createops
from ebcli.operations.tagops.taglist import TagList
from ebcli.operations.tagops.tagops import TagOps


class TestCreateOps(unittest.TestCase):

    def test_get_and_validate_tags__tags_is_empty(self):
        tags = ''

        self.assertEqual([], createops.get_and_validate_tags(tags))

    def test_get_and_validate_tags__tags_is_empty__add_multiple_new_tags(self):
        taglist = TagList([])

        addition_string = ','.join(
            [
                'key1=value1',
                'key2=value2',
                'key3=value3'
            ]
        )

        expected_additions_list = [
            {'Key': 'key1', 'Value': 'value1'},
            {'Key': 'key2', 'Value': 'value2'},
            {'Key': 'key3', 'Value': 'value3'}
        ]

        self.assertEqual(
            expected_additions_list,
            createops.get_and_validate_tags(addition_string)
        )
