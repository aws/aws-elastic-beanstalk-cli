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
import mock
from packaging import version as pkg_version
from datetime import datetime
from dateutil import tz

from ebcli.objects.platform import PlatformVersion, PlatformBranch


class TestPlatformVersion(unittest.TestCase):

    platform_version_description = {
        "CustomAmiList": [
            {"ImageId": "", "VirtualizationType": "pv"},
            {"ImageId": "ami-090bd2f2f88b0a815", "VirtualizationType": "hvm"}
        ],
        "DateCreated": datetime(2018, 7, 19, 21, 50, 21, 623000, tzinfo=tz.tzutc()),
        "DateUpdated": datetime(2018, 7, 19, 21, 50, 21, 623000, tzinfo=tz.tzutc()),
        "Description": "64bit Amazon Linux running PHP",
        "Frameworks": [],
        "Maintainer": "aws-elasticbeanstalk-platforms@amazon.com",
        "OperatingSystemName": "Amazon Linux",
        "OperatingSystemVersion": "2018.03",
        "PlatformArn": "arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/2.9.2",
        "PlatformBranchLifecycleState": "Deprecated",
        "PlatformBranchName": "PHP 7.1 running on 64bit Amazon Linux",
        "PlatformCategory": "PHP",
        "PlatformLifecycleState": "Recommended",
        "PlatformName": "PHP 7.1 running on 64bit Amazon Linux",
        "PlatformOwner": "AWSElasticBeanstalk",
        "PlatformStatus": "Ready",
        "PlatformVersion": "2.9.2",
        "ProgrammingLanguages": [
            {"Name": "PHP", "Version": "7.1.33"}
        ],
        "SolutionStackName": "64bit Amazon Linux 2018.03 v2.9.2 running PHP 7.1",
        "SupportedAddonList": [
            "Log/S3",
            "Monitoring/Healthd", "WorkerDaemon/SQSD"
        ],
        "SupportedTierList": ["WebServer/Standard", "Worker/SQS/HTTP"],
    }

    platform_version_summary = {
        "OperatingSystemName": "Amazon Linux",
        "OperatingSystemVersion": "2018.03",
        "PlatformArn": "arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/2.9.2",
        "PlatformBranchLifecycleState": "Deprecated",
        "PlatformBranchName": "PHP 7.1 running on 64bit Amazon Linux",
        "PlatformCategory": "PHP",
        "PlatformLifecycleState": "Recommended",
        "PlatformOwner": "AWSElasticBeanstalk",
        "PlatformStatus": "Ready",
        "PlatformVersion": "2.9.2",
        "SupportedAddonList": ["Log/S3", "Monitoring/Healthd", "WorkerDaemon/SQSD"],
        "SupportedTierList": ["WebServer/Standard", "Worker/SQS/HTTP"],
    }

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

    def test_get_region_from_platform_arn__valid_eb_managed_arn(self):
        arn = 'arn:aws:elasticbeanstalk:us-west-2::platform/Multi-container Docker running on 64bit Amazon Linux/2.7.5'

        self.assertEqual(
            'us-west-2',
            PlatformVersion.get_region_from_platform_arn(arn)
        )

    def test_get_region_from_platform_arn__custom_platform(self):
        custom_platform = 'arn:aws:elasticbeanstalk:us-east-1:00000000000:platform/Name/0.0.0'

        self.assertIsNone(PlatformVersion.get_region_from_platform_arn(custom_platform))

    def test_get_region_from_platform_arn__valid_solution_stack(self):
        solution_stack = 'Multi-container Docker running on 64bit Amazon Linux/2.7.5'

        self.assertIsNone(PlatformVersion.get_region_from_platform_arn(solution_stack))

    def test_get_region_from_platform_arn__solution_stack_shorthand(self):
        solution_stack_shorthand = 'test-dev'

        self.assertIsNone(PlatformVersion.get_region_from_platform_arn(solution_stack_shorthand))

    def test_get_region_from_platform_arn__language_name(self):
        language_name = 'node.js'

        self.assertIsNone(PlatformVersion.get_region_from_platform_arn(language_name))

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

    def test_from_platform_version_description(self):
        platform_version_description = self.platform_version_description

        result = PlatformVersion.from_platform_version_description(
            platform_version_description)

        self.assertEqual(platform_version_description['CustomAmiList'], result.custom_ami_list)
        self.assertEqual(platform_version_description['DateCreated'], result.date_created)
        self.assertEqual(platform_version_description['DateUpdated'], result.date_updated)
        self.assertEqual(platform_version_description['Maintainer'], result.maintainer)
        self.assertEqual(platform_version_description['OperatingSystemName'], result.operating_system_name)
        self.assertEqual(
            platform_version_description['OperatingSystemVersion'], result.operating_system_version)
        self.assertEqual(platform_version_description['PlatformArn'], result.platform_arn)
        self.assertEqual(
            platform_version_description['PlatformBranchLifecycleState'], result.platform_branch_lifecycle_state)
        self.assertEqual(platform_version_description['PlatformBranchName'], result.platform_branch_name)
        self.assertEqual(platform_version_description['PlatformCategory'], result.platform_category)
        self.assertEqual(
            platform_version_description['PlatformLifecycleState'], result.platform_lifecycle_state)
        self.assertEqual(platform_version_description['PlatformName'], result.platform_name)
        self.assertEqual(platform_version_description['PlatformOwner'], result.platform_owner)
        self.assertEqual(platform_version_description['PlatformStatus'], result.platform_status)
        self.assertEqual(platform_version_description['PlatformVersion'], result.platform_version)
        self.assertEqual(platform_version_description['SolutionStackName'], result.solution_stack_name)
        self.assertEqual(platform_version_description['SupportedAddonList'], result.supported_addon_list)
        self.assertEqual(platform_version_description['SupportedTierList'], result.supported_tier_list)

    def test_from_platform_version_summary(self):
        platform_version_summary = self.platform_version_summary

        result = PlatformVersion.from_platform_version_summary(
            platform_version_summary)

        self.assertEqual(platform_version_summary['OperatingSystemName'], result.operating_system_name)
        self.assertEqual(
            platform_version_summary['OperatingSystemVersion'], result.operating_system_version)
        self.assertEqual(platform_version_summary['PlatformArn'], result.platform_arn)
        self.assertEqual(
            platform_version_summary['PlatformBranchLifecycleState'], result.platform_branch_lifecycle_state)
        self.assertEqual(platform_version_summary['PlatformBranchName'], result.platform_branch_name)
        self.assertEqual(platform_version_summary['PlatformCategory'], result.platform_category)
        self.assertEqual(
            platform_version_summary['PlatformLifecycleState'], result.platform_lifecycle_state)
        self.assertEqual(platform_version_summary['PlatformOwner'], result.platform_owner)
        self.assertEqual(platform_version_summary['PlatformStatus'], result.platform_status)
        self.assertEqual(platform_version_summary['PlatformVersion'], result.platform_version)
        self.assertEqual(platform_version_summary['SupportedAddonList'], result.supported_addon_list)
        self.assertEqual(platform_version_summary['SupportedTierList'], result.supported_tier_list)

    def test_hydrate(self):
        platform_version_description = self.platform_version_description
        platform_arn = platform_version_description['PlatformArn']
        describe_platform_version = mock.Mock(
            return_value=platform_version_description)

        platform_version = PlatformVersion(platform_arn)
        platform_version.hydrate(describe_platform_version)

        self.assertEqual(platform_version_description['CustomAmiList'], platform_version.custom_ami_list)
        self.assertEqual(platform_version_description['DateCreated'], platform_version.date_created)
        self.assertEqual(platform_version_description['DateUpdated'], platform_version.date_updated)
        self.assertEqual(platform_version_description['Maintainer'], platform_version.maintainer)
        self.assertEqual(
            platform_version_description['OperatingSystemName'], platform_version.operating_system_name)
        self.assertEqual(
            platform_version_description['OperatingSystemVersion'], platform_version.operating_system_version)
        self.assertEqual(platform_version_description['PlatformArn'], platform_version.platform_arn)
        self.assertEqual(
            platform_version_description['PlatformBranchLifecycleState'], platform_version.platform_branch_lifecycle_state)
        self.assertEqual(
            platform_version_description['PlatformBranchName'], platform_version.platform_branch_name)
        self.assertEqual(platform_version_description['PlatformCategory'], platform_version.platform_category)
        self.assertEqual(
            platform_version_description['PlatformLifecycleState'], platform_version.platform_lifecycle_state)
        self.assertEqual(platform_version_description['PlatformName'], platform_version.platform_name)
        self.assertEqual(platform_version_description['PlatformOwner'], platform_version.platform_owner)
        self.assertEqual(platform_version_description['PlatformStatus'], platform_version.platform_status)
        self.assertEqual(platform_version_description['PlatformVersion'], platform_version.platform_version)
        self.assertEqual(
            platform_version_description['SolutionStackName'], platform_version.solution_stack_name)
        self.assertEqual(
            platform_version_description['SupportedAddonList'], platform_version.supported_addon_list)
        self.assertEqual(
            platform_version_description['SupportedTierList'], platform_version.supported_tier_list)

    def test_is_recommended(self):
        platform_arn = self.platform_version_description['PlatformArn']
        platform_version = PlatformVersion(
            platform_arn,
            platform_lifecycle_state='Recommended')

        self.assertTrue(platform_version.is_recommended)

        platform_version = PlatformVersion(
            platform_arn)
        self.assertFalse(platform_version.is_recommended)

    @mock.patch('ebcli.objects.platform.utils.parse_version')
    def test_sortable_version(self, parse_version_mock):
        version = pkg_version.parse(self.platform_version_description['PlatformVersion'])
        parse_version_mock.return_value = version

        platform_version = PlatformVersion.from_platform_version_description(self.platform_version_description)
        result = platform_version.sortable_version

        parse_version_mock.assert_called_once_with(self.platform_version_description['PlatformVersion'])
        self.assertIs(version, result)


class TestPlatformBranch(unittest.TestCase):
    platform_branch_summary = {
        "BranchName": "PHP 7.1 running on 64bit Amazon Linux",
        "LifecycleState": "Deprecated",
        "PlatformName": "PHP",
        "SupportedTierList": ["WebServer/Standard", "Worker/SQS/HTTP"]
    }

    def test_from_platform_branch_summary(self):
        platform_branch_summary = self.platform_branch_summary

        result = PlatformBranch.from_platform_branch_summary(
            platform_branch_summary)

        self.assertEqual(platform_branch_summary['BranchName'], result.branch_name)
        self.assertEqual(platform_branch_summary['LifecycleState'], result.lifecycle_state)
        self.assertEqual(platform_branch_summary['PlatformName'], result.platform_name)
        self.assertEqual(platform_branch_summary['SupportedTierList'], result.supported_tier_list)

    def test_is_beta(self):
        platform_branch = PlatformBranch(
            branch_name=self.platform_branch_summary['BranchName'],
            lifecycle_state='Beta')

        self.assertTrue(platform_branch.is_beta)

        platform_branch = PlatformBranch(
            branch_name=self.platform_branch_summary['BranchName'],
            lifecycle_state='Supported')

        self.assertFalse(platform_branch.is_beta)

    def test_is_deprecated(self):
        platform_branch = PlatformBranch(
            branch_name=self.platform_branch_summary['BranchName'],
            lifecycle_state='Deprecated')

        self.assertTrue(platform_branch.is_deprecated)

        platform_branch = PlatformBranch(
            branch_name=self.platform_branch_summary['BranchName'],
            lifecycle_state='Supported')

        self.assertFalse(platform_branch.is_deprecated)

    def test_is_retired(self):
        platform_branch = PlatformBranch(
            branch_name=self.platform_branch_summary['BranchName'],
            lifecycle_state='Retired')

        self.assertTrue(platform_branch.is_retired)

        platform_branch = PlatformBranch(
            branch_name=self.platform_branch_summary['BranchName'],
            lifecycle_state='Supported')

        self.assertFalse(platform_branch.is_retired)

    def test_is_supported(self):
        platform_branch = PlatformBranch(
            branch_name=self.platform_branch_summary['BranchName'],
            lifecycle_state='Supported')

        self.assertTrue(platform_branch.is_supported)

        platform_branch = PlatformBranch(
            branch_name=self.platform_branch_summary['BranchName'],
            lifecycle_state='Beta')

        self.assertFalse(platform_branch.is_supported)

    def test_hydrate(self):
        platform_branch_summary = self.platform_branch_summary
        get_platform_branch_by_name = mock.Mock(return_value=platform_branch_summary)

        platform_branch = PlatformBranch(platform_branch_summary['BranchName'])
        result = platform_branch.hydrate(get_platform_branch_by_name)

        self.assertEqual(platform_branch_summary['BranchName'], platform_branch.branch_name)
        self.assertEqual(platform_branch_summary['LifecycleState'], platform_branch.lifecycle_state)
        self.assertEqual(platform_branch_summary['PlatformName'], platform_branch.platform_name)
        self.assertEqual(platform_branch_summary['SupportedTierList'], platform_branch.supported_tier_list)
