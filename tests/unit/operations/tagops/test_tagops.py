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
from os import linesep
import unittest

from ebcli.operations.tagops import tagops
from ebcli.operations.tagops.taglist import TagList


class TestOperationsValidator(unittest.TestCase):
    def setUp(self):
        self.current_list = [
            {
                'Key': 'key1',
                'Value': 'value1'
            }
        ]

    def test_validate_additions__attempt_to_add_preexisting_tag__raises_exception(self):
        taglist = TagList(self.current_list)
        taglist.populate_add_list("key1=value2")

        with self.assertRaises(tagops.InvalidAttemptToModifyTagsError) as context_manager:
            tagops.validate_additions(taglist)

        print(context_manager.exception.message)
        expected_error_message = "Tags with the following keys can't be added because they already exist:{0}{0}  key1{0}".format(linesep)
        self.assertEqual(
            expected_error_message,
            context_manager.exception.message
        )

    def test_validate___attempt_to_add_new_tag__passes_validation(self):
        taglist = TagList(self.current_list)
        taglist.populate_add_list("key2=value2")

        tagops.validate_additions(taglist)

    def test_validate_deletion__attempt_to_delete_non_existent_tag__raises_exception(self):
        taglist = TagList(self.current_list)
        taglist.populate_delete_list("key2")

        with self.assertRaises(tagops.InvalidAttemptToModifyTagsError) as context_manager:
            tagops.validate_deletions(taglist)

        expected_error_message = "Tags with the following keys can't be deleted because they don't exist:{0}{0}  key2{0}".format(linesep)
        self.assertEqual(expected_error_message, context_manager.exception.message)

    def test_validate_deletion__attempt_to_delete_existing_tag__passes_validation(self):
        taglist = TagList(self.current_list)
        taglist.populate_delete_list("key1")

        tagops.validate_deletions(taglist)

    def test_validate_update__attempt_to_update_non_existent_tag__raises_exception(self):
        taglist = TagList(self.current_list)
        taglist.populate_update_list("key2=value2")

        with self.assertRaises(tagops.InvalidAttemptToModifyTagsError) as context_manager:
            tagops.validate_updates(taglist)

        expected_error_message = "Tags with the following keys can't be updated because they don't exist:{0}{0}  key2{0}".format(linesep)
        self.assertEqual(expected_error_message, context_manager.exception.message)

    def test_validate_update__attempt_to_update_existing_tag__passes_validation(self):
        taglist = TagList(self.current_list)
        taglist.populate_update_list("key1=value1")

        tagops.validate_updates(taglist)
