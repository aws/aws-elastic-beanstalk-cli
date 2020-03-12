# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

from ebcli.controllers.platform import status
from ebcli.objects.platform import PlatformVersion


class TestPlatformShowController(unittest.TestCase):

    def setUp(self):
        self.platform_show_controller = status.PlatformShowController()

    @mock.patch('ebcli.controllers.platform.status.platform_version_ops.get_latest_custom_platform_version')
    def test_get_latest_custom_platform(
        self,
        get_latest_custom_platform_version_mock,
    ):
        platform_arn = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        platform_version = PlatformVersion(platform_arn=platform_arn)
        get_latest_custom_platform_version_mock.return_value = platform_version
        expected = (platform_arn, 'custom-platform-1')

        actual = self.platform_show_controller.get_latest_custom_platform(platform_arn)

        get_latest_custom_platform_version_mock.assert_called_once_with(platform_arn)
        self.assertEqual(expected, actual)
