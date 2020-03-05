# -*- coding: utf-8 -*-

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
import datetime
import os
import shutil

import mock
import unittest


from ebcli.core import fileoperations
from ebcli.operations import platformops
from ebcli.objects.exceptions import ValidationError, NotFoundError
from ebcli.objects.environment import Environment
from ebcli.objects.platform import PlatformVersion
from ebcli.objects.solutionstack import SolutionStack


class TestPlatformOperations(unittest.TestCase):

    custom_platforms_list = [
        {
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.0',
            'PlatformStatus': 'Ready',
            'SupportedAddonList': [
                'Log/S3',
                'WorkerDaemon/SQSD'
            ],
            'OperatingSystemName': 'Ubuntu',
            'PlatformCategory': 'custom',
            'PlatformOwner': 'self',
            'OperatingSystemVersion': '16.04',
            'SupportedTierList': [
                'WebServer/Standard',
                'Worker/SQS/HTTP'
            ]
        },
        {
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'PlatformStatus': 'Ready',
            'SupportedAddonList': [
                'Log/S3',
                'WorkerDaemon/SQSD'
            ],
            'OperatingSystemName': 'Amazon linux',
            'PlatformCategory': 'custom',
            'PlatformOwner': 'self',
            'OperatingSystemVersion': '2016.09.1',
            'SupportedTierList': [
                'WebServer/Standard',
                'Worker/SQS/HTTP'
            ]
        },
        {
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.2',
            'PlatformStatus': 'Ready',
            'SupportedAddonList': [
                'Log/S3',
                'WorkerDaemon/SQSD'
            ],
            'OperatingSystemName': 'Amazon linux',
            'PlatformCategory': 'custom',
            'PlatformOwner': 'self',
            'OperatingSystemVersion': '2016.09.1',
            'SupportedTierList': [
                'WebServer/Standard',
                'Worker/SQS/HTTP'
            ]
        },
        {
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.0',
            'PlatformStatus': 'Ready',
            'SupportedAddonList': [
                'Log/S3',
                'WorkerDaemon/SQSD'
            ],
            'OperatingSystemName': 'Amazon linux',
            'PlatformCategory': 'custom',
            'PlatformOwner': 'self',
            'OperatingSystemVersion': '2016.09.1',
            'SupportedTierList': [
                'WebServer/Standard',
                'Worker/SQS/HTTP'
            ]
        },
        {
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-3/1.0.0',
            'PlatformStatus': 'Ready',
            'SupportedAddonList': [
                'Log/S3',
                'WorkerDaemon/SQSD'
            ],
            'OperatingSystemName': 'Ubuntu',
            'PlatformCategory': 'custom',
            'PlatformOwner': 'self',
            'OperatingSystemVersion': '16.04',
            'SupportedTierList': [
                'WebServer/Standard',
                'Worker/SQS/HTTP'
            ]
        },
        {
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.2',
            'PlatformStatus': 'Failed',
            'SupportedTierList': [

            ],
            'SupportedAddonList': [

            ],
            'PlatformOwner': 'self'
        },
        {
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.1',
            'PlatformStatus': 'Failed',
            'SupportedTierList': [

            ],
            'SupportedAddonList': [

            ],
            'PlatformOwner': 'self'
        },
        {
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0',
            'PlatformStatus': 'Ready',
            'SupportedAddonList': [
                'Log/S3',
                'WorkerDaemon/SQSD'
            ],
            'OperatingSystemName': 'Amazon linux',
            'PlatformCategory': 'custom',
            'PlatformOwner': 'self',
            'OperatingSystemVersion': '2016.09.1',
            'SupportedTierList': [
                'WebServer/Standard',
                'Worker/SQS/HTTP'
            ]
        }
    ]

    eb_managed_platforms_list = [
        {
            "PlatformArn": "arn:aws:elasticbeanstalk:us-west-2::platform/Java 8 running on 64bit Amazon Linux/2.5.3",
            "PlatformOwner": "AWSElasticBeanstalk",
            "PlatformStatus": "Ready",
            "PlatformCategory": "Java",
            "OperatingSystemName": "Amazon Linux",
            "OperatingSystemVersion": "2017.03",
            "SupportedTierList": [
                "WebServer/Standard",
                "Worker/SQS/HTTP"
            ],
            "SupportedAddonList": [
                "Log/S3",
                "Monitoring/Healthd",
                "WorkerDaemon/SQSD"
            ]
        },
        {
            "PlatformArn": "arn:aws:elasticbeanstalk:us-west-2::platform/Java 8 running on 64bit Amazon Linux/2.5.2",
            "PlatformOwner": "AWSElasticBeanstalk",
            "PlatformStatus": "Ready",
            "PlatformCategory": "Java",
            "OperatingSystemName": "Amazon Linux",
            "OperatingSystemVersion": "2017.03",
            "SupportedTierList": [
                "WebServer/Standard",
                "Worker/SQS/HTTP"
            ],
            "SupportedAddonList": [
                "Log/S3",
                "Monitoring/Healthd",
                "WorkerDaemon/SQSD"
            ]
        },
        {
            "PlatformArn": "arn:aws:elasticbeanstalk:us-west-2::platform/Go 1 running on 64bit Amazon Linux/2.1.0",
            "PlatformOwner": "AWSElasticBeanstalk",
            "PlatformStatus": "Ready",
            "PlatformCategory": "Go",
            "OperatingSystemName": "Amazon Linux",
            "OperatingSystemVersion": "2016.03",
            "SupportedTierList": [
                "WebServer/Standard",
                "Worker/SQS/HTTP"
            ],
            "SupportedAddonList": []
        },
        {
            "PlatformArn": "arn:aws:elasticbeanstalk:us-west-2::platform/Docker running on 64bit Amazon Linux/2.1.0",
            "PlatformOwner": "AWSElasticBeanstalk",
            "PlatformStatus": "Ready",
            "PlatformCategory": "Docker",
            "OperatingSystemName": "Amazon Linux",
            "OperatingSystemVersion": "2016.03",
            "SupportedTierList": [
                "WebServer/Standard",
                "Worker/SQS/HTTP"
            ],
            "SupportedAddonList": []
        },
    ]

    describe_platform_result = {
        'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0',
        'PlatformOwner': 'self',
        'PlatformName': 'custom-platform-1',
        'PlatformVersion': '1.0.0',
        'PlatformStatus': 'Ready',
        'DateCreated': '2017-07-05T22:55:15.583Z',
        'DateUpdated': '2017-07-05T23:07:02.859Z',
        'PlatformCategory': 'custom',
        'Description': 'Sample NodeJs Container.',
        'Maintainer': '<please enter your name here>',
        'OperatingSystemName': 'Ubuntu',
        'OperatingSystemVersion': '16.04',
        'ProgrammingLanguages': [
            {
                'Name': 'ECMAScript',
                'Version': 'ECMA-262'
            }
        ],
        'Frameworks': [
            {
                'Name': 'NodeJs',
                'Version': '4.4.4'
            }
        ],
        'CustomAmiList': [
            {
                'VirtualizationType': 'pv',
                'ImageId': 'ami-123123'
            },
            {
                'VirtualizationType': 'hvm',
                'ImageId': 'ami-123123'
            }
        ],
        'SupportedTierList': [
            'WebServer/Standard',
            'Worker/SQS/HTTP'
        ],
        'SupportedAddonList': [
            'Log/S3',
            'WorkerDaemon/SQSD'
        ]
    }

    def setUp(self):
        if not os.path.exists('testDir'):
            os.makedirs('testDir')
        os.chdir('testDir')

        self.platform_name = 'test-platform'
        self.platform_version = '1.0.0'
        self.platform_arn = 'arn:aws:elasticbeanstalk:us-east-1:123123123123:platform/{0}/{1}'.format(
                self.platform_name,
                self.platform_version)

    def tearDown(self):
        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            shutil.rmtree('testDir')

    @mock.patch('ebcli.operations.platformops.io')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk')
    @mock.patch('ebcli.operations.platformops.commonops')
    @mock.patch('ebcli.operations.platformops._version_to_arn')
    def test_delete_no_environments(
            self,
            _version_to_arn_mock,
            commonops_mock,
            elasticbeanstalk_mock,
            io_mock
    ):
        _version_to_arn_mock.return_value = self.platform_arn
        elasticbeanstalk_mock.get_environments.return_value = []
        elasticbeanstalk_mock.delete_platform.return_value = { 'ResponseMetadata': { 'RequestId': 'request-id' } }
        
        platformops.delete_platform_version(self.platform_arn, False)

        elasticbeanstalk_mock.get_environments.assert_called_with()
        elasticbeanstalk_mock.delete_platform.assert_called_with(self.platform_arn)

    @mock.patch('ebcli.operations.platformops.io')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk')
    @mock.patch('ebcli.operations.platformops.commonops')
    @mock.patch('ebcli.operations.platformops._version_to_arn')
    def test_delete_with_environments(
            self,
            _version_to_arn_mock,
            commonops_mock,
            elasticbeanstalk_mock,
            io_mock
    ):
        _version_to_arn_mock.return_value = self.platform_arn
        environments = [ 
                Environment(name='env1', platform=PlatformVersion(self.platform_arn)),
                Environment(name='no match', platform=PlatformVersion('arn:aws:elasticbeanstalk:us-east-1:123123123123:platform/foo/2.0.0')),
                Environment(name='env2', platform=PlatformVersion(self.platform_arn))
        ]

        elasticbeanstalk_mock.get_environments.return_value = environments
        elasticbeanstalk_mock.delete_platform.return_value = { 'ResponseMetadata': { 'RequestId': 'request-id' } }
        
        self.assertRaises(ValidationError, platformops.delete_platform_version, self.platform_arn, False)

        elasticbeanstalk_mock.get_environments.assert_called_with()

    @mock.patch('ebcli.lib.elasticbeanstalk.list_platform_versions')
    def test_list_custom_platform_versions__filtered_by_owner_name(self, list_platform_versions_mock):
        list_platform_versions_mock.return_value = self.custom_platforms_list

        custom_platforms = platformops.list_custom_platform_versions(
            show_status=True
        )

        self.assertEqual(
            [
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3  Status: Ready',
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.2  Status: Ready',
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.0  Status: Ready',
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-3/1.0.0  Status: Ready',
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.0  Status: Ready',
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.2  Status: Failed',
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.1  Status: Failed',
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0  Status: Ready',
            ],
            custom_platforms
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.list_platform_versions')
    def test_list_custom_platform_versions__filtered_by_owner_name__display_list_without_status(self, list_platform_versions_mock):
        list_platform_versions_mock.return_value = self.custom_platforms_list

        custom_platforms = platformops.list_custom_platform_versions()

        self.assertEqual(
            [
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.2',
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.0',
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-3/1.0.0',
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.0',
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.2',
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.1',
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0',
            ],
            custom_platforms
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.list_platform_versions')
    def test_list_eb_managed_platform_versions(self, list_platform_versions_mock):
        list_platform_versions_mock.return_value = self.eb_managed_platforms_list

        eb_managed_platforms = platformops.list_eb_managed_platform_versions()

        self.assertEqual(
            [
                'arn:aws:elasticbeanstalk:us-west-2::platform/Java 8 running on 64bit Amazon Linux/2.5.3',
                'arn:aws:elasticbeanstalk:us-west-2::platform/Java 8 running on 64bit Amazon Linux/2.5.2',
                'arn:aws:elasticbeanstalk:us-west-2::platform/Go 1 running on 64bit Amazon Linux/2.1.0',
                'arn:aws:elasticbeanstalk:us-west-2::platform/Docker running on 64bit Amazon Linux/2.1.0'
            ],
            eb_managed_platforms
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.list_platform_versions')
    @mock.patch('ebcli.lib.elasticbeanstalk.describe_platform_version')
    def test_describe_custom_platform_version(self, describe_platform_version_mock, list_platform_versions_mock):
        list_platform_versions_mock.return_value = self.custom_platforms_list
        describe_platform_version_mock.return_value = self.describe_platform_result

        custom_platform = platformops.describe_custom_platform_version(
            platform_name='custom-platform-1',
            platform_version='1.0.0',
            owner='self'
        )

        self.assertEqual(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0',
            custom_platform['PlatformArn']
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.describe_platform_version')
    def test_describe_custom_platform_version__platform_arn_passed_in(self, describe_platform_version_mock):
        describe_platform_version_mock.return_value = self.describe_platform_result

        custom_platform = platformops.describe_custom_platform_version(
            platform_arn='arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        )

        self.assertEqual(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0',
            custom_platform['PlatformArn']
        )

    @mock.patch('ebcli.operations.platformops.list_custom_platform_versions')
    def test_get_latest_custom_platform(self, custom_platforms_lister_mock):
        custom_platforms_lister_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.0'
        ]
        current_platform_arn = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.0'
        self.assertEqual(
            PlatformVersion('arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.3'),
            platformops.get_latest_custom_platform(current_platform_arn)
        )

    def test_group_custom_platforms_by_platform_name(self):
        custom_platform_arns = [custom_platform['PlatformArn'] for custom_platform in self.custom_platforms_list]

        self.assertEqual(
            [
                'custom-platform-1',
                'custom-platform-2',
                'custom-platform-3',
                'custom-platform-4'
            ],
            platformops.group_custom_platforms_by_platform_name(custom_platform_arns)
        )

    @mock.patch('ebcli.lib.utils.prompt_for_index_in_list')
    @mock.patch('ebcli.operations.platformops.group_custom_platforms_by_platform_name')
    def test_prompt_customer_for_custom_platform_name(
            self,
            custom_platforms_grouper_mock,
            index_prompter_mock
    ):
        custom_platform_arns = [custom_platform['PlatformArn'] for custom_platform in self.custom_platforms_list]
        custom_platforms_grouper_mock.return_value = [
            'custom-platform-1',
            'custom-platform-2',
            'custom-platform-3',
            'custom-platform-4'
        ]

        index_prompter_mock.return_value = 2

        self.assertEqual(
            'custom-platform-3',
            platformops.prompt_customer_for_custom_platform_name(custom_platform_arns)
        )

    @mock.patch('ebcli.lib.utils.prompt_for_index_in_list')
    def test_prompt_customer_for_custom_platform_version(self, index_prompter_mock):
        version_to_arn_mappings = {
            '1.0.3': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.3',
            '1.0.0': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.0',
            '1.0.2': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.2'
        }

        index_prompter_mock.return_value = 2

        self.assertEqual(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.3',
            platformops.prompt_customer_for_custom_platform_version(version_to_arn_mappings)
        )

    @mock.patch('ebcli.lib.utils.prompt_for_index_in_list')
    def test_resolve_custom_platform_version__multiple_versions_to_choose_from(self, index_prompter_mock):
        custom_platforms = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.0',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.2'
        ]
        selected_platform_name = 'custom-platform-2'

        index_prompter_mock.return_value = 0

        self.assertEqual(
            PlatformVersion('arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.0'),
            platformops.resolve_custom_platform_version(custom_platforms, selected_platform_name)
        )

    def test_resolve_custom_platform_version__single_version_available(self):
        custom_platforms = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.0',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.2'
        ]
        selected_platform_name = 'custom-platform-1'

        self.assertEqual(
            PlatformVersion('arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3'),
            platformops.resolve_custom_platform_version(custom_platforms, selected_platform_name)
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    def test_version_to_arn__is_valid_eb_managed_platform_arn(
            self,
            get_platform_name_mock
    ):
        get_platform_name_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2::platform/Java 8 running on 64bit Amazon Linux/2.5.3'
        self.assertEqual(
            'arn:aws:elasticbeanstalk:us-west-2::platform/Java 8 running on 64bit Amazon Linux/2.5.3',
            platformops._version_to_arn(
                'arn:aws:elasticbeanstalk:us-west-2::platform/Java 8 running on 64bit Amazon Linux/2.5.3'
            )
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    def test_version_to_arn__is_valid_custom_platform_arn(
            self,
            get_platform_name_mock
    ):
        get_platform_name_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3'
        self.assertEqual(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3',
            platformops._version_to_arn(
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3'
            )
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    def test_version_to_arn__is_invalid_version_number(
            self,
            get_platform_name_mock
    ):
        get_platform_name_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3'

        with self.assertRaises(platformops.InvalidPlatformVersionError) as context_manager:
            platformops._version_to_arn('1.0.3.3')
        self.assertEqual(
            'No such version exists for the current platform.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops._get_platform_arn')
    def test_version_to_arn__is_valid_version_number_but_does_not_match_platform_name(
            self,
            _get_platform_arn_mock,
            get_platform_name_mock
    ):
        _get_platform_arn_mock.return_value = None
        get_platform_name_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3'

        with self.assertRaises(platformops.InvalidPlatformVersionError) as context_manager:
            platformops._version_to_arn('1.0.4')
        self.assertEqual(
            'No such version exists for the current platform.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops._get_platform_arn')
    def test_version_to_arn__is_valid_version_number_but_does_not_match_platform_name(
            self,
            _get_platform_arn_mock,
            get_platform_name_mock
    ):
        _get_platform_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3'
        get_platform_name_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3'

        self.assertEqual(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3',
            platformops._version_to_arn('1.0.3')
        )
        _get_platform_arn_mock.assert_called_once_with(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3',
            '1.0.3',
            owner='self'
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops._get_platform_arn')
    def test_version_to_arn__is_valid_arn_in_short_format(
            self,
            _get_platform_arn_mock,
            get_platform_name_mock
    ):
        _get_platform_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3'
        get_platform_name_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3'

        self.assertEqual(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3',
            platformops._version_to_arn('custom-platform-1/1.0.3')
        )

        _get_platform_arn_mock.assert_called_once_with('custom-platform-1', '1.0.3', owner='self')

    def test_name_to_arn__is_valid_eb_managed_platform_arn(self):
        self.assertEqual(
            'arn:aws:elasticbeanstalk:us-west-2::platform/Java 8 running on 64bit Amazon Linux/2.5.3',
            platformops._name_to_arn(
                'arn:aws:elasticbeanstalk:us-west-2::platform/Java 8 running on 64bit Amazon Linux/2.5.3'
            )
        )

    def test_name_to_arn__is_valid_custom_platform_arn(self):
        self.assertEqual(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3',
            platformops._name_to_arn(
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3'
            )
        )

    @mock.patch('ebcli.operations.platformops._get_platform_arn')
    def test_name_to_arn__is_valid_platform_name(
            self,
            _get_platform_arn_mock
    ):
        _get_platform_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3'

        self.assertEqual(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3',
            platformops._name_to_arn('custom-platform-1')
        )
        _get_platform_arn_mock.assert_called_once_with('custom-platform-1', 'latest', owner='self')

    @mock.patch('ebcli.operations.platformops._get_platform_arn')
    def test_name_to_arn__is_valid_platform_short_name(
            self,
            _get_platform_arn_mock
    ):
        _get_platform_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3'

        self.assertEqual(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3',
            platformops._name_to_arn('custom-platform-1/1.0.3')
        )
        _get_platform_arn_mock.assert_called_once_with('custom-platform-1', '1.0.3', owner='self')

    @mock.patch('ebcli.operations.platformops.describe_custom_platform_version')
    def test_get_platform_arn(
            self,
            describe_custom_platform_version_mock
    ):
        describe_custom_platform_version_mock.return_value = {
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3'
        }

        self.assertEqual(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3',
            platformops._get_platform_arn('custom-platform-1', '1.0.3', 'self')
        )

        describe_custom_platform_version_mock.assert_called_once_with(
            owner='self',
            platform_name='custom-platform-1',
            platform_version='1.0.3'
        )

    @mock.patch('ebcli.operations.platformops.describe_custom_platform_version')
    def test_get_platform_arn__no_platform_returned(
            self,
            describe_custom_platform_version_mock
    ):
        describe_custom_platform_version_mock.return_value = {}

        self.assertIsNone(platformops._get_platform_arn('custom-platform-1', '1.0.3', 'self'))

        describe_custom_platform_version_mock.assert_called_once_with(
            owner='self',
            platform_name='custom-platform-1',
            platform_version='1.0.3'
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops._version_to_arn')
    @mock.patch('ebcli.operations.platformops.describe_custom_platform_version')
    @mock.patch('ebcli.operations.platformops.io.echo')
    def test_get_version_status(
            self,
            echo_mock,
            describe_custom_platform_version_mock,
            _version_to_arn_mock,
            get_platform_name_mock
    ):
        get_platform_name_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        _version_to_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        describe_custom_platform_version_mock.return_value = self.describe_platform_result
        platformops.get_version_status('1.0.0')
        echo_mock.assert_has_calls(
            [
                mock.call('Platform: ', 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'),
                mock.call('Name: ', 'custom-platform-1'),
                mock.call('Version: ', '1.0.0'),
                mock.call('Maintainer: ', '<please enter your name here>'),
                mock.call('Description: ', 'Sample NodeJs Container.'),
                mock.call('Operating System: ', 'Ubuntu'),
                mock.call('Operating System Version: ', '16.04'),
                mock.call('Supported Tiers: ', ['WebServer/Standard', 'Worker/SQS/HTTP']),
                mock.call('Status: ', 'Ready'),
                mock.call('Created: ', '2017-07-05T22:55:15.583Z'),
                mock.call('Updated: ', '2017-07-05T23:07:02.859Z')
            ]
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_version')
    @mock.patch('ebcli.operations.platformops._version_to_arn')
    @mock.patch('ebcli.operations.platformops.describe_custom_platform_version')
    @mock.patch('ebcli.operations.platformops.io.echo')
    def test_get_version_status__version_derived_from_config_yml(
            self,
            echo_mock,
            describe_custom_platform_version_mock,
            _version_to_arn_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        get_platform_version_mock.return_value = '1.0.0'
        get_platform_name_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        _version_to_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        describe_custom_platform_version_mock.return_value = self.describe_platform_result
        platformops.get_version_status(None)
        echo_mock.assert_has_calls(
            [
                mock.call('Platform: ', 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'),
                mock.call('Name: ', 'custom-platform-1'),
                mock.call('Version: ', '1.0.0'),
                mock.call('Maintainer: ', '<please enter your name here>'),
                mock.call('Description: ', 'Sample NodeJs Container.'),
                mock.call('Operating System: ', 'Ubuntu'),
                mock.call('Operating System Version: ', '16.04'),
                mock.call('Supported Tiers: ', ['WebServer/Standard', 'Worker/SQS/HTTP']),
                mock.call('Status: ', 'Ready'),
                mock.call('Created: ', '2017-07-05T22:55:15.583Z'),
                mock.call('Updated: ', '2017-07-05T23:07:02.859Z')
            ]
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.update_platform_version')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_version')
    @mock.patch('ebcli.operations.platformops._version_to_arn')
    @mock.patch('ebcli.operations.platformops._get_latest_version')
    @mock.patch('ebcli.operations.platformops.describe_custom_platform_version')
    @mock.patch('ebcli.operations.platformops.io.echo')
    def test_get_version_status__latest_version_retrieved_from_aws(
            self,
            echo_mock,
            describe_custom_platform_version_mock,
            _get_latest_version_mock,
            _version_to_arn_mock,
            get_platform_version_mock,
            get_platform_name_mock,
            update_platform_version_mock
    ):
        _get_latest_version_mock.return_value = '1.0.0'
        get_platform_version_mock.return_value = None
        get_platform_name_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        _version_to_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        describe_custom_platform_version_mock.return_value = self.describe_platform_result
        platformops.get_version_status(None)
        echo_mock.assert_has_calls(
            [
                mock.call('Platform: ', 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'),
                mock.call('Name: ', 'custom-platform-1'),
                mock.call('Version: ', '1.0.0'),
                mock.call('Maintainer: ', '<please enter your name here>'),
                mock.call('Description: ', 'Sample NodeJs Container.'),
                mock.call('Operating System: ', 'Ubuntu'),
                mock.call('Operating System Version: ', '16.04'),
                mock.call('Supported Tiers: ', ['WebServer/Standard', 'Worker/SQS/HTTP']),
                mock.call('Status: ', 'Ready'),
                mock.call('Created: ', '2017-07-05T22:55:15.583Z'),
                mock.call('Updated: ', '2017-07-05T23:07:02.859Z')
            ]
        )
        update_platform_version_mock.assert_called_once_with('1.0.0')

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_version')
    @mock.patch('ebcli.operations.platformops._version_to_arn')
    @mock.patch('ebcli.operations.platformops._get_latest_version')
    @mock.patch('ebcli.operations.platformops.describe_custom_platform_version')
    def test_get_version_status__version_could_not_be_determined(
            self,
            describe_custom_platform_version_mock,
            _get_latest_version_mock,
            _version_to_arn_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        _get_latest_version_mock.return_value = None
        get_platform_version_mock.return_value = None
        get_platform_name_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        _version_to_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        describe_custom_platform_version_mock.return_value = self.describe_platform_result
        with self.assertRaises(platformops.InvalidPlatformVersionError) as context_manager:
            platformops.get_version_status(None)
        self.assertEqual(
            'No such version exists for the current platform.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops._version_to_arn')
    @mock.patch('ebcli.operations.platformops.describe_custom_platform_version')
    def test_get_version_status__invalid_platform_version(
            self,
            describe_custom_platform_version_mock,
            _version_to_arn_mock,
            get_platform_name_mock
    ):
        get_platform_name_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        _version_to_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        describe_custom_platform_version_mock.return_value = []

        with self.assertRaises(platformops.InvalidPlatformVersionError) as context_manager:
            platformops.get_version_status('1.0.0')
        self.assertEqual(
            'No such version exists for the current platform.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.platformops._raise_if_version_format_is_invalid')
    @mock.patch('ebcli.operations.platformops._raise_if_directory_is_empty')
    @mock.patch('ebcli.operations.platformops._raise_if_platform_definition_file_is_missing')
    def test_create_platform_version__invalid_version(
            self,
            _raise_if_platform_definition_file_is_missing_mock,
            _raise_if_directory_is_empty_mock,
            _raise_if_version_format_is_invalid_mock
    ):
        _raise_if_directory_is_empty_mock.side_effect = None
        _raise_if_platform_definition_file_is_missing_mock.side_effect = None
        _raise_if_version_format_is_invalid_mock.side_effect = platformops.InvalidPlatformVersionError

        with self.assertRaises(platformops.InvalidPlatformVersionError):
            platformops.create_platform_version('1.0.0.5', False, False, True, 't2.micro')

    @mock.patch('ebcli.operations.platformops._raise_if_directory_is_empty')
    @mock.patch('ebcli.operations.platformops._raise_if_platform_definition_file_is_missing')
    def test_create_platform_version__platform_definition_file_absent(
            self,
            _raise_if_platform_definition_file_is_missing_mock,
            _raise_if_directory_is_empty_mock
    ):
        _raise_if_platform_definition_file_is_missing_mock.side_effect = platformops.PlatformWorkspaceEmptyError
        _raise_if_directory_is_empty_mock.side_effect = None

        with self.assertRaises(platformops.PlatformWorkspaceEmptyError):
            platformops.create_platform_version('1.0.0', False, False, True, 't2.micro')

    @mock.patch('ebcli.operations.platformops.fileoperations.update_platform_version')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_instance_profile')
    @mock.patch('ebcli.operations.platformops.commonops.get_default_keyname')
    @mock.patch('ebcli.operations.platformops.commonops.set_environment_for_current_branch')
    @mock.patch('ebcli.operations.platformops._raise_if_directory_is_empty')
    @mock.patch('ebcli.operations.platformops._raise_if_platform_definition_file_is_missing')
    @mock.patch('ebcli.operations.platformops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.platformops._get_latest_version')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.create_platform_version')
    @mock.patch('ebcli.operations.platformops._resolve_version_number')
    @mock.patch('ebcli.operations.platformops._resolve_version_label')
    @mock.patch('ebcli.operations.platformops._upload_platform_version_to_s3_if_necessary')
    @mock.patch('ebcli.operations.platformops._resolve_s3_bucket_and_key')
    @mock.patch('ebcli.operations.platformops.stream_platform_logs')
    def test_create_platform_version__version_not_passed_in__next_version_resolved_by_the_ebcli(
            self,
            stream_platform_logs_mock,
            _resolve_s3_bucket_and_key_mock,
            _upload_platform_version_to_s3_if_necessary_mock,
            _resolve_version_label_mock,
            _resolve_version_number_mock,
            create_platform_version_mock,
            _get_latest_version_mock,
            get_source_control_mock,
            _raise_if_platform_definition_file_is_missing_mock,
            _raise_if_directory_is_empty_mock,
            set_environment_for_current_branch_mock,
            get_default_keyname_mock,
            get_instance_profile_mock,
            get_platform_name_mock,
            update_platform_version_mock
    ):
        _raise_if_platform_definition_file_is_missing_mock.side_effect = None
        _raise_if_directory_is_empty_mock.side_effect = None
        get_default_keyname_mock.return_value = 'aws-eb-us-west-2'
        get_instance_profile_mock.return_value = 'default'
        get_platform_name_mock.return_value = 'custom-platform-1'
        get_source_control_mock.untracked_changes_exist = mock.MagicMock(return_value=False)
        _resolve_version_label_mock.return_value = 'my-version-label'
        _resolve_s3_bucket_and_key_mock.return_value = ('s3-bucket', 's3-key', 'file_path')
        create_platform_version_mock.return_value = {
            'PlatformSummary': {
                'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
            },
            'ResponseMetadata': {
                'RequestId': 'my-request-id'
            }
        }
        _get_latest_version_mock.return_value = '1.0.0'
        _resolve_version_number_mock.return_value = '2.0.0'

        platformops.create_platform_version(None, True, False, False, 't2.micro')

        _upload_platform_version_to_s3_if_necessary_mock.assert_called_once_with('s3-bucket', 's3-key', 'file_path')
        _resolve_version_number_mock.assert_called_once_with('custom-platform-1', True, False, False)
        create_platform_version_mock.assert_called_once_with(
            'custom-platform-1',
            '2.0.0',
            's3-bucket',
            's3-key',
            'default',
            'aws-eb-us-west-2',
            't2.micro',
            [],
            None,
        )
        update_platform_version_mock.assert_called_once_with('2.0.0')
        set_environment_for_current_branch_mock.assert_called_once_with(
            'eb-custom-platform-builder-packer'
        )
        stream_platform_logs_mock.assert_called_once_with(
            {
                'PlatformSummary': {
                    'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
                },
                'ResponseMetadata': {
                    'RequestId': 'my-request-id'
                }
            },
            'custom-platform-1',
            '2.0.0',
            None
        )

    @mock.patch('ebcli.operations.platformops._raise_if_directory_is_empty')
    def test_create_platform_version__directory_is_empty(
            self,
            _raise_if_directory_is_empty_mock,
    ):
        _raise_if_directory_is_empty_mock.side_effect = platformops.PlatformWorkspaceEmptyError

        with self.assertRaises(platformops.PlatformWorkspaceEmptyError):
            platformops.create_platform_version(None, False, False, True, 't2.micro')

    @mock.patch('ebcli.operations.platformops.get_platforms')
    def test_get_latest_version(self, get_platforms_mock):
        get_platforms_mock.return_value = {
            'custom-platform-1': '1.0.0'
        }
        self.assertEqual(
            '1.0.0',
            platformops._get_latest_version(
                platform_name='custom-platform-1',
                owner='self',
                ignored_states=['Failed']
            )
        )
        get_platforms_mock.assert_called_once_with(
            ignored_states=['Failed'],
            owner='self',
            platform_name='custom-platform-1',
            platform_version='latest'
        )


    @mock.patch('ebcli.operations.platformops.get_platforms')
    def test_get_latest_version__version_not_found(self, get_platforms_mock):
        get_platforms_mock.return_value = {}
        self.assertIsNone(
            platformops._get_latest_version(
                platform_name='custom-platform-1',
                owner='self',
                ignored_states=['Failed']
            )
        )
        get_platforms_mock.assert_called_once_with(
            ignored_states=['Failed'],
            owner='self',
            platform_name='custom-platform-1',
            platform_version='latest'
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.platformops.yaml.safe_load')
    def test_enable_healthd(
            self,
            load_mock,
            traverse_mock
    ):
        open('platform.yaml', 'w').close()
        load_mock.return_value = {
            'option_settings': [
                {
                    'namespace': 'aws:ec2:vpc',
                    'option_name': 'VPCId',
                    'value': 'vpc-1231223'
                }
            ]
        }
        platformops._enable_healthd()
        with open('platform.yaml') as file:
            self.assertEqual(
                """option_settings:
- namespace: aws:ec2:vpc
  option_name: VPCId
  value: vpc-1231223
- namespace: aws:elasticbeanstalk:healthreporting:system
  option_name: SystemType
  value: enhanced
- namespace: aws:elasticbeanstalk:environment
  option_name: ServiceRole
  value: aws-elasticbeanstalk-service-role
""",
                file.read()
            )

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_version')
    @mock.patch('ebcli.operations.platformops.describe_custom_platform_version')
    @mock.patch('ebcli.operations.platformops.print_events')
    def test_show_platform_events(
            self,
            print_events_mock,
            describe_custom_platform_version_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        get_platform_name_mock.return_value = 'custom-platform-1'
        get_platform_version_mock.return_value = '1.0.0'
        describe_custom_platform_version_mock.return_value = {
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        }

        platformops.show_platform_events(True, None)

        describe_custom_platform_version_mock.assert_called_once_with(
            owner='self',
            platform_name='custom-platform-1',
            platform_version='1.0.0'
        )
        print_events_mock.assert_called_once_with(
            app_name=None,
            env_name=None,
            follow=True,
            platform_arn='arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.print_events')
    @mock.patch('ebcli.operations.platformops._version_to_arn')
    def test_show_platform_events__version_provided(
            self,
            _version_to_arn_mock,
            print_events_mock,
            get_platform_name_mock
    ):
        get_platform_name_mock.return_value = 'custom-platform-1'
        _version_to_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'

        platformops.show_platform_events(True, '1.0.0')

        _version_to_arn_mock.assert_called_once_with('1.0.0')
        print_events_mock.assert_called_once_with(
            app_name=None,
            env_name=None,
            follow=True,
            platform_arn='arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.update_platform_version')
    @mock.patch('ebcli.operations.platformops._get_latest_version')
    @mock.patch('ebcli.operations.platformops.get_version_status')
    def test_set_workspace_to_latest(
            self,
            get_version_status_mock,
            _get_platform_version_mock,
            update_platform_version_mock,
            get_platform_name_mock
    ):
        get_platform_name_mock.return_value = 'custom-platform-1'
        _get_platform_version_mock.return_value = '1.0.0'

        platformops.set_workspace_to_latest()

        get_version_status_mock.assert_called_once_with('1.0.0')
        update_platform_version_mock.assert_called_once_with('1.0.0')

    @mock.patch('ebcli.operations.platformops.fileoperations.update_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.update_platform_version')
    @mock.patch('ebcli.operations.platformops.get_version_status')
    @mock.patch('ebcli.operations.platformops._name_to_arn')
    def test_set_platform(
            self,
            _name_to_arn_mock,
            get_version_status_mock,
            update_platform_version_mock,
            update_platform_name_mock
    ):
        _name_to_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'

        platformops.set_platform('custom-platform-1')

        get_version_status_mock.assert_called_once_with('1.0.0')
        update_platform_version_mock.assert_called_once_with('1.0.0')
        update_platform_name_mock.assert_called_once_with('custom-platform-1')

    @mock.patch('ebcli.operations.platformops.fileoperations.update_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.update_platform_version')
    @mock.patch('ebcli.operations.platformops.get_version_status')
    @mock.patch('ebcli.operations.platformops._name_to_arn')
    @mock.patch('ebcli.operations.platformops.io.echo')
    def test_set_platform__failed_to_get_version_status(
            self,
            echo_mock,
            _name_to_arn_mock,
            get_version_status_mock,
            update_platform_version_mock,
            update_platform_name_mock
    ):
        _name_to_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        get_version_status_mock.side_effect = platformops.InvalidPlatformVersionError

        platformops.set_platform('custom-platform-1')

        get_version_status_mock.assert_called_once_with('1.0.0')
        update_platform_version_mock.assert_called_once_with('1.0.0')
        update_platform_name_mock.assert_called_once_with('custom-platform-1')
        echo_mock.assert_has_calls(
            [
                mock.call('Setting workspace platform version to:'),
                mock.call('New platform "custom-platform-1"')
            ]
        )

    @mock.patch('ebcli.operations.platformops.get_platforms')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_current_directory_name')
    @mock.patch('ebcli.operations.platformops.utils.prompt_for_item_in_list')
    def test_get_platform_name_and_version_interactive(
            self,
            prompt_for_item_in_list_mock,
            get_current_directory_name_mock,
            get_platforms_mock
    ):
        get_platforms_mock.return_value = {
            'custom-platform-1': '1.0.0'
        }
        get_current_directory_name_mock.return_value = 'file_name'
        prompt_for_item_in_list_mock.return_value = 'custom-platform-1'

        self.assertEqual(
            ('custom-platform-1', '1.0.0'),
            platformops.get_platform_name_and_version_interactive()
        )

    @mock.patch('ebcli.operations.platformops.get_platforms')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_current_directory_name')
    @mock.patch('ebcli.operations.platformops.utils.get_unique_name')
    @mock.patch('ebcli.operations.platformops.io.prompt_for_unique_name')
    def test_get_platform_name_and_version_interactive__no_platforms(
            self,
            prompt_for_unique_name_mock,
            get_unique_name_mock,
            get_current_directory_name_mock,
            get_platforms_mock
    ):
        get_platforms_mock.return_value = dict()
        get_current_directory_name_mock.return_value = 'file_name'
        get_unique_name_mock.return_value = 'unique-name'
        prompt_for_unique_name_mock.return_value = 'my-unique-name'

        self.assertEqual(
            ('my-unique-name', None),
            platformops.get_platform_name_and_version_interactive()
        )
        get_unique_name_mock.assert_called_once_with('file_name', [])
        prompt_for_unique_name_mock.assert_called_once_with('unique-name', [])

    @mock.patch('ebcli.operations.platformops.list_eb_managed_platform_versions')
    def test_get_latest_eb_managed_platform(
            self,
            list_eb_managed_platform_versions_mock
    ):
        platform_arn = "arn:aws:elasticbeanstalk:us-west-2::platform/Java 8 running on 64bit Amazon Linux/2.5.3"
        list_eb_managed_platform_versions_mock.return_value = [
            "arn:aws:elasticbeanstalk:us-west-2::platform/Java 8 running on 64bit Amazon Linux/2.5.3",
            "arn:aws:elasticbeanstalk:us-west-2::platform/Java 8 running on 64bit Amazon Linux/2.6.3"
        ]

        self.assertEqual(
            'arn:aws:elasticbeanstalk:us-west-2::platform/Java 8 running on 64bit Amazon Linux/2.5.3',
            platformops.get_latest_eb_managed_platform(platform_arn).arn
        )

        list_eb_managed_platform_versions_mock.assert_called_once_with(
            platform_name='Java 8 running on 64bit Amazon Linux',
            status='Ready'
        )

    @mock.patch('ebcli.operations.platformops.list_eb_managed_platform_versions')
    def test_get_latest_eb_managed_platform__cannot_find_latest(
            self,
            list_eb_managed_platform_versions_mock
    ):
        platform_arn = "arn:aws:elasticbeanstalk:us-west-2::platform/Java 8 running on 64bit Amazon Linux/2.5.3"
        list_eb_managed_platform_versions_mock.return_value = []

        self.assertIsNone(platformops.get_latest_eb_managed_platform(platform_arn))

        list_eb_managed_platform_versions_mock.assert_called_once_with(
            platform_name='Java 8 running on 64bit Amazon Linux',
            status='Ready'
        )

    @mock.patch('ebcli.operations.platformops.heuristics.directory_is_empty')
    def test_raise_if_directory_is_empty__directory_is_not_empty(
            self,
            directory_is_empty_mock
    ):
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5',
            workspace_type='Platform'
        )
        cwd = os.getcwd()
        directory_is_empty_mock.return_value = False

        platformops._raise_if_directory_is_empty()

        self.assertEqual(cwd, os.getcwd())

    @mock.patch('ebcli.operations.platformops.heuristics.directory_is_empty')
    def test_raise_if_directory_is_empty__directory_is_empty(
            self,
            directory_is_empty_mock
    ):
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5',
            workspace_type='Platform'
        )
        cwd = os.getcwd()
        directory_is_empty_mock.return_value = True
        with self.assertRaises(platformops.PlatformWorkspaceEmptyError) as context_manager:
            platformops._raise_if_directory_is_empty()

        self.assertEqual(
            'The current directory does not contain any Platform configuration files. Unable to create new Platform.',
            str(context_manager.exception)
        )
        self.assertEqual(cwd, os.getcwd())

    @mock.patch('ebcli.operations.platformops._get_latest_version')
    def test__resolve_version_number__could_not_get_latest_version(
            self,
            _get_latest_version_mock
    ):
        _get_latest_version_mock.return_value = None

        self.assertEqual(
            '1.0.0',
            platformops._resolve_version_number('my-custom-platform', True, False, False)
        )

    @mock.patch('ebcli.operations.platformops._get_latest_version')
    def test__resolve_version_number__increment_major_version(
            self,
            _get_latest_version_mock
    ):
        _get_latest_version_mock.return_value = '1.0.3'

        self.assertEqual(
            '2.0.0',
            platformops._resolve_version_number('my-custom-platform', True, False, False)
        )

    @mock.patch('ebcli.operations.platformops._get_latest_version')
    def test__resolve_version_number__increment_minor_version(
            self,
            _get_latest_version_mock
    ):
        _get_latest_version_mock.return_value = '1.0.3'

        self.assertEqual(
            '1.1.0',
            platformops._resolve_version_number('my-custom-platform', False, True, False)
        )

    @mock.patch('ebcli.operations.platformops._get_latest_version')
    def test__resolve_version_number__increment_patch_version(
            self,
            _get_latest_version_mock
    ):
        _get_latest_version_mock.return_value = '1.0.3'

        self.assertEqual(
            '1.0.4',
            platformops._resolve_version_number('my-custom-platform', False, False, True)
        )

    @mock.patch('ebcli.operations.platformops.heuristics.has_platform_definition_file')
    def test_raise_if_platform_definition_file_is_missing__is_missing(
            self,
            has_platform_definition_file_mock
    ):
        has_platform_definition_file_mock.return_value = False

        with self.assertRaises(platformops.PlatformWorkspaceEmptyError) as context_manager:
            platformops._raise_if_platform_definition_file_is_missing()

        self.assertEqual(
            "Unable to create platform version. Your workspace does not have a Platform Definition File, 'platform.yaml', in the root directory.",
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.platformops.heuristics.has_platform_definition_file')
    def test_raise_if_platform_definition_file_is_missing__is_present(
            self,
            has_platform_definition_file_mock
    ):
        has_platform_definition_file_mock.return_value = True

        platformops._raise_if_platform_definition_file_is_missing()

    def test_raise_if_version_format_is_invalid__invalid(self):
        with self.assertRaises(platformops.InvalidPlatformVersionError) as context_manager:
            platformops._raise_if_version_format_is_invalid('1.0.0.4')

        self.assertEqual(
            'Invalid version format. Only ARNs, version numbers, or platform_name/version formats are accepted.',
            str(context_manager.exception)
        )

    def test_raise_if_version_format_is_invalid__valid(self):
        platformops._raise_if_version_format_is_invalid('1.0.4')

    def test_resolve_version_label(self):
        source_control = mock.MagicMock()
        source_control.get_version_label.return_value = 'my-version-label'

        self.assertEqual('my-version-label', platformops._resolve_version_label(source_control, False))

    @mock.patch('ebcli.operations.platformops._datetime_now')
    def test_resolve_version_label__staged(
            self,
            _datetime_now_mock
    ):
        _datetime_now_mock.return_value = datetime.datetime(2018, 7, 19, 21, 50, 21, 623000)
        source_control = mock.MagicMock()
        source_control.get_version_label.return_value = 'my-version-label'

        self.assertEqual('my-version-label-stage-180719_215021', platformops._resolve_version_label(source_control, True))

    @mock.patch('ebcli.operations.platformops._generate_platform_yaml_copy')
    @mock.patch('ebcli.operations.platformops._enable_healthd')
    @mock.patch('ebcli.operations.platformops._create_app_version_zip_if_not_present_on_s3')
    @mock.patch('ebcli.operations.platformops.move')
    def test_resolve_s3_bucket_and_key(
            self,
            move_mock,
            _create_app_version_zip_if_not_present_on_s3_mock,
            _enable_healthd_mock,
            _generate_platform_yaml_copy_mock
    ):
        _generate_platform_yaml_copy_mock.return_value = 'platform_yaml_copy'
        _create_app_version_zip_if_not_present_on_s3_mock.return_value = ('s3_bucket', 's3_key', 'file_path')
        source_control_mock = mock.MagicMock()

        self.assertEqual(
            ('s3_bucket', 's3_key', 'file_path'),
            platformops._resolve_s3_bucket_and_key('my-custom-platform', 'my-version-label', source_control_mock, False)
        )

        _create_app_version_zip_if_not_present_on_s3_mock.assert_called_once_with(
            'my-custom-platform',
            'my-version-label',
            source_control_mock,
            False
        )
        move_mock.assert_called_once_with('platform_yaml_copy', 'platform.yaml')
        _enable_healthd_mock.assert_called_once_with()

    @mock.patch('ebcli.operations.platformops.tempfile.mkstemp')
    @mock.patch('ebcli.operations.platformops.copyfile')
    @mock.patch('ebcli.operations.platformops.os.close')
    def test_generate_platform_yaml_copy(
            self,
            close_mock,
            copyfile_mock,
            mkstemp_mock
    ):

        with open('some-random-file', 'w') as fd:
            mkstemp_mock.return_value = (fd, 'platform_yaml_copy')
            self.assertEqual(
                'platform_yaml_copy',
                platformops._generate_platform_yaml_copy()
            )

        copyfile_mock.assert_called_once_with('platform.yaml', 'platform_yaml_copy')
        close_mock.assert_called_once_with(fd)

    @mock.patch('ebcli.operations.platformops.get_app_version_s3_location')
    def test_create_app_version_zip_if_not_present_on_s3__app_version_already_on_s3(
            self,
            get_app_version_s3_location_mock
    ):
        get_app_version_s3_location_mock.return_value = ('s3_bucket', 's3_key')
        source_control_mock = mock.MagicMock()

        self.assertEqual(
            ('s3_bucket', 's3_key', None),
            platformops._create_app_version_zip_if_not_present_on_s3(
                'my-platform',
                'my-version-label',
                source_control_mock,
                False
            )
        )

    @mock.patch('ebcli.operations.platformops.get_app_version_s3_location')
    @mock.patch('ebcli.operations.platformops._zip_up_project')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.get_storage_location')
    def test_create_app_version_zip_if_not_present_on_s3__app_version_not_in_s3__zip_up_project_and_create_s3_location(
            self,
            get_storage_location_mock,
            _zip_up_project_mock,
            get_app_version_s3_location_mock
    ):
        get_app_version_s3_location_mock.return_value = (None, None)
        _zip_up_project_mock.return_value = ('file_name', 'file_path')
        get_storage_location_mock.return_value = 's3-bucket'
        source_control_mock = mock.MagicMock()

        self.assertEqual(
            ('s3-bucket', 'my-platform/file_name', 'file_path'),
            platformops._create_app_version_zip_if_not_present_on_s3(
                'my-platform',
                'my-version-label',
                source_control_mock,
                False
            )
        )
        _zip_up_project_mock.assert_called_once_with('my-version-label', source_control_mock, staged=False)

    @mock.patch('ebcli.operations.platformops.s3.get_object_info')
    @mock.patch('ebcli.operations.platformops.io.log_info')
    @mock.patch('ebcli.operations.platformops.fileoperations.delete_app_versions')
    def test_upload_platform_version_to_s3_if_necessary__app_version_already_present(
            self,
            delete_app_versions_mock,
            log_info_mock,
            get_object_info_mock
    ):
        get_object_info_mock.side_effect = None
        delete_app_versions_mock.side_effect = None

        platformops._upload_platform_version_to_s3_if_necessary('bucket', 'key', 'file_path')

        get_object_info_mock.assert_called_once_with('bucket', 'key')
        log_info_mock.assert_called_once_with('S3 Object already exists. Skipping upload.')
        delete_app_versions_mock.assert_called_once_with()

    @mock.patch('ebcli.operations.platformops.s3.get_object_info')
    @mock.patch('ebcli.operations.platformops.s3.upload_platform_version')
    @mock.patch('ebcli.operations.platformops.io.log_info')
    @mock.patch('ebcli.operations.platformops.fileoperations.delete_app_versions')
    def test_upload_platform_version_to_s3_if_necessary__app_version_needs_to_be_uploaded(
            self,
            delete_app_versions_mock,
            log_info_mock,
            upload_platform_version_mock,
            get_object_info_mock
    ):
        get_object_info_mock.side_effect = platformops.NotFoundError
        delete_app_versions_mock.side_effect = None

        platformops._upload_platform_version_to_s3_if_necessary('bucket', 'key', 'file_path')

        get_object_info_mock.assert_called_once_with('bucket', 'key')
        upload_platform_version_mock.assert_called_once_with('bucket', 'key', 'file_path')
        log_info_mock.assert_called_once_with('Uploading archive to s3 location: key')
        delete_app_versions_mock.assert_called_once_with()

    @mock.patch('ebcli.operations.platformops.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.platformops.logsops.io.get_event_streamer')
    @mock.patch('ebcli.operations.platformops.threading.Thread')
    @mock.patch('ebcli.operations.platformops.PackerStreamFormatter')
    def test_stream_platform_logs(
            self,
            PackerStreamFormatter_mock,
            Thread_mock,
            get_event_streamer_mock,
            wait_for_success_events_mock
    ):
        response = {
            'PlatformSummary': {
                'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
            },
            'ResponseMetadata': {
                'RequestId': 'my-request-id'
            }
        }
        streamer_mock = mock.MagicMock()
        get_event_streamer_mock.return_value = streamer_mock
        formatter_mock = mock.MagicMock()
        PackerStreamFormatter_mock.return_value = formatter_mock
        builder_events_thread_mock = mock.MagicMock()
        Thread_mock.return_value = builder_events_thread_mock

        platformops.stream_platform_logs(response, 'custom-platform-1', '2.0.0', None)

        Thread_mock.assert_called_once_with(
            args=('custom-platform-1', '2.0.0', streamer_mock, 5, None, formatter_mock),
            target=platformops.logsops.stream_platform_logs
        )
        builder_events_thread_mock.start.assert_called_once_with()
        self.assertTrue(builder_events_thread_mock.daemon)
        wait_for_success_events_mock.assert_called_once_with(
            'my-request-id',
            platform_arn='arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0',
            streamer=streamer_mock,
            timeout_in_minutes=30
        )

    @mock.patch('ebcli.operations.platformops.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.platformops.logsops.io.get_event_streamer')
    @mock.patch('ebcli.operations.platformops.threading.Thread')
    @mock.patch('ebcli.operations.platformops.PackerStreamFormatter')
    def test_stream_platform_logs__timeout_specified(
            self,
            PackerStreamFormatter_mock,
            Thread_mock,
            get_event_streamer_mock,
            wait_for_success_events_mock
    ):
        response = {
            'PlatformSummary': {
                'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
            },
            'ResponseMetadata': {
                'RequestId': 'my-request-id'
            }
        }
        streamer_mock = mock.MagicMock()
        get_event_streamer_mock.return_value = streamer_mock
        formatter_mock = mock.MagicMock()
        PackerStreamFormatter_mock.return_value = formatter_mock
        builder_events_thread_mock = mock.MagicMock()
        Thread_mock.return_value = builder_events_thread_mock

        platformops.stream_platform_logs(response, 'custom-platform-1', '2.0.0', 60)

        Thread_mock.assert_called_once_with(
            args=('custom-platform-1', '2.0.0', streamer_mock, 5, None, formatter_mock),
            target=platformops.logsops.stream_platform_logs
        )
        builder_events_thread_mock.start.assert_called_once_with()
        self.assertTrue(builder_events_thread_mock.daemon)
        wait_for_success_events_mock.assert_called_once_with(
            'my-request-id',
            platform_arn='arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0',
            streamer=streamer_mock,
            timeout_in_minutes=60
        )

    @mock.patch('ebcli.operations.platformops.commonops.get_config_setting_from_branch_or_default')
    def test_get_configured_default_platform(
        self,
        get_config_setting_from_branch_or_default_mock,
    ):
        get_config_setting_from_branch_or_default_mock.return_value = 'PHP 7.3'

        result = platformops.get_configured_default_platform()

        get_config_setting_from_branch_or_default_mock.assert_called_once_with('default_platform')
        self.assertEqual('PHP 7.3', result)

    @mock.patch('ebcli.operations.platformops.PlatformVersion.is_valid_arn')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.describe_platform_version')
    @mock.patch('ebcli.operations.platformops.is_platform_branch_name')
    @mock.patch('ebcli.operations.platformops.get_preferred_platform_version_for_branch')
    @mock.patch('ebcli.operations.platformops.solution_stack_ops.find_solution_stack_from_string')
    def test_get_platform_version_for_platform_string__given_arn(
        self,
        find_solution_stack_from_string_mock,
        get_preferred_platform_version_for_branch_mock,
        is_platform_branch_name_mock,
        describe_platform_version_mock,
        is_valid_arn_mock,
    ):
        platform_string = 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/2.9.2'
        is_valid_arn_mock.return_value = True
        describe_platform_version_mock.return_value = { 'PlatformBranchLifecycleState': 'Supported' }

        result = platformops.get_platform_version_for_platform_string(platform_string)

        is_valid_arn_mock.assert_called_once_with(platform_string)
        describe_platform_version_mock.assert_called_once_with(platform_string)
        is_platform_branch_name_mock.assert_not_called()
        get_preferred_platform_version_for_branch_mock.assert_not_called()
        find_solution_stack_from_string_mock.assert_not_called()
        self.assertIsInstance(result, PlatformVersion)
        self.assertEqual(platform_string, result.platform_arn)
        self.assertEqual('Supported', result.platform_branch_lifecycle_state)

    @mock.patch('ebcli.operations.platformops.PlatformVersion.is_valid_arn')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.describe_platform_version')
    @mock.patch('ebcli.operations.platformops.is_platform_branch_name')
    @mock.patch('ebcli.operations.platformops.get_preferred_platform_version_for_branch')
    @mock.patch('ebcli.operations.platformops.solution_stack_ops.find_solution_stack_from_string')
    def test_get_platform_version_for_platform_string__given_branch_name(
        self,
        find_solution_stack_from_string_mock,
        get_preferred_platform_version_for_branch_mock,
        is_platform_branch_name_mock,
        describe_platform_version_mock,
        is_valid_arn_mock,
    ):
        platform_string = 'PHP 7.1 running on 64bit Amazon Linux'
        platform_version = PlatformVersion(
            'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/2.9.2')
        is_valid_arn_mock.return_value = False
        is_platform_branch_name_mock.return_value = True
        get_preferred_platform_version_for_branch_mock.return_value = platform_version

        result = platformops.get_platform_version_for_platform_string(platform_string)

        is_valid_arn_mock.assert_called_once_with(platform_string)
        describe_platform_version_mock.assert_not_called()
        is_platform_branch_name_mock.assert_called_once_with(platform_string)
        get_preferred_platform_version_for_branch_mock.assert_called_with(platform_string)
        find_solution_stack_from_string_mock.assert_not_called()
        self.assertIsInstance(result, PlatformVersion)
        self.assertIs(platform_version, result)

    @mock.patch('ebcli.operations.platformops.PlatformVersion.is_valid_arn')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.describe_platform_version')
    @mock.patch('ebcli.operations.platformops.is_platform_branch_name')
    @mock.patch('ebcli.operations.platformops.get_preferred_platform_version_for_branch')
    @mock.patch('ebcli.operations.platformops.solution_stack_ops.find_solution_stack_from_string')
    def test_get_platform_version_for_platform_string__given_solution_stack_string(
        self,
        find_solution_stack_from_string_mock,
        get_preferred_platform_version_for_branch_mock,
        is_platform_branch_name_mock,
        describe_platform_version_mock,
        is_valid_arn_mock,
    ):
        platform_string = 'PHP 7.1'
        solution_stack = SolutionStack(platform_string)
        is_valid_arn_mock.return_value = False
        is_platform_branch_name_mock.return_value = False
        find_solution_stack_from_string_mock.return_value = solution_stack

        result = platformops.get_platform_version_for_platform_string(platform_string)

        is_valid_arn_mock.assert_called_once_with(platform_string)
        describe_platform_version_mock.assert_not_called()
        is_platform_branch_name_mock.assert_called_once_with(platform_string)
        get_preferred_platform_version_for_branch_mock.assert_not_called()
        find_solution_stack_from_string_mock.assert_called_once_with(platform_string)
        self.assertIsInstance(result, SolutionStack)
        self.assertIs(solution_stack, result)

    @mock.patch('ebcli.operations.platformops.get_platform_versions_for_branch')
    def test_preferred_platform_version_for_branch(
        self,
        get_platform_versions_for_branch_mock,
    ):
        branch_name = 'PHP 7.1 running on 64bit Amazon Linux'
        platform_versions = [
            PlatformVersion(
                platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.3.1',
            ),
            PlatformVersion(
                platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.2.1',
                platform_lifecycle_state='Recommended'
            ),
            PlatformVersion(
                platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.1.1',
            ),
            PlatformVersion(
                platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.3',
            ),
        ]
        get_platform_versions_for_branch_mock.return_value = platform_versions

        result = platformops.get_preferred_platform_version_for_branch(branch_name)

        get_platform_versions_for_branch_mock.assert_called_once_with(branch_name)
        self.assertEqual('0.2.1', result.platform_version)
        self.assertIs(platform_versions[1], result)

    @mock.patch('ebcli.operations.platformops.get_platform_versions_for_branch')
    def test_preferred_platform_version_for_branch__no_recommended(
        self,
        get_platform_versions_for_branch_mock,
    ):
        branch_name = 'PHP 7.1 running on 64bit Amazon Linux'
        platform_versions = [
            PlatformVersion(
                platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.1',
            ),
            PlatformVersion(
                platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.2.1',
            ),
            PlatformVersion(
                platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.1.1',
            ),
            PlatformVersion(
                platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.3',
            ),
        ]
        get_platform_versions_for_branch_mock.return_value = platform_versions

        result = platformops.get_preferred_platform_version_for_branch(branch_name)

        get_platform_versions_for_branch_mock.assert_called_once_with(branch_name)
        self.assertEqual('0.2.1', result.platform_version)
        self.assertIs(platform_versions[1], result)

    @mock.patch('ebcli.operations.platformops.get_platform_versions_for_branch')
    def test_preferred_platform_version_for_branch__multiple_recommended(
        self,
        get_platform_versions_for_branch_mock,
    ):
        branch_name = 'PHP 7.1 running on 64bit Amazon Linux'
        platform_versions = [
            PlatformVersion(
                platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.3.1',
            ),
            PlatformVersion(
                platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.2.1',
                platform_lifecycle_state='Recommended',
            ),
            PlatformVersion(
                platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.1.1',
                platform_lifecycle_state='Recommended',
            ),
            PlatformVersion(
                platform_arn='arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.3',
            ),
        ]
        get_platform_versions_for_branch_mock.return_value = platform_versions

        result = platformops.get_preferred_platform_version_for_branch(branch_name)

        get_platform_versions_for_branch_mock.assert_called_once_with(branch_name)
        self.assertEqual('0.2.1', result.platform_version)
        self.assertIs(platform_versions[1], result)

    @mock.patch('ebcli.operations.platformops.get_platform_versions_for_branch')
    def test_preferred_platform_version_for_branch__none_found(
        self,
        get_platform_versions_for_branch_mock,
    ):
        branch_name = 'PHP 7.1 running on 64bit Amazon Linux'
        platform_versions = []
        get_platform_versions_for_branch_mock.return_value = platform_versions

        self.assertRaises(
            NotFoundError,
            platformops.get_preferred_platform_version_for_branch,
            branch_name,
        )

    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.list_platform_versions')
    def test_get_platform_versions_for_branch(
        self,
        list_platform_versions_mock
    ):
        branch_name = 'PHP 7.1 running on 64bit Amazon Linux'
        list_results = [
            { 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.1' },
            { 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.2.1' },
            { 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.4' },
        ]
        list_platform_versions_mock.return_value = list_results
        expected_filters = [
            {
                'Type': 'PlatformBranchName',
                'Operator': '=',
                'Values': [branch_name],
            }
        ]

        result = platformops.get_platform_versions_for_branch(branch_name)

        list_platform_versions_mock.assert_called_once_with(filters=expected_filters)
        self.assertEqual(
            PlatformVersion.from_platform_version_summary(list_results[0]),
            result[0],
        )
        self.assertEqual(
            PlatformVersion.from_platform_version_summary(list_results[1]),
            result[1],
        )
        self.assertEqual(
            PlatformVersion.from_platform_version_summary(list_results[2]),
            result[2],
        )

    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.list_platform_versions')
    def test_get_platform_versions_for_branch__recommended_only(
        self,
        list_platform_versions_mock
    ):
        branch_name = 'PHP 7.1 running on 64bit Amazon Linux'
        list_results = [
            { 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.1' },
            { 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.2.1' },
            { 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.4' },
        ]
        list_platform_versions_mock.return_value = list_results
        expected_filters = [
            {
                'Type': 'PlatformBranchName',
                'Operator': '=',
                'Values': [branch_name],
            },
            {
                'Type': 'PlatformLifecycleState',
                'Operator': '=',
                'Values': ['Recommended'],
            }
        ]

        result = platformops.get_platform_versions_for_branch(branch_name, recommended_only=True)

        list_platform_versions_mock.assert_called_once_with(filters=expected_filters)
        self.assertEqual(
            PlatformVersion.from_platform_version_summary(list_results[0]),
            result[0],
        )
        self.assertEqual(
            PlatformVersion.from_platform_version_summary(list_results[1]),
            result[1],
        )
        self.assertEqual(
            PlatformVersion.from_platform_version_summary(list_results[2]),
            result[2],
        )

    @mock.patch('ebcli.operations.platformops.PlatformVersion.is_valid_arn')
    @mock.patch('ebcli.operations.platformops.get_platform_branch_by_name')
    def test_is_platform_branch_name__with_branch_name(
        self,
        get_platform_branch_by_name_mock,
        is_valid_arn_mock,
    ):
        branch_name = 'PHP 7.1 running on 64bit Amazon Linux'
        is_valid_arn_mock.return_value = False
        get_platform_branch_by_name_mock.return_value = {
            'BranchName': branch_name
        }

        result = platformops.is_platform_branch_name(branch_name)

        is_valid_arn_mock.assert_called_once_with(branch_name)
        get_platform_branch_by_name_mock.assert_called_once_with(branch_name)
        self.assertTrue(result)

    @mock.patch('ebcli.operations.platformops.PlatformVersion.is_valid_arn')
    @mock.patch('ebcli.operations.platformops.get_platform_branch_by_name')
    def test_is_platform_branch_name__with_arn(
        self,
        get_platform_branch_by_name_mock,
        is_valid_arn_mock,
    ):
        branch_name = 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.1'
        is_valid_arn_mock.return_value = True

        result = platformops.is_platform_branch_name(branch_name)

        is_valid_arn_mock.assert_called_once_with(branch_name)
        get_platform_branch_by_name_mock.assert_not_called()
        self.assertFalse(result)

    @mock.patch('ebcli.operations.platformops.PlatformVersion.is_valid_arn')
    @mock.patch('ebcli.operations.platformops.get_platform_branch_by_name')
    def test_is_platform_branch_name__with_non_branch_name(
        self,
        get_platform_branch_by_name_mock,
        is_valid_arn_mock,
    ):
        branch_name = 'PHP 7.1'
        is_valid_arn_mock.return_value = False
        get_platform_branch_by_name_mock.return_value = None

        result = platformops.is_platform_branch_name(branch_name)

        is_valid_arn_mock.assert_called_once_with(branch_name)
        get_platform_branch_by_name_mock.assert_called_once_with(branch_name)
        self.assertFalse(result)

    @mock.patch('ebcli.operations.platformops._resolve_conflicting_platform_branches')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.list_platform_branches')
    def test_get_platform_branch_by_name(
        self,
        list_platform_branches_mock,
        _resolve_conflicting_platform_branches_mock,
    ):
        branch_name = 'PHP 7.1 running on 64bit Amazon Linux'
        list_results = [
            { 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.1' },
            # { 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.2.1' },
            # { 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.4' },
        ]

        list_platform_branches_mock.return_value = list_results

        expected_filters = [
            {
                'Attribute': 'BranchName',
                'Operator': '=',
                'Values': [branch_name],
            }
        ]

        result = platformops.get_platform_branch_by_name(branch_name)

        list_platform_branches_mock.assert_called_once_with(filters=expected_filters)
        _resolve_conflicting_platform_branches_mock.assert_not_called()
        self.assertEqual(list_results[0], result)

    @mock.patch('ebcli.operations.platformops._resolve_conflicting_platform_branches')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.list_platform_branches')
    def test_get_platform_branch_by_name__multiple_results(
        self,
        list_platform_branches_mock,
        _resolve_conflicting_platform_branches_mock,
    ):
        branch_name = 'PHP 7.1 running on 64bit Amazon Linux'
        list_results = [
            { 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.1' },
            { 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.2.1' },
            { 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.1 running on 64bit Amazon Linux/0.0.4' },
        ]

        list_platform_branches_mock.return_value = list_results
        _resolve_conflicting_platform_branches_mock.return_value = list_results[1]

        expected_filters = [
            {
                'Attribute': 'BranchName',
                'Operator': '=',
                'Values': [branch_name],
            }
        ]

        result = platformops.get_platform_branch_by_name(branch_name)

        list_platform_branches_mock.assert_called_once_with(filters=expected_filters)
        _resolve_conflicting_platform_branches_mock.assert_called_once_with(list_results)
        self.assertEqual(list_results[1], result)

    @mock.patch('ebcli.operations.platformops._resolve_conflicting_platform_branches')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.list_platform_branches')
    def test_get_platform_branch_by_name__no_results(
        self,
        list_platform_branches_mock,
        _resolve_conflicting_platform_branches_mock,
    ):
        branch_name = 'PHP 7.1 running on 64bit Amazon Linux'
        list_results = []

        list_platform_branches_mock.return_value = list_results

        expected_filters = [
            {
                'Attribute': 'BranchName',
                'Operator': '=',
                'Values': [branch_name],
            }
        ]

        result = platformops.get_platform_branch_by_name(branch_name)

        list_platform_branches_mock.assert_called_once_with(filters=expected_filters)
        _resolve_conflicting_platform_branches_mock.assert_not_called()
        self.assertEqual(None, result)

    def test__resolve_conflicting_platform_branches(self):
        branches = [
            {
                'BranchName': 'PHP 7.1',
                'LifecycleState': 'Deprecated',
            },
            {
                'BranchName': 'PHP 7.3',
                'LifecycleState': 'Supported',
            },
            {
                'BranchName': 'PHP 7.2',
                'LifecycleState': 'Deprecated',
            },
        ]
        expected = branches[1]

        result = platformops._resolve_conflicting_platform_branches(branches)

        self.assertEqual(expected, result)


class TestPackerStreamMessage(unittest.TestCase):
    def test_raw_message__match_found(self):
        event_message = u'I, [2017-11-21T19:13:21.560213+0000#29667]  ' \
                        u'INFO -- Packer: 1511291601,,ui,message,    '  \
                        u'HVM AMI builder: + install_eb_gems https://some-s3-gem-path' \
                        u'https://some-other-s3-gem-path' \
                        u'https://yet-s3-gem-path'

        expected_raw_message = u'Packer: 1511291601,,ui,message,    '  \
                                u'HVM AMI builder: + install_eb_gems https://some-s3-gem-path' \
                                u'https://some-other-s3-gem-path' \
                                u'https://yet-s3-gem-path'

        packet_stream_message = platformops.PackerStreamMessage(event_message)

        self.assertEqual(expected_raw_message, packet_stream_message.raw_message())

    def test_raw_message__match_not_found(self):
        event_message = u'I, [2017-11-21T19:13:21.560213+0000#29667]  ' \
                        u'INFO Packer: 1511291601,,ui,message,    ' \
                        u'HVM AMI builder: + install_eb_gems https://some-s3-gem-path' \
                        u'https://some-other-s3-gem-path' \
                        u'https://yet-s3-gem-path'

        packet_stream_message = platformops.PackerStreamMessage(event_message)

        self.assertIsNone(packet_stream_message.raw_message())

    def test_message_severity__INFO(self):
        event_message = u'I, [2017-11-21T19:13:21.561685+0000#29667]  INFO -- info'

        packet_stream_message = platformops.PackerStreamMessage(event_message)

        self.assertEqual('INFO', packet_stream_message.message_severity())

    def test_message_severity__ERROR(self):
        event_message = u'I, [2017-11-21T19:13:21.561685+0000#29667]  ERROR -- error'

        packet_stream_message = platformops.PackerStreamMessage(event_message)

        self.assertEqual('ERROR', packet_stream_message.message_severity())

    def test_message_severity__WARN(self):
        event_message = u'I, [2017-11-21T19:13:21.561685+0000#29667]  WARN -- warning'

        packet_stream_message = platformops.PackerStreamMessage(event_message)

        self.assertEqual('WARN', packet_stream_message.message_severity())

    def test_message_severity__not_present(self):
        event_message = u'I, [2017-11-21T19:13:21.561685+0000#29667]'

        packet_stream_message = platformops.PackerStreamMessage(event_message)

        self.assertIsNone(packet_stream_message.message_severity())

    def test_ui_message(self):
        event_message = u'I, [2017-11-21T19:13:26.119871+0000#29667]  ' \
                        u'INFO -- Packer: 1511291606,,ui,message,    ' \
                        u'HVM AMI builder: \x1b[K    100% |' \
                        u'\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588' \
                        u'\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588' \
                        u'\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588' \
                        u'\u2588\u2588| 51kB 3.2MB/s'

        expected_ui_message = u'HVM AMI builder: \x1b[K    100% |' \
                              u'\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588' \
                              u'\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588' \
                              u'\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588' \
                              u'\u2588\u2588| 51kB 3.2MB/s'

        packet_stream_message = platformops.PackerStreamMessage(event_message)

        self.assertEqual(
            expected_ui_message,
            packet_stream_message.ui_message()
        )

    def test_other_packer_message(self):
        event_message = u'I, [2017-11-21T19:13:26.119871+0000#29667]  ' \
                        u'INFO -- Packer: 1511291606,\u2588\u2588\u2588, MESSAGE TARGET'

        expected_ui_message = u'\u2588\u2588\u2588'

        packet_stream_message = platformops.PackerStreamMessage(event_message)

        self.assertEqual(
            expected_ui_message,
            packet_stream_message.other_packer_message()
        )

    def test_other_packer_message_target(self):
        event_message = u'I, [2017-11-21T19:13:26.119871+0000#29667]  ' \
                        u'INFO -- Packer: 1511291606,\u2588\u2588\u2588, MESSAGE TARGET'

        packet_stream_message = platformops.PackerStreamMessage(event_message)

        self.assertEqual(
            'MESSAGE TARGET',
            packet_stream_message.other_packer_message_target()
        )

    def test_other_message(self):
        event_message = u'I, [2017-11-21T19:13:26.119871+0000#29667]  ' \
                        u'INFO -- aws: \u2588my:message'

        packet_stream_message = platformops.PackerStreamMessage(event_message)

        self.assertEqual(
            u'\u2588my:message',
            packet_stream_message.other_message()
        )


class TestPackerStreamFormatter(unittest.TestCase):
    def test_message_is_not_a_packet_stream_message(self):
        packet_stream_formatter = platformops.PackerStreamFormatter()

        self.assertEqual(
            'Custom Stream hello, world',
            packet_stream_formatter.format('hello, world', 'Custom Stream')
        )

    def test_message_is_a_packet_stream_message__ui_message(self):
        packet_stream_formatter = platformops.PackerStreamFormatter()
        event_message = u'I, [2017-11-21T19:13:26.119871+0000#29667]  ' \
                        u'INFO -- Packer: 1511291606,,ui,message,    ' \
                        u'HVM AMI builder: \x1b[K    100% |' \
                        u'\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588' \
                        u'\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588' \
                        u'\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588' \
                        u'\u2588\u2588| 51kB 3.2MB/s'

        expected_formatted_message = u'HVM AMI builder: \x1b[K    100% |' \
                              u'\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588' \
                              u'\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588' \
                              u'\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588' \
                              u'\u2588\u2588| 51kB 3.2MB/s'

        self.assertEqual(
            expected_formatted_message,
            packet_stream_formatter.format(event_message, 'Custom Stream')
        )

    def test_other_packer_message(self):
        event_message = u'I, [2017-11-21T19:13:26.119871+0000#29667]  ' \
                        u'INFO -- Packer: 1511291606,\u2588\u2588\u2588, MESSAGE TARGET'

        expected_formatted_message = u'MESSAGE TARGET:\u2588\u2588\u2588'

        packet_stream_formatter = platformops.PackerStreamFormatter()

        self.assertEqual(
            expected_formatted_message,
            packet_stream_formatter.format(event_message, 'Custom Stream')
        )

    def test_other_message(self):
        event_message = u'I, [2017-11-21T19:13:26.119871+0000#29667]  ' \
                        u'INFO -- aws: \u2588my:message'

        packet_stream_formatter = platformops.PackerStreamFormatter()

        self.assertEqual(
            u'\u2588my:message',
            packet_stream_formatter.format(event_message, 'Custom Stream')
        )
