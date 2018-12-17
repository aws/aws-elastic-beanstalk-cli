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

from ebcli.objects.platform import PlatformVersion


class TestPlatform(unittest.TestCase):
    def test_arn_to_platform__managed_platform_arn(self):
        arn = 'arn:aws:elasticbeanstalk:us-east-1::platform/Name/1.0.0'
        self.assertEqual(
            ('', 'Name', '1.0.0'),
            PlatformVersion.arn_to_platform(arn)
        )

    def test_arn_to_platform__custom_platform_arn(self):
        arn = 'arn:aws:elasticbeanstalk:us-east-1:00000000000:platform/Name/0.0.0'
        self.assertEqual(
            ('00000000000', 'Name', '0.0.0'),
            PlatformVersion.arn_to_platform(arn)
        )

    def test_arn_to_platform__raises_when_argument_is_not_arn_like(self):
        arn = 'node.js'
        with self.assertRaises(PlatformVersion.UnableToParseArnException) as context_manager:
            PlatformVersion.arn_to_platform(arn)

        self.assertEqual(
            "Unable to parse arn 'node.js'",
            context_manager.exception.message
        )

    def test_is_valid_arn__managed_platform_arn(self):
        arn = 'arn:aws:elasticbeanstalk:us-east-1::platform/Name/1.0.0'

        self.assertTrue(PlatformVersion.is_valid_arn(arn))

    def test_is_valid_arn__custom_platform_arn(self):
        arn = 'arn:aws:elasticbeanstalk:us-east-1:00000000000:platform/Name/0.0.0'

        self.assertTrue(PlatformVersion.is_valid_arn(arn))

    def test_is_valid_arn__returns_none_when_arn_is_not_found(self):
        arn = 'node.js'

        self.assertFalse(PlatformVersion.is_valid_arn(arn))

    def test_get_platform_version__managed_platform_arn(self):
        arn = 'arn:aws:elasticbeanstalk:us-east-1::platform/Name/1.0.0'

        self.assertEqual(
            '1.0.0',
            PlatformVersion.get_platform_version(arn)
        )

    def test_get_platform_version__custom_platform_arn(self):
        arn = 'arn:aws:elasticbeanstalk:us-east-1:00000000000:platform/Name/0.0.0'

        self.assertEqual(
            '0.0.0',
            PlatformVersion.get_platform_version(arn)
        )

    def test_get_platform_version__returns_none_when_arn_is_not_found(self):
        arn = 'node.js'

        with self.assertRaises(PlatformVersion.UnableToParseArnException) as context_manager:
            PlatformVersion.get_platform_version(arn)

        self.assertEqual(
            "Unable to parse arn 'node.js'",
            context_manager.exception.message
        )

    def test_get_platform_name__managed_platform_arn(self):
        arn = 'arn:aws:elasticbeanstalk:us-east-1::platform/Name/1.0.0'

        self.assertEqual(
            'Name',
            PlatformVersion.get_platform_name(arn)
        )

    def test_get_platform_name__custom_platform_arn(self):
        arn = 'arn:aws:elasticbeanstalk:us-east-1:00000000000:platform/Name/0.0.0'

        self.assertEqual(
            'Name',
            PlatformVersion.get_platform_name(arn)
        )

    def test_get_platform_name__returns_none_when_arn_is_not_found(self):
        arn = 'node.js'

        with self.assertRaises(PlatformVersion.UnableToParseArnException) as context_manager:
            PlatformVersion.get_platform_name(arn)

        self.assertEqual(
            "Unable to parse arn 'node.js'",
            context_manager.exception.message
        )

    def test_is_eb_managed_platform(self):
        arn = 'arn:aws:elasticbeanstalk:us-west-2::platform/Multi-container Docker running on 64bit Amazon Linux/2.7.5'

        self.assertTrue(PlatformVersion.is_eb_managed_platform_arn(arn))

    def test_has_healthd_support(self):
        platform_arn_1 = 'arn:aws:elasticbeanstalk:ap-southeast-2::platform/PHP 5.4 running on 64bit Amazon Linux/2.6.0'
        platform_arn_2 = 'arn:aws:elasticbeanstalk:ap-southeast-2::platform/PHP 5.4 running on 64bit Amazon Linux/1.4.6'
        platform_arn_3 = 'arn:aws:elasticbeanstalk:ap-southeast-2::platform/IIS 10.0 running on 64bit Windows Server 2016/1.2.0'

        self.assertTrue(PlatformVersion(platform_arn_1).has_healthd_support)
        self.assertFalse(PlatformVersion(platform_arn_2).has_healthd_support)
        self.assertFalse(PlatformVersion(platform_arn_3).has_healthd_support)
