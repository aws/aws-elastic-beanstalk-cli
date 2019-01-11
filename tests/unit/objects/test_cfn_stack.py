# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

from dateutil import tz
import unittest

from ebcli.objects.cfn_stack import CFNStack

from .. import mock_responses


class TestCFNStack(unittest.TestCase):
    def test_json_to_stack_object(self):
        cfn_stack = CFNStack.json_to_stack_object(mock_responses.DESCRIBE_STACKS_RESPONSE__2['Stacks'][0])

        self.assertEqual(
            'arn:aws:cloudformation:us-west-2:123123123123:stack/sam-cfn-stack-2/13bfae60-b196-11e8-b2de-0ad5109330ec',
            cfn_stack.stack_id
        )
        self.assertEqual('sam-cfn-stack-2', cfn_stack.stack_name)
        self.assertEqual('ROLLBACK_COMPLETE', cfn_stack.stack_status)
        self.assertIsNone(cfn_stack.stack_status_reason)
        self.assertIsNone(cfn_stack.description)
        self.assertEqual(
            datetime.datetime(2018, 9, 6, 5, 31, 16, 951000, tzinfo=tz.tzutc()),
            cfn_stack.creation_time
        )
        self.assertEqual(
            datetime.datetime(2018, 9, 19, 4, 41, 12, 407000, tzinfo=tz.tzutc()),
            cfn_stack.deletion_time
        )
        self.assertEqual(
            datetime.datetime(2018, 9, 19, 4, 41, 8, 956000, tzinfo=tz.tzutc()),
            cfn_stack.last_updated_time
        )
        self.assertIsNone(cfn_stack.change_set_id)
