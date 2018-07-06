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
import os
import shutil

import mock
from pytest_socket import disable_socket, enable_socket
import unittest


from ebcli.operations import platformops
from ebcli.objects.exceptions import ValidationError
from ebcli.objects.environment import Environment
from ebcli.objects.platform import PlatformVersion


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
        disable_socket()
        # set up test directory
        if not os.path.exists('testDir'):
            os.makedirs('testDir')
        os.chdir('testDir')

        self.platform_name = 'test-platform'
        self.platform_version = '1.0.0'
        self.platform_arn = 'arn:aws:elasticbeanstalk:us-east-1:647823116501:platform/{0}/{1}'.format(
                self.platform_name,
                self.platform_version)

    def tearDown(self):
        enable_socket()
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
                Environment(name='no match', platform=PlatformVersion('arn:aws:elasticbeanstalk:us-east-1:647823116501:platform/foo/2.0.0')),
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

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_instance_profile')
    @mock.patch('ebcli.operations.platformops.commonops.get_default_keyname')
    def test_create_platform_version__invalid_version(
            self,
            get_default_keyname_mock,
            get_instance_profile_mock,
            get_platform_name_mock
    ):
        get_default_keyname_mock.return_value = 'aws-eb-us-west-2'
        get_instance_profile_mock.return_value = 'default'
        get_platform_name_mock.return_value = 'custom-platform-1'

        with self.assertRaises(platformops.InvalidPlatformVersionError) as context_manager:
            platformops.create_platform_version('1.0.0.5', False, False, True, 't2.micro')
        self.assertEqual(
            'Invalid version format. Only ARNs, version numbers, or platform_name/version formats are accepted.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.platformops.fileoperations._traverse_to_project_root')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_instance_profile')
    @mock.patch('ebcli.operations.platformops.commonops.get_default_keyname')
    @mock.patch('ebcli.operations.platformops.heuristics.has_platform_definition_file')
    def test_create_platform_version__platform_definition_file_absent(
            self,
            has_platform_definition_file_mock,
            get_default_keyname_mock,
            get_instance_profile_mock,
            get_platform_name_mock,
            _traverse_to_project_root_mock
    ):
        has_platform_definition_file_mock.return_value = False
        get_default_keyname_mock.return_value = 'aws-eb-us-west-2'
        get_instance_profile_mock.return_value = 'default'
        get_platform_name_mock.return_value = 'custom-platform-1'

        with self.assertRaises(platformops.PlatformWorkspaceEmptyError) as context_manager:
            platformops.create_platform_version('1.0.0', False, False, True, 't2.micro')
        self.assertEqual(
            'The current directory does not contain any Platform configuration files. Unable to create new Platform.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.update_platform_version')
    @mock.patch('ebcli.operations.platformops.fileoperations.delete_app_versions')
    @mock.patch('ebcli.operations.platformops.fileoperations._traverse_to_project_root')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_instance_profile')
    @mock.patch('ebcli.operations.platformops.commonops.get_default_keyname')
    @mock.patch('ebcli.operations.platformops.commonops.set_environment_for_current_branch')
    @mock.patch('ebcli.operations.platformops.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.platformops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.platformops.heuristics.has_platform_definition_file')
    @mock.patch('ebcli.operations.platformops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.platformops.copyfile')
    @mock.patch('ebcli.operations.platformops.move')
    @mock.patch('ebcli.operations.platformops._enable_healthd')
    @mock.patch('ebcli.operations.platformops.get_app_version_s3_location')
    @mock.patch('ebcli.operations.platformops._zip_up_project')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.get_storage_location')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.create_platform_version')
    @mock.patch('ebcli.operations.platformops.s3.get_object_info')
    @mock.patch('ebcli.operations.platformops.io.get_event_streamer')
    @mock.patch('ebcli.operations.platformops.logsops.stream_platform_logs')
    @mock.patch('ebcli.operations.platformops.PackerStreamFormatter')
    def test_create_platform_version__app_version_already_exists_on_s3(
            self,
            packer_stream_formatter_mock,
            stream_platform_logs_mock,
            get_event_streamer_mock,
            get_object_info_mock,
            create_platform_version_mock,
            get_storage_location_mock,
            _zip_up_project_mock,
            get_app_version_s3_location_mock,
            _enable_healthd_mock,
            move_mock,
            copyfile_mock,
            get_source_control_mock,
            has_platform_definition_file_mock,
            directory_is_empty_mock,
            wait_for_success_events_mock,
            set_environment_for_current_branch_mock,
            get_default_keyname_mock,
            get_instance_profile_mock,
            get_platform_name_mock,
            _traverse_to_project_root_mock,
            delete_app_versions_mock,
            update_platform_version_mock
    ):
        packer_stream_formatter_instance_mock = mock.MagicMock()
        packer_stream_formatter_mock.return_value = packer_stream_formatter_instance_mock
        get_storage_location_mock.return_value = 's3-bucket'
        has_platform_definition_file_mock.return_value = True
        directory_is_empty_mock.return_value = False
        get_default_keyname_mock.return_value = 'aws-eb-us-west-2'
        get_instance_profile_mock.return_value = 'default'
        get_platform_name_mock.return_value = 'custom-platform-1'
        get_source_control_mock.untracked_changes_exist = mock.MagicMock(return_value=False)
        get_source_control_mock.get_version_label = mock.MagicMock(return_value='my-version-label')
        get_app_version_s3_location_mock.return_value = ['s3-bucket', 's3-key']
        create_platform_version_mock.return_value = {
            'PlatformSummary': {
                'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
            },
            'ResponseMetadata': {
                'RequestId': 'my-request-id'
            }
        }
        streamer_mock = mock.MagicMock()
        get_event_streamer_mock.return_value = streamer_mock

        platformops.create_platform_version('1.0.0', False, False, False, 't2.micro')

        get_object_info_mock.assert_called_once_with('s3-bucket', 's3-key')
        create_platform_version_mock.assert_called_once_with(
            'custom-platform-1',
            '1.0.0',
            's3-bucket',
            's3-key',
            'default',
            'aws-eb-us-west-2',
            't2.micro',
            None
        )
        update_platform_version_mock.assert_called_once_with('1.0.0')
        set_environment_for_current_branch_mock.assert_called_once_with(
            'eb-custom-platform-builder-packer'
        )
        get_event_streamer_mock.assert_called_once()
        stream_platform_logs_mock.assert_called_once_with(
            'custom-platform-1',
            '1.0.0',
            streamer_mock,
            5,
            None,
            packer_stream_formatter_instance_mock
        )
        wait_for_success_events_mock.assert_called_once_with(
            'my-request-id',
            platform_arn='arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0',
            streamer=streamer_mock,
            timeout_in_minutes=30
        )
        _enable_healthd_mock.assert_called_once()

        _zip_up_project_mock.assert_not_called()

    @mock.patch('ebcli.operations.platformops.fileoperations.update_platform_version')
    @mock.patch('ebcli.operations.platformops.fileoperations.delete_app_versions')
    @mock.patch('ebcli.operations.platformops.fileoperations._traverse_to_project_root')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_instance_profile')
    @mock.patch('ebcli.operations.platformops.commonops.get_default_keyname')
    @mock.patch('ebcli.operations.platformops.commonops.set_environment_for_current_branch')
    @mock.patch('ebcli.operations.platformops.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.platformops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.platformops.heuristics.has_platform_definition_file')
    @mock.patch('ebcli.operations.platformops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.platformops.copyfile')
    @mock.patch('ebcli.operations.platformops.move')
    @mock.patch('ebcli.operations.platformops._enable_healthd')
    @mock.patch('ebcli.operations.platformops.get_app_version_s3_location')
    @mock.patch('ebcli.operations.platformops._zip_up_project')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.get_storage_location')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.create_platform_version')
    @mock.patch('ebcli.operations.platformops.s3.get_object_info')
    @mock.patch('ebcli.operations.platformops.io.get_event_streamer')
    @mock.patch('ebcli.operations.platformops.logsops.stream_platform_logs')
    @mock.patch('ebcli.operations.platformops.PackerStreamFormatter')
    def test_create_platform_version__app_version_needs_to_be_created(
            self,
            packer_stream_formatter_mock,
            stream_platform_logs_mock,
            get_event_streamer_mock,
            get_object_info_mock,
            create_platform_version_mock,
            get_storage_location_mock,
            _zip_up_project_mock,
            get_app_version_s3_location_mock,
            _enable_healthd_mock,
            move_mock,
            copyfile_mock,
            get_source_control_mock,
            has_platform_definition_file_mock,
            directory_is_empty_mock,
            wait_for_success_events_mock,
            set_environment_for_current_branch_mock,
            get_default_keyname_mock,
            get_instance_profile_mock,
            get_platform_name_mock,
            _traverse_to_project_root_mock,
            delete_app_versions_mock,
            update_platform_version_mock
    ):
        packer_stream_formatter_instance_mock = mock.MagicMock()
        packer_stream_formatter_mock.return_value = packer_stream_formatter_instance_mock
        get_storage_location_mock.return_value = 's3-bucket'
        has_platform_definition_file_mock.return_value = True
        directory_is_empty_mock.return_value = False
        get_default_keyname_mock.return_value = 'aws-eb-us-west-2'
        get_instance_profile_mock.return_value = 'default'
        get_platform_name_mock.return_value = 'custom-platform-1'
        source_control_mock = mock.MagicMock()
        source_control_mock.untracked_changes_exist = mock.MagicMock(return_value=False)
        version_label_mock = mock.MagicMock(return_value='my-version-label')
        source_control_mock.get_version_label = version_label_mock
        get_source_control_mock.return_value = source_control_mock
        get_app_version_s3_location_mock.return_value = [None, None]
        _zip_up_project_mock.return_value = ['s3-file-name', 's3-path']
        create_platform_version_mock.return_value = {
            'PlatformSummary': {
                'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
            },
            'ResponseMetadata': {
                'RequestId': 'my-request-id'
            }
        }
        streamer_mock = mock.MagicMock()
        get_event_streamer_mock.return_value = streamer_mock

        platformops.create_platform_version('1.0.0', False, False, False, 't2.micro')

        get_object_info_mock.assert_called_once_with('s3-bucket', 'custom-platform-1/s3-file-name')
        create_platform_version_mock.assert_called_once_with(
            'custom-platform-1',
            '1.0.0',
            's3-bucket',
            'custom-platform-1/s3-file-name',
            'default',
            'aws-eb-us-west-2',
            't2.micro',
            None
        )
        update_platform_version_mock.assert_called_once_with('1.0.0')
        set_environment_for_current_branch_mock.assert_called_once_with(
            'eb-custom-platform-builder-packer'
        )
        get_event_streamer_mock.assert_called_once()
        stream_platform_logs_mock.assert_called_once_with(
            'custom-platform-1',
            '1.0.0',
            streamer_mock,
            5,
            None,
            packer_stream_formatter_instance_mock
        )
        wait_for_success_events_mock.assert_called_once_with(
            'my-request-id',
            platform_arn='arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0',
            streamer=streamer_mock,
            timeout_in_minutes=30
        )
        _enable_healthd_mock.assert_called_once()
        _zip_up_project_mock.assert_called_once_with(
            'my-version-label',
            source_control_mock,
            staged=False
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.update_platform_version')
    @mock.patch('ebcli.operations.platformops.fileoperations.delete_app_versions')
    @mock.patch('ebcli.operations.platformops.fileoperations._traverse_to_project_root')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_instance_profile')
    @mock.patch('ebcli.operations.platformops.commonops.get_default_keyname')
    @mock.patch('ebcli.operations.platformops.commonops.set_environment_for_current_branch')
    @mock.patch('ebcli.operations.platformops.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.platformops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.platformops.heuristics.has_platform_definition_file')
    @mock.patch('ebcli.operations.platformops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.platformops.copyfile')
    @mock.patch('ebcli.operations.platformops.move')
    @mock.patch('ebcli.operations.platformops._get_latest_version')
    @mock.patch('ebcli.operations.platformops._enable_healthd')
    @mock.patch('ebcli.operations.platformops.get_app_version_s3_location')
    @mock.patch('ebcli.operations.platformops._zip_up_project')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.get_storage_location')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.create_platform_version')
    @mock.patch('ebcli.operations.platformops.s3.get_object_info')
    @mock.patch('ebcli.operations.platformops.io.get_event_streamer')
    @mock.patch('ebcli.operations.platformops.logsops.stream_platform_logs')
    @mock.patch('ebcli.operations.platformops.PackerStreamFormatter')
    def test_create_platform_version__update_major_version(
            self,
            packer_stream_formatter_mock,
            stream_platform_logs_mock,
            get_event_streamer_mock,
            get_object_info_mock,
            create_platform_version_mock,
            get_storage_location_mock,
            _zip_up_project_mock,
            get_app_version_s3_location_mock,
            _enable_healthd_mock,
            _get_latest_version_mock,
            move_mock,
            copyfile_mock,
            get_source_control_mock,
            has_platform_definition_file_mock,
            directory_is_empty_mock,
            wait_for_success_events_mock,
            set_environment_for_current_branch_mock,
            get_default_keyname_mock,
            get_instance_profile_mock,
            get_platform_name_mock,
            _traverse_to_project_root_mock,
            delete_app_versions_mock,
            update_platform_version_mock
    ):
        packer_stream_formatter_instance_mock = mock.MagicMock()
        packer_stream_formatter_mock.return_value = packer_stream_formatter_instance_mock
        get_storage_location_mock.return_value = 's3-bucket'
        has_platform_definition_file_mock.return_value = True
        directory_is_empty_mock.return_value = False
        get_default_keyname_mock.return_value = 'aws-eb-us-west-2'
        get_instance_profile_mock.return_value = 'default'
        get_platform_name_mock.return_value = 'custom-platform-1'
        get_source_control_mock.untracked_changes_exist = mock.MagicMock(return_value=False)
        get_source_control_mock.get_version_label = mock.MagicMock(return_value='my-version-label')
        get_app_version_s3_location_mock.return_value = ['s3-bucket', 's3-key']
        create_platform_version_mock.return_value = {
            'PlatformSummary': {
                'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
            },
            'ResponseMetadata': {
                'RequestId': 'my-request-id'
            }
        }
        _get_latest_version_mock.return_value = '1.0.0'
        streamer_mock = mock.MagicMock()
        get_event_streamer_mock.return_value = streamer_mock

        platformops.create_platform_version(None, True, False, False, 't2.micro')

        get_object_info_mock.assert_called_once_with('s3-bucket', 's3-key')
        create_platform_version_mock.assert_called_once_with(
            'custom-platform-1',
            '2.0.0',
            's3-bucket',
            's3-key',
            'default',
            'aws-eb-us-west-2',
            't2.micro',
            None
        )
        update_platform_version_mock.assert_called_once_with('2.0.0')
        set_environment_for_current_branch_mock.assert_called_once_with(
            'eb-custom-platform-builder-packer'
        )
        get_event_streamer_mock.assert_called_once()
        stream_platform_logs_mock.assert_called_once_with(
            'custom-platform-1',
            '2.0.0',
            streamer_mock,
            5,
            None,
            packer_stream_formatter_instance_mock
        )
        wait_for_success_events_mock.assert_called_once_with(
            'my-request-id',
            platform_arn='arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0',
            streamer=streamer_mock,
            timeout_in_minutes=30
        )
        _enable_healthd_mock.assert_called_once()

        _zip_up_project_mock.assert_not_called()

    @mock.patch('ebcli.operations.platformops.fileoperations.update_platform_version')
    @mock.patch('ebcli.operations.platformops.fileoperations.delete_app_versions')
    @mock.patch('ebcli.operations.platformops.fileoperations._traverse_to_project_root')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_instance_profile')
    @mock.patch('ebcli.operations.platformops.commonops.get_default_keyname')
    @mock.patch('ebcli.operations.platformops.commonops.set_environment_for_current_branch')
    @mock.patch('ebcli.operations.platformops.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.platformops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.platformops.heuristics.has_platform_definition_file')
    @mock.patch('ebcli.operations.platformops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.platformops.copyfile')
    @mock.patch('ebcli.operations.platformops.move')
    @mock.patch('ebcli.operations.platformops._get_latest_version')
    @mock.patch('ebcli.operations.platformops._enable_healthd')
    @mock.patch('ebcli.operations.platformops.get_app_version_s3_location')
    @mock.patch('ebcli.operations.platformops._zip_up_project')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.get_storage_location')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.create_platform_version')
    @mock.patch('ebcli.operations.platformops.s3.get_object_info')
    @mock.patch('ebcli.operations.platformops.io.get_event_streamer')
    @mock.patch('ebcli.operations.platformops.logsops.stream_platform_logs')
    @mock.patch('ebcli.operations.platformops.PackerStreamFormatter')
    def test_create_platform_version__update_minor_version(
            self,
            packer_stream_formatter_mock,
            stream_platform_logs_mock,
            get_event_streamer_mock,
            get_object_info_mock,
            create_platform_version_mock,
            get_storage_location_mock,
            _zip_up_project_mock,
            get_app_version_s3_location_mock,
            _enable_healthd_mock,
            _get_latest_version_mock,
            move_mock,
            copyfile_mock,
            get_source_control_mock,
            has_platform_definition_file_mock,
            directory_is_empty_mock,
            wait_for_success_events_mock,
            set_environment_for_current_branch_mock,
            get_default_keyname_mock,
            get_instance_profile_mock,
            get_platform_name_mock,
            _traverse_to_project_root_mock,
            delete_app_versions_mock,
            update_platform_version_mock
    ):
        packer_stream_formatter_instance_mock = mock.MagicMock()
        packer_stream_formatter_mock.return_value = packer_stream_formatter_instance_mock
        get_storage_location_mock.return_value = 's3-bucket'
        has_platform_definition_file_mock.return_value = True
        directory_is_empty_mock.return_value = False
        get_default_keyname_mock.return_value = 'aws-eb-us-west-2'
        get_instance_profile_mock.return_value = 'default'
        get_platform_name_mock.return_value = 'custom-platform-1'
        get_source_control_mock.untracked_changes_exist = mock.MagicMock(return_value=False)
        get_source_control_mock.get_version_label = mock.MagicMock(return_value='my-version-label')
        get_app_version_s3_location_mock.return_value = ['s3-bucket', 's3-key']
        create_platform_version_mock.return_value = {
            'PlatformSummary': {
                'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
            },
            'ResponseMetadata': {
                'RequestId': 'my-request-id'
            }
        }
        _get_latest_version_mock.return_value = '1.0.0'
        streamer_mock = mock.MagicMock()
        get_event_streamer_mock.return_value = streamer_mock

        platformops.create_platform_version(None, False, True, False, 't2.micro')

        get_object_info_mock.assert_called_once_with('s3-bucket', 's3-key')
        create_platform_version_mock.assert_called_once_with(
            'custom-platform-1',
            '1.1.0',
            's3-bucket',
            's3-key',
            'default',
            'aws-eb-us-west-2',
            't2.micro',
            None
        )
        update_platform_version_mock.assert_called_once_with('1.1.0')
        set_environment_for_current_branch_mock.assert_called_once_with(
            'eb-custom-platform-builder-packer'
        )
        get_event_streamer_mock.assert_called_once()
        stream_platform_logs_mock.assert_called_once_with(
            'custom-platform-1',
            '1.1.0',
            streamer_mock,
            5,
            None,
            packer_stream_formatter_instance_mock
        )
        wait_for_success_events_mock.assert_called_once_with(
            'my-request-id',
            platform_arn='arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0',
            streamer=streamer_mock,
            timeout_in_minutes=30
        )
        _enable_healthd_mock.assert_called_once()

        _zip_up_project_mock.assert_not_called()

    @mock.patch('ebcli.operations.platformops.fileoperations.update_platform_version')
    @mock.patch('ebcli.operations.platformops.fileoperations.delete_app_versions')
    @mock.patch('ebcli.operations.platformops.fileoperations._traverse_to_project_root')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_instance_profile')
    @mock.patch('ebcli.operations.platformops.commonops.get_default_keyname')
    @mock.patch('ebcli.operations.platformops.commonops.set_environment_for_current_branch')
    @mock.patch('ebcli.operations.platformops.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.platformops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.platformops.heuristics.has_platform_definition_file')
    @mock.patch('ebcli.operations.platformops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.platformops.copyfile')
    @mock.patch('ebcli.operations.platformops.move')
    @mock.patch('ebcli.operations.platformops._get_latest_version')
    @mock.patch('ebcli.operations.platformops._enable_healthd')
    @mock.patch('ebcli.operations.platformops.get_app_version_s3_location')
    @mock.patch('ebcli.operations.platformops._zip_up_project')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.get_storage_location')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.create_platform_version')
    @mock.patch('ebcli.operations.platformops.s3.get_object_info')
    @mock.patch('ebcli.operations.platformops.io.get_event_streamer')
    @mock.patch('ebcli.operations.platformops.logsops.stream_platform_logs')
    @mock.patch('ebcli.operations.platformops.PackerStreamFormatter')
    def test_create_platform_version__update_patch_version(
            self,
            packer_stream_formatter_mock,
            stream_platform_logs_mock,
            get_event_streamer_mock,
            get_object_info_mock,
            create_platform_version_mock,
            get_storage_location_mock,
            _zip_up_project_mock,
            get_app_version_s3_location_mock,
            _enable_healthd_mock,
            _get_latest_version_mock,
            move_mock,
            copyfile_mock,
            get_source_control_mock,
            has_platform_definition_file_mock,
            directory_is_empty_mock,
            wait_for_success_events_mock,
            set_environment_for_current_branch_mock,
            get_default_keyname_mock,
            get_instance_profile_mock,
            get_platform_name_mock,
            _traverse_to_project_root_mock,
            delete_app_versions_mock,
            update_platform_version_mock
    ):
        packer_stream_formatter_instance_mock = mock.MagicMock()
        packer_stream_formatter_mock.return_value = packer_stream_formatter_instance_mock
        get_storage_location_mock.return_value = 's3-bucket'
        has_platform_definition_file_mock.return_value = True
        directory_is_empty_mock.return_value = False
        get_default_keyname_mock.return_value = 'aws-eb-us-west-2'
        get_instance_profile_mock.return_value = 'default'
        get_platform_name_mock.return_value = 'custom-platform-1'
        get_source_control_mock.untracked_changes_exist = mock.MagicMock(return_value=False)
        get_source_control_mock.get_version_label = mock.MagicMock(return_value='my-version-label')
        get_app_version_s3_location_mock.return_value = ['s3-bucket', 's3-key']
        create_platform_version_mock.return_value = {
            'PlatformSummary': {
                'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
            },
            'ResponseMetadata': {
                'RequestId': 'my-request-id'
            }
        }
        _get_latest_version_mock.return_value = '1.0.0'
        streamer_mock = mock.MagicMock()
        get_event_streamer_mock.return_value = streamer_mock

        platformops.create_platform_version(None, False, False, True, 't2.micro')

        get_object_info_mock.assert_called_once_with('s3-bucket', 's3-key')
        create_platform_version_mock.assert_called_once_with(
            'custom-platform-1',
            '1.0.1',
            's3-bucket',
            's3-key',
            'default',
            'aws-eb-us-west-2',
            't2.micro',
            None
        )
        update_platform_version_mock.assert_called_once_with('1.0.1')
        set_environment_for_current_branch_mock.assert_called_once_with(
            'eb-custom-platform-builder-packer'
        )
        get_event_streamer_mock.assert_called_once()
        stream_platform_logs_mock.assert_called_once_with(
            'custom-platform-1',
            '1.0.1',
            streamer_mock,
            5,
            None,
            packer_stream_formatter_instance_mock
        )
        wait_for_success_events_mock.assert_called_once_with(
            'my-request-id',
            platform_arn='arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0',
            streamer=streamer_mock,
            timeout_in_minutes=30
        )
        _enable_healthd_mock.assert_called_once()

        _zip_up_project_mock.assert_not_called()

    @mock.patch('ebcli.operations.platformops.fileoperations.update_platform_version')
    @mock.patch('ebcli.operations.platformops.fileoperations._traverse_to_project_root')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_instance_profile')
    @mock.patch('ebcli.operations.platformops.commonops.get_default_keyname')
    @mock.patch('ebcli.operations.platformops.commonops.set_environment_for_current_branch')
    @mock.patch('ebcli.operations.platformops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.platformops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.platformops.copyfile')
    @mock.patch('ebcli.operations.platformops.move')
    @mock.patch('ebcli.operations.platformops._get_latest_version')
    @mock.patch('ebcli.operations.platformops.get_app_version_s3_location')
    @mock.patch('ebcli.operations.platformops._zip_up_project')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.get_storage_location')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.create_platform_version')
    @mock.patch('ebcli.operations.platformops.io.get_event_streamer')
    @mock.patch('ebcli.operations.platformops.logsops.stream_platform_logs')
    @mock.patch('ebcli.operations.platformops.PackerStreamFormatter')
    def test_create_platform_version__directory_is_empty(
            self,
            packer_stream_formatter_mock,
            stream_platform_logs_mock,
            get_event_streamer_mock,
            create_platform_version_mock,
            get_storage_location_mock,
            _zip_up_project_mock,
            get_app_version_s3_location_mock,
            _get_latest_version_mock,
            move_mock,
            copyfile_mock,
            get_source_control_mock,
            directory_is_empty_mock,
            set_environment_for_current_branch_mock,
            get_default_keyname_mock,
            get_instance_profile_mock,
            get_platform_name_mock,
            _traverse_to_project_root_mock,
            update_platform_version_mock
    ):
        packer_stream_formatter_instance_mock = mock.MagicMock()
        packer_stream_formatter_mock.return_value = packer_stream_formatter_instance_mock
        get_storage_location_mock.return_value = 's3-bucket'
        directory_is_empty_mock.return_value = True
        get_default_keyname_mock.return_value = 'aws-eb-us-west-2'
        get_instance_profile_mock.return_value = 'default'
        get_platform_name_mock.return_value = 'custom-platform-1'
        get_source_control_mock.untracked_changes_exist = mock.MagicMock(return_value=False)
        get_source_control_mock.get_version_label = mock.MagicMock(return_value='my-version-label')
        get_app_version_s3_location_mock.return_value = ['s3-bucket', 's3-key']
        create_platform_version_mock.return_value = {
            'PlatformSummary': {
                'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
            },
            'ResponseMetadata': {
                'RequestId': 'my-request-id'
            }
        }
        _get_latest_version_mock.return_value = '1.0.0'
        streamer_mock = mock.MagicMock()
        get_event_streamer_mock.return_value = streamer_mock

        with self.assertRaises(platformops.PlatformWorkspaceEmptyError):
            platformops.create_platform_version(None, False, False, True, 't2.micro')

        create_platform_version_mock.assert_not_called()
        update_platform_version_mock.assert_not_called()
        set_environment_for_current_branch_mock.assert_not_called()

        _zip_up_project_mock.assert_not_called()

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

    @mock.patch('ebcli.operations.platformops.fileoperations._traverse_to_project_root')
    @mock.patch('ebcli.operations.platformops.yaml.load')
    def test_enable_healthd(
            self,
            load_mock,
            _traverse_to_project_root_mock
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

    @mock.patch('ebcli.operations.platformops.list_platform_versions')
    def test_get_platforms(
            self,
            list_platform_versions_mock
    ):
        list_platform_versions_mock.return_value = self.custom_platforms_list

        self.assertEqual(
            {
                'custom-platform-2': '1.0.0',
                'custom-platform-4': '1.0.0',
                'custom-platform-3': '1.0.0',
                'custom-platform-1': '1.0.0'
            },
            platformops.get_platforms()
        )

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
