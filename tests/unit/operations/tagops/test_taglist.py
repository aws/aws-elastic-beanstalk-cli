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
from sys import version_info as python_version

import unittest

from ebcli.operations.tagops.taglist import(
    ArgumentSyntaxValidator,
    TagList,
    TagListValidator,
    column_length,
    list_of_keys_of
)


class TestModuleMethods(unittest.TestCase):

    def test_list_of_keys_of(self):
        list_of_tags = [
            {
                'Key': 'key1',
                'Value': 'value',
            },
            {
                'Key': 'key2',
                'Value': 'value',
            },
        ]

        self.assertEqual(['key1', 'key2'], list_of_keys_of(list_of_tags))

    def test_list_of_keys_of__empty_list_of_tags(self):
        list_of_tags = []

        self.assertEqual([], list_of_keys_of(list_of_tags))

    def test_column_length(self):
        list_of_tags = [
            {
                'Key': 'key123',
                'Value': 'value',
            },
            {
                'Key': 'key2',
                'Value': 'value',
            },
        ]

        self.assertEqual(6, column_length(list_of_tags))


class ArgumentSyntaxValidatorTest(unittest.TestCase):
    """
    Negative test cases
    """
    def test_validate_key_value_pair__key_is_invalid(self):
        self.__validate_key_value_pair__with_error_in_key(tag="ke'y1=value1", key="ke'y1")

    def test_validate_key_value_pair__value_is_invalid(self):
        self.__validate_key_value_pair__with_error_in_value(tag="key1=val'ue1", value="val'ue1")

    def test_validate_key_value_pair__key_is_blank__invalid_input(self):
        argument_syntax_validator = ArgumentSyntaxValidator()

        with self.assertRaises(ArgumentSyntaxValidator.InvalidTagKeyError) as context_manager:
            argument_syntax_validator.validate_key_value_pair('=value')

        self.assertEqual(
            'Tag key must not be blank.',
            context_manager.exception.message
        )

    def test_validate_key_value_pair__value_is_blank__invalid_input(self):
        for tag in ['key=', 'key']:
            argument_syntax_validator = ArgumentSyntaxValidator()

            with self.assertRaises(ArgumentSyntaxValidator.InvalidTagValueError) as context_manager:
                argument_syntax_validator.validate_key_value_pair(tag)

            self.assertEqual(
                'Tag value must not be blank.',
                context_manager.exception.message
            )

    def test_validate_key_value_pair__key_is_129_characters_long__invalid_input(self):
        one_twenty_nine_ones = '1' * 129
        argument_syntax_validator = ArgumentSyntaxValidator()

        with self.assertRaises(ArgumentSyntaxValidator.InvalidTagKeyError) as context_manager:
            argument_syntax_validator.validate_key_value_pair('{0}=value'.format(one_twenty_nine_ones))

        self.assertEqual(
            (linesep * 2).join(
                [
                    "Tag with the following key exceed length limit. Tag keys can be up to 128 characters in length.",
                    one_twenty_nine_ones
                ]
            ),
            context_manager.exception.message
        )

    def test_validate_key_value_pair__value_is_257_characters_long__invalid_input(self):
        two_hundred_and_fifty_seven_ones = '1' * 257
        argument_syntax_validator = ArgumentSyntaxValidator()

        with self.assertRaises(ArgumentSyntaxValidator.InvalidTagValueError) as context_manager:
            argument_syntax_validator.validate_key_value_pair('key={0}'.format(two_hundred_and_fifty_seven_ones))

            self.assertEqual(
                (linesep * 2).join(
                    [
                        "Tag with the following value exceed length limit. Tag values can be up to 128 characters in length.",
                        two_hundred_and_fifty_seven_ones
                    ]
                ),
                context_manager.exception.message
            )

    @unittest.skipIf(python_version < (3, 0), 'Python 2.7 does not support non-ASCII characters')
    def test_validate_key_value_pair__unicode_characters(self):
        """
        Python identifies certain Unicode characters as letters, but not others.

        For example, the greek delta symbol is not a Unicode letter, and hence
        will not match `\w` during regex comparisons, whereas the Swedish `a`
        is a letter.

        It is also to be noted that even if Python recognizes a Unicode character
        as a string, it is not necessary that the server (which might be in another
        language) will.

        Note about skipping this test for Python 2.7: Python 2.7 will print non-ASCII
        characters to STDOUT, but not process them in *.py files.
        """
        greek_symbol_delta = b'\xe2\x88\x82'.decode('utf-8')
        swedish_a = b'\xc3\xa5'.decode('utf-8')
        self.__validate_key_value_pair__with_error_in_key(
            tag='{0}=value1'.format(greek_symbol_delta),
            key='{0}'.format(greek_symbol_delta)
        )
        self.__validate_key_value_pair__without_error(
            tag="{0}=value1".format(swedish_a)
        )

    """
    Positive test cases
    """
    def test_validate_key_value_pair__key_is_128_characters_long__invalid_input(self):
        one_twenty_eight_ones = '1' * 128
        self.__validate_key_value_pair__without_error(
            tag='{0}=value1'.format(one_twenty_eight_ones)
        )

    def test_validate_key_value_pair__value_is_256_characters_long(self):
        two_hundred_and_fifty_six_ones = '1' * 256
        self.__validate_key_value_pair__without_error(
            tag='key1={0}'.format(two_hundred_and_fifty_six_ones)
        )

    def test_validate_key_value_pair__value_contains_equal_to_sign(self):
        self.__validate_key_value_pair__without_error(tag='key1=val=ue1')

    def test_validate_key_value_pair__tag_contains_plus_sign(self):
        self.__validate_key_value_pair__without_error(tag='ke+y1=val+ue1')

    def test_validate_key_value_pair__tag_contains_period(self):
        self.__validate_key_value_pair__without_error(tag='ke.y1=val.ue1')

    def test_validate_key_value_pair__tag_contains_colon(self):
        self.__validate_key_value_pair__without_error(tag='ke:y1=val:ue1')

    def test_validate_key_value_pair__tag_contains_forward_slash(self):
        self.__validate_key_value_pair__without_error(tag='ke/y1=val/ue1')

    def test_validate_key_value_pair__tag_contains_hyphen(self):
        self.__validate_key_value_pair__without_error(tag='ke-y1=val-ue1')

    def test_validate_key_value_pair__key_contains_whitespace(self):
        self.__validate_key_value_pair__without_error(tag='k e y 1=val-ue1')

    def test_validate_key_value_pair__value_contains_whitespace(self):
        self.__validate_key_value_pair__without_error(tag='key1=val ue1')

    def test_validate_key_value_pair__tag_contains_whitespace__whitespace_surrounding_equal_to_is_stripped(self):
        self.__validate_key_value_pair__without_error(tag='key1 = value1')

    def test_validate_key_value_pair__tag_contains_leading_whitespace(self):
        self.__validate_key_value_pair__without_error(tag=' key1=value1')

    def test_validate_key_value_pair__tag_contains_trailing_whitespace(self):
        self.__validate_key_value_pair__without_error(tag='key1=value1 ')

    def test_validate_key_value_pair__complicated_but_valid_key_and_value_pair(self):
        self.__validate_key_value_pair__without_error(tag='_k:/@e/-y=v/.a@l+=u:e_')

    def __validate_key_value_pair__without_error(self, tag):
        argument_syntax_validator = ArgumentSyntaxValidator()

        argument_syntax_validator.validate_key_value_pair(tag)

    def __validate_key_value_pair__with_error_in_key(self, tag, key):
        argument_syntax_validator = ArgumentSyntaxValidator()

        with self.assertRaises(ArgumentSyntaxValidator.InvalidTagKeyError) as context_manager:
            argument_syntax_validator.validate_key_value_pair(tag)

        self.assertEqual(
            "Tag key '{0}' has invalid characters. Only letters, numbers, white space, and these characters are allowed: _ . : / + - @.".format(key),
            context_manager.exception.message
        )

    def __validate_key_value_pair__with_error_in_value(self, tag, value):
        argument_syntax_validator = ArgumentSyntaxValidator()

        with self.assertRaises(ArgumentSyntaxValidator.InvalidTagValueError) as context_manager:
            argument_syntax_validator.validate_key_value_pair(tag)

        self.assertEqual(
            "Tag value '{0}' has invalid characters. Only letters, numbers, white space, and these characters are allowed: _ . : / = + - @.".format(value),
            context_manager.exception.message
        )


class TagListValidatorTest(unittest.TestCase):

    def setUp(self):
        self.taglist = TagList([])

    def test_validate_key_for_addition_is_unique__key_already_present_in_add_list__raises_duplicate_key_error(self):
        self.taglist.additions = [{'Key': 'key1', 'Value': 'value1'}]

        with self.assertRaises(TagListValidator.DuplicateKeyError) as context_manager:
            TagListValidator(self.taglist, 'key1').validate_key_for_addition_is_unique()

        self.assertEqual(
            "A tag with the key 'key1' is specified more than once for '--add'. You can add a tag key only once.{0}".format(linesep),
            context_manager.exception.message
        )

    def test_validate_key_for_addition_is_unique__key_is_new(self):
        self.taglist.additions = [{'Key': 'key1', 'Value': 'value1'}]

        TagListValidator(self.taglist, 'key2').validate_key_for_addition_is_unique()

    def test_validate_key_for_deletion_is_unique__key_already_present_in_deletion_list__raises_duplicate_key_error(self):
        self.taglist.deletions = ['key1']

        with self.assertRaises(TagListValidator.DuplicateKeyError) as context_manager:
            TagListValidator(self.taglist, 'key1').validate_key_for_deletion_is_unique()

        self.assertEqual(
            "A tag with the key 'key1' is specified more than once for '--delete'. You can delete a tag key only once.{0}".format(linesep),
            context_manager.exception.message
        )

    def test_validate_key_for_deletion_is_unique__key_is_new(self):
        self.taglist.additions = [{'Key': 'key1', 'Value': 'value1'}]

        TagListValidator(self.taglist, 'key2').validate_key_for_deletion_is_unique()

    def test_validate_key_for_updates_is_unique__key_already_present_in_deletion_list__raises_duplicate_key_error(self):
        self.taglist.deletions = ['key1']

        with self.assertRaises(TagListValidator.DuplicateKeyError) as context_manager:
            TagListValidator(self.taglist, 'key1').validate_key_for_update_is_unique()

        self.assertEqual(
            "A tag with the key 'key1' is specified for both '--delete' and '--update'. You can either delete or update each tag in a single operation.{0}".format(linesep),
            context_manager.exception.message
        )

    def test_validate_key_for_update_is_unique__key_already_present_in_updates_list__raises_duplicate_key_error(self):
        self.taglist.updates = [{'Key': 'key1', 'Value': 'value1'}]

        with self.assertRaises(TagListValidator.DuplicateKeyError) as context_manager:
            TagListValidator(self.taglist, 'key1').validate_key_for_update_is_unique()

        self.assertEqual(
            "A tag with the key 'key1' is specified more than once for '--update'. You can update a tag key only once.{0}".format(linesep),
            context_manager.exception.message
        )

    def test_validate_key_for_update_is_unique__key_is_new(self):
        self.taglist.additions = [{'Key': 'key1', 'Value': 'value1'}]
        self.taglist.deletions = ['key2']
        self.taglist.updates = [{'Key': 'key3', 'Value': 'value1'}]

        TagListValidator(self.taglist, 'key4').validate_key_for_update_is_unique()


class TestAdditionList(unittest.TestCase):

    def setUp(self):
        self.env_name = 'test-4'
        self.current_list = [
            {
                'Key': 'key1',
                'Value': 'value1'
            },
            {
                'Key': 'key2',
                'Value': 'value2'
            }
        ]

    def test_populate_add_list__key_value_pair_is_enclosed_within_single_quotes__legal_string(self):
        expected_add_list = [
            {
                'Key': 'key10',
                'Value': 'value1'
            }
        ]
        taglist = TagList(self.current_list)
        tag_keys_to_create = "'key10=value1'"

        taglist.populate_add_list(tag_keys_to_create)

        self.assertEqual(expected_add_list, taglist.additions)

    def test_populate_add_list__key_value_pair_is_enclosed_within_double_quotes__legal_string(self):
        expected_add_list = [
            {
                'Key': 'key10',
                'Value': 'value1'
            }
        ]
        taglist = TagList(self.current_list)
        tag_keys_to_create = '"key10=value1"'

        taglist.populate_add_list(tag_keys_to_create)

        self.assertEqual(expected_add_list, taglist.additions)

    def test_populate_add_list__multiple_comma_separated_key_value_pairs_are_enclosed_within_double_quotes__legal_string(self):
        expected_add_list = [
            {
                'Key': 'key10',
                'Value': 'value10'
            },
            {
                'Key': 'key11',
                'Value': 'value11'
            }
        ]
        taglist = TagList(self.current_list)
        tag_keys_to_create = '"key10=value10,key11=value11"'

        taglist.populate_add_list(tag_keys_to_create)
        self.assertEqual(expected_add_list, taglist.additions)

    def test_populate_add_list__tag_contains_multiple_equal_to_signs__key_ends_before_first_equal_to(self):
        expected_add_list = [
            {
                'Key': 'key',
                'Value': '10=value1'
            }
        ]
        taglist = TagList(self.current_list)
        tag_keys_to_create = '"key=10=value1"'

        taglist.populate_add_list(tag_keys_to_create)

        self.assertEqual(expected_add_list, taglist.additions)

    def test_populate_add_list__whitespace_around_commas_is_stripped(self):
        expected_add_list = [
            {
                'Key': 'key10',
                'Value': 'value10'
            },
            {
                'Key': 'key11',
                'Value': 'value11'
            }
        ]
        taglist = TagList(self.current_list)
        tag_keys_to_create = '"key10=value10 , key11=value11"'

        taglist.populate_add_list(tag_keys_to_create)
        self.assertEqual(expected_add_list, taglist.additions)

    def test_populate_add_list__whitespace_around_equal_to_separating_key_and_value_is_stripped(self):
        expected_add_list = [
            {
                'Key': 'key10',
                'Value': 'value10'
            },
            {
                'Key': 'key11',
                'Value': 'value11'
            },
            {
                'Key': 'key12',
                'Value': 'value12'
            }
        ]
        taglist = TagList(self.current_list)
        tag_keys_to_create = 'key10= value10,key11 =value11,key12 = value12'

        taglist.populate_add_list(tag_keys_to_create)
        self.assertEqual(expected_add_list, taglist.additions)

    def test_populate_add_list__trailing_and_leading_whitespaces_are_stripped(self):
        expected_add_list = [
            {
                'Key': 'key10',
                'Value': 'value10'
            }
        ]
        taglist = TagList(self.current_list)
        tag_keys_to_create = ' key10=value10 '

        taglist.populate_add_list(tag_keys_to_create)

        self.assertEqual(expected_add_list, taglist.additions)

    def test_populate_add_list__add_one_new_tag__key_does_not_preexist__successfully_adds(self):
        taglist = TagList(self.current_list)

        addition_string = 'myuniquekey=value3'

        taglist.populate_add_list(addition_string)

        expected_additions_list = [
            {
                'Key': 'myuniquekey',
                'Value': 'value3'
            }
        ]

        self.assertEqual(expected_additions_list, taglist.additions)

    def test_populate_add_list__add_multiple_new_tags__keys_dont_preexist__successfully_adds(self):
        taglist = TagList(self.current_list)

        addition_string = ','.join(
            [
                'myuniquekey=value3',
                'myuniquekey2=value3',
                'myuniquekey3=value4'
            ]
        )

        taglist.populate_add_list(addition_string)

        expected_additions_list = [
            {'Key': 'myuniquekey', 'Value': 'value3'},
            {'Key': 'myuniquekey2', 'Value': 'value3'},
            {'Key': 'myuniquekey3', 'Value': 'value4'}
        ]

        self.assertEqual(expected_additions_list, taglist.additions)

    def test_populate_add_list__single_character_keys_and_values_are_permitted(self):
        taglist = TagList(self.current_list)

        addition_string = 'a=b'

        taglist.populate_add_list(addition_string)

        expected_additions_list = [
            {'Key': 'a', 'Value': 'b'}
        ]

        self.assertEqual(expected_additions_list, taglist.additions)


class TestDeletionList(unittest.TestCase):

    def setUp(self):
        self.env_name = 'test-4'
        self.current_list = [
            {
                'Key': 'key1',
                'Value': 'value1'
            },
            {
                'Key': 'key2',
                'Value': 'value2'
            }
        ]

    def test_populate_delete_list__whitespace_around_commas_is_stripped(self):
        expected_delete_list = ['key10', 'key11']

        taglist = TagList(self.current_list)
        tag_keys_to_delete = '"key10 , key11'

        taglist.populate_delete_list(tag_keys_to_delete)
        self.assertEqual(expected_delete_list, taglist.deletions)

    def test_populate_delete_list__trailing_and_leading_whitespaces_are_stripped(self):
        expected_delete_list = ['key10']

        taglist = TagList(self.current_list)
        tag_keys_to_delete = ' key10 '

        taglist.populate_delete_list(tag_keys_to_delete)
        self.assertEqual(expected_delete_list, taglist.deletions)

    def test_populate_delete_list__whitespace_inside_key_is_preserved(self):
        expected_delete_list = ['key 10']

        taglist = TagList(self.current_list)
        tag_keys_to_delete = 'key 10'

        taglist.populate_delete_list(tag_keys_to_delete)
        self.assertEqual(expected_delete_list, taglist.deletions)

    def test_populate_delete_list__successfully_adds_one_key_to_delete_list(self):
        taglist = TagList(self.current_list)

        deletion_string = 'myuniquekey'

        taglist.populate_delete_list(deletion_string)

        self.assertEqual(['myuniquekey'], taglist.deletions)

    def test_populate_delete_list__successfully_adds_multiple_keys_to_delete_list(self):
        taglist = TagList(self.current_list)

        deletion_string = ','.join(
            [
                'myuniquekey',
                'myuniquekey2',
                'myuniquekey3'
            ]
        )

        taglist.populate_delete_list(deletion_string)

        expected_deletions_list = [
            'myuniquekey',
            'myuniquekey2',
            'myuniquekey3'
        ]

        self.assertEqual(expected_deletions_list, taglist.deletions)


class TestUpdateList(unittest.TestCase):

    def setUp(self):
        self.env_name = 'test-4'
        self.current_list = [
            {
                'Key': 'key1',
                'Value': 'value1'
            },
            {
                'Key': 'key2',
                'Value': 'value2'
            }
        ]

    def test_populate_updates_list__multiple_comma_separated_key_value_pairs_are_enclosed_within_single_quotes__legal_string(self):
        expected_update_list = [
            {
                'Key': 'key10',
                'Value': 'value10'
            },
            {
                'Key': 'key11',
                'Value': 'value11'
            }
        ]
        taglist = TagList(self.current_list)
        tag_keys_to_update = "'key10=value10,key11=value11'"

        taglist.populate_update_list(tag_keys_to_update)

        self.assertEqual(expected_update_list, taglist.updates)

    def test_populate_updates_list__multiple_comma_separated_key_value_pairs_are_enclosed_within_double_quotes__legal_string(self):
        expected_update_list = [
            {
                'Key': 'key10',
                'Value': 'value10'
            },
            {
                'Key': 'key11',
                'Value': 'value11'
            }
        ]
        taglist = TagList(self.current_list)
        tag_keys_to_update = '"key10=value10,key11=value11"'

        taglist.populate_update_list(tag_keys_to_update)

        self.assertEqual(expected_update_list, taglist.updates)

    def test_populate_update_list__tag_contains_multiple_equal_to_signs__key_ends_before_first_equal_to(self):
        expected_update_list = [
            {
                'Key': 'key',
                'Value': '10=value1'
            }
        ]
        taglist = TagList(self.current_list)
        tag_keys_to_update = '"key=10=value1"'

        taglist.populate_update_list(tag_keys_to_update)

        self.assertEqual(expected_update_list, taglist.updates)

    def test_populate_update_list__whitespace_around_commas_is_stripped(self):
        expected_update_list = [
            {
                'Key': 'key10',
                'Value': 'value10'
            },
            {
                'Key': 'key11',
                'Value': 'value11'
            }
        ]
        taglist = TagList(self.current_list)
        tag_keys_to_update = '"key10=value10 , key11=value11"'

        taglist.populate_update_list(tag_keys_to_update)

        self.assertEqual(expected_update_list, taglist.updates)

    def test_populate_update_list__whitespace_around_equal_to_separating_key_and_value_is_stripped(self):
        expected_update_list = [
            {
                'Key': 'key10',
                'Value': 'value10'
            },
            {
                'Key': 'key11',
                'Value': 'value11'
            },
            {
                'Key': 'key12',
                'Value': 'value12'
            }
        ]
        taglist = TagList(self.current_list)
        tag_keys_to_update = 'key10= value10,key11 =value11,key12 = value12'

        taglist.populate_update_list(tag_keys_to_update)

        self.assertEqual(expected_update_list, taglist.updates)

    def test_populate_update_list__trailing_and_leading_whitespaces_are_stripped(self):
        expected_update_list = [
            {
                'Key': 'key10',
                'Value': 'value10'
            }
        ]
        taglist = TagList(self.current_list)
        tag_keys_to_update = ' key10=value10 '

        taglist.populate_update_list(tag_keys_to_update)

        self.assertEqual(expected_update_list, taglist.updates)

    def test_populate_update_list__update_one_existing_tag(self):
        taglist = TagList(self.current_list)

        update_string = 'key1=value3'

        taglist.populate_update_list(update_string)

        expected_update_list = [
            {
                'Key': 'key1',
                'Value': 'value3'
            }
        ]

        self.assertEqual(expected_update_list, taglist.updates)

    def test_populate_update_list__update_multiple_existing_tags(self):
        taglist = TagList(self.current_list)

        update_string = ','.join(
            [
                'key1=value3',
                'key2=value3'
            ]
        )

        taglist.populate_update_list(update_string)

        expected_update_list = [
            {'Key': 'key1', 'Value': 'value3'},
            {'Key': 'key2', 'Value': 'value3'}
        ]

        self.assertEqual(expected_update_list, taglist.updates)
