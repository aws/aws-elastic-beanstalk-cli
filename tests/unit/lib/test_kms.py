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
from pytest_socket import disable_socket, enable_socket
import unittest

from ebcli.lib import kms

from .. import mock_responses


class TestKMS(unittest.TestCase):
    @mock.patch('ebcli.lib.kms.aws.make_api_call')
    def test_topics(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.LIST_KEYS_RESPONSE

        self.assertEqual(
            [
                '12312312-a783-4f6c-8b8f-502a99545967',
                '12312312-c7d9-457a-a90d-943be31f6144',
                '12312312-ff32-4398-b352-a470ced64752',
                '12312312-36d5-43e6-89ef-c6e82f027d8b',
                '12312312-c660-48ee-b5d1-02d6d1ffc275',
                '12312312-eec7-49a1-a696-335efc664327',
                '12312312-87b5-4fe3-b69f-57494da80071'
            ],
            kms.keys()
        )

        make_api_call_mock.assert_called_once_with('kms', 'list_keys')
