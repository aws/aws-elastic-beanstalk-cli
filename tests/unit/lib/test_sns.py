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
import mock
import unittest

from ebcli.lib import sns

from .. import mock_responses


class TestSNS(unittest.TestCase):
    @mock.patch('ebcli.lib.sns.aws.make_api_call')
    def test_topics(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.LIST_TOPICS_RESPONSE

        self.assertEqual(
            [
                'arn:aws:sns:us-west-2:123123123123:topic_1',
                'arn:aws:sns:us-west-2:123123123123:topic_2',
                'arn:aws:sns:us-west-2:123123123123:topic_3'
            ],
            sns.topics()
        )

        make_api_call_mock.assert_called_once_with('sns', 'list_topics')
