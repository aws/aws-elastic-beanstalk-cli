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
import os
import shutil
import io

import unittest
import mock

from ebcli.operations import spotops


class TestSpotOps(unittest.TestCase):

    @mock.patch('ebcli.operations.spotops.prompt_for_instance_types')
    def test_get_spot_instance_types_from_customer__success(
            self,
            prompt_for_instance_types_mock,
    ):
        enable_spot=True
        interactive=True
        prompt_for_instance_types_mock.return_value='t2.micro, t3.micro'
        self.assertEqual('t2.micro, t3.micro', spotops.get_spot_instance_types_from_customer(interactive, enable_spot))

    @mock.patch('ebcli.operations.spotops.prompt_for_instance_types')
    def test_get_spot_instance_types_from_customer__test_for_prompting(
            self,
            prompt_for_instance_types_mock,
    ):
        prompt_for_instance_types_mock.return_value=''
        self.assertEqual(
            '',
            spotops.get_spot_instance_types_from_customer(
                interactive=True,
                enable_spot=True,
            )
        )
        prompt_for_instance_types_mock.assert_called_once_with()

    @mock.patch('ebcli.operations.spotops.prompt_for_instance_types')
    def test_get_spot_instance_types_from_customer__enable_spot_not_passed(
            self,
            prompt_for_instance_types_mock,
    ):
        enable_spot=None
        interactive=True
        prompt_for_instance_types_mock.assert_not_called()
        self.assertFalse(spotops.get_spot_instance_types_from_customer(interactive, enable_spot))

    @mock.patch('ebcli.operations.spotops.prompt_for_instance_types')
    def test_get_spot_instance_types_from_customer__interactive_is_disabled(
            self,
            prompt_for_instance_types_mock,
    ):
        enable_spot=False
        interactive=False
        prompt_for_instance_types_mock.assert_not_called()
        self.assertFalse(spotops.get_spot_instance_types_from_customer(interactive, enable_spot))
