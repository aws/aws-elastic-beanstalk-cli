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
from ebcli.objects.platform import PlatformBranch, PlatformVersion
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

    @mock.patch('ebcli.operations.platformops.platform_version_ops.list_custom_platform_versions')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_family')
    @mock.patch('ebcli.operations.platformops.get_custom_platform_from_customer')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_branch')
    def test_prompt_for_platform(
        self,
        prompt_for_platform_branch_mock,
        get_custom_platform_from_customer_mock,
        prompt_for_platform_family_mock,
        list_custom_platform_versions_mock,
    ):
        platform_branch = PlatformBranch('Python 3.6 running on 64bit Amazon Linux')
        list_custom_platform_versions_mock.return_value = []
        prompt_for_platform_family_mock.return_value = 'Python'
        prompt_for_platform_branch_mock.return_value = platform_branch
        expected = platform_branch

        result = platformops.prompt_for_platform()

        list_custom_platform_versions_mock.assert_called_once_with()
        prompt_for_platform_family_mock.assert_called_once_with(include_custom=False)
        get_custom_platform_from_customer_mock.assert_not_called()
        prompt_for_platform_branch_mock.assert_called_once_with('Python')
        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.get_custom_platform_from_customer')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_branch')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_family')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.list_custom_platform_versions')
    def test_prompt_for_platform__with_custom_platform_versions(
        self,
        list_custom_platform_versions_mock,
        prompt_for_platform_family_mock,
        prompt_for_platform_branch_mock,
        get_custom_platform_from_customer_mock
    ):
        custom_platform_versions = [
            {
                'PlatformOwner': 'self',
                'PlatformStatus': 'Ready',
            }
        ]
        list_custom_platform_versions_mock.return_value = custom_platform_versions
        prompt_for_platform_family_mock.return_value = 'Custom Platform'
        get_custom_platform_from_customer_mock.return_value = 'Custom Platform v1'

        result = platformops.prompt_for_platform()

        list_custom_platform_versions_mock.assert_called_once_with()
        prompt_for_platform_family_mock.assert_called_once_with(include_custom=True)
        prompt_for_platform_branch_mock.assert_not_called()
        get_custom_platform_from_customer_mock.assert_called_once_with(custom_platform_versions)
        self.assertEqual('Custom Platform v1', result)

    @mock.patch('ebcli.operations.platformops.platform_version_ops.list_custom_platform_versions')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_family')
    @mock.patch('ebcli.operations.platformops.get_custom_platform_from_customer')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_branch')
    def test_prompt_for_platform__with_custom_platforms_selected(
        self,
        prompt_for_platform_branch_mock,
        get_custom_platform_from_customer_mock,
        prompt_for_platform_family_mock,
        list_custom_platform_versions_mock,
    ):
        custom_platform_version = PlatformVersion(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.0')
        list_custom_platform_versions_mock.return_value = TestPlatformOperations.custom_platforms_list
        prompt_for_platform_family_mock.return_value = 'Custom Platform'
        get_custom_platform_from_customer_mock.return_value = custom_platform_version
        expected = custom_platform_version

        result = platformops.prompt_for_platform()

        list_custom_platform_versions_mock.assert_called_once_with()
        prompt_for_platform_family_mock.assert_called_once_with(include_custom=True)
        get_custom_platform_from_customer_mock.assert_called_once_with(TestPlatformOperations.custom_platforms_list)
        prompt_for_platform_branch_mock.assert_not_called()
        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.io.echo')
    @mock.patch('ebcli.operations.platformops.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.operations.platformops.list_nonretired_platform_families')
    @mock.patch('ebcli.operations.platformops.detect_platform_family')
    def test_prompt_for_platform_family(
        self,
        detect_platform_family_mock,
        list_nonretired_platform_families_mock,
        prompt_for_item_in_list_mock,
        echo_mock,
    ):
        families_unsorted = ['Python', 'Docker', 'Node.js', 'Golang']
        families_sorted = ['Docker', 'Golang', 'Node.js', 'Python']

        detect_platform_family_mock.return_value = None
        list_nonretired_platform_families_mock.return_value = families_unsorted
        prompt_for_item_in_list_mock.return_value = families_sorted[0]
        call_tracker = mock.Mock()
        call_tracker.attach_mock(prompt_for_item_in_list_mock, 'prompt_for_item_in_list_mock')
        call_tracker.attach_mock(echo_mock, 'echo_mock')
        expected = families_sorted[0]

        result = platformops.prompt_for_platform_family()

        detect_platform_family_mock.assert_called_once_with(families_sorted)
        list_nonretired_platform_families_mock.assert_called_once_with(cache=True)
        call_tracker.assert_has_calls(
            [
                mock.call.echo_mock('Select a platform.'),
                mock.call.prompt_for_item_in_list_mock(families_sorted, default=None),
            ],
            any_order=False
        )
        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.io.echo')
    @mock.patch('ebcli.operations.platformops.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.operations.platformops.list_nonretired_platform_families')
    @mock.patch('ebcli.operations.platformops.detect_platform_family')
    def test_prompt_for_platform_family__with_custom_platform(
        self,
        detect_platform_family_mock,
        list_nonretired_platform_families_mock,
        prompt_for_item_in_list_mock,
        echo_mock,
    ):
        families_unsorted = ['Python', 'Docker', 'Node.js', 'Golang']
        families_sorted = ['Docker', 'Golang', 'Node.js', 'Python']

        detect_platform_family_mock.return_value = None
        list_nonretired_platform_families_mock.return_value = families_unsorted
        prompt_for_item_in_list_mock.return_value = families_sorted[0]
        call_tracker = mock.Mock()
        call_tracker.attach_mock(prompt_for_item_in_list_mock, 'prompt_for_item_in_list_mock')
        call_tracker.attach_mock(echo_mock, 'echo_mock')
        expected = families_sorted[0]

        result = platformops.prompt_for_platform_family(include_custom=True)

        detect_platform_family_mock.assert_called_once_with(families_sorted + ['Custom Platform'])
        list_nonretired_platform_families_mock.assert_called_once_with(cache=True)
        call_tracker.assert_has_calls(
            [
                mock.call.echo_mock('Select a platform.'),
                mock.call.prompt_for_item_in_list_mock(families_sorted + ['Custom Platform'], default=None),
            ],
            any_order=False
        )
        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.io.echo')
    @mock.patch('ebcli.operations.platformops.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.operations.platformops.list_nonretired_platform_families')
    @mock.patch('ebcli.operations.platformops.detect_platform_family')
    def test_prompt_for_platform_family__with_detected_platform_family(
        self,
        detect_platform_family_mock,
        list_nonretired_platform_families_mock,
        prompt_for_item_in_list_mock,
        echo_mock,
    ):
        families_unsorted = ['Python', 'Docker', 'Node.js', 'Golang']
        families_sorted = ['Docker', 'Golang', 'Node.js', 'Python']

        detect_platform_family_mock.return_value = 'Python'
        list_nonretired_platform_families_mock.return_value = families_unsorted
        expected = 'Python'

        result = platformops.prompt_for_platform_family()

        list_nonretired_platform_families_mock.assert_called_once_with(cache=True)
        detect_platform_family_mock.assert_called_once_with(families_sorted)
        prompt_for_item_in_list_mock.assert_not_called()
        echo_mock.assert_not_called()
        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.list_custom_platform_versions')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_family')
    @mock.patch('ebcli.operations.platformops.get_custom_platform_from_customer')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_branch')
    def test_prompt_for_platform(
        self,
        prompt_for_platform_branch_mock,
        get_custom_platform_from_customer_mock,
        prompt_for_platform_family_mock,
        list_custom_platform_versions_mock,
    ):
        platform_branch = PlatformBranch('Python 3.6 running on 64bit Amazon Linux')
        list_custom_platform_versions_mock.return_value = []
        prompt_for_platform_family_mock.return_value = 'Python'
        prompt_for_platform_branch_mock.return_value = platform_branch
        expected = platform_branch

        result = platformops.prompt_for_platform()

        list_custom_platform_versions_mock.assert_called_once_with()
        prompt_for_platform_family_mock.assert_called_once_with(include_custom=False)
        get_custom_platform_from_customer_mock.assert_not_called()
        prompt_for_platform_branch_mock.assert_called_once_with('Python')
        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.get_custom_platform_from_customer')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_branch')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_family')
    @mock.patch('ebcli.operations.platformops.list_custom_platform_versions')
    def test_prompt_for_platform__with_custom_platform_versions(
        self,
        list_custom_platform_versions_mock,
        prompt_for_platform_family_mock,
        prompt_for_platform_branch_mock,
        get_custom_platform_from_customer_mock
    ):
        custom_platform_versions = [
            {
                'PlatformOwner': 'self',
                'PlatformStatus': 'Ready',
            }
        ]
        list_custom_platform_versions_mock.return_value = custom_platform_versions
        prompt_for_platform_family_mock.return_value = 'Custom Platform'
        get_custom_platform_from_customer_mock.return_value = 'Custom Platform v1'

        result = platformops.prompt_for_platform()

        list_custom_platform_versions_mock.assert_called_once_with()
        prompt_for_platform_family_mock.assert_called_once_with(include_custom=True)
        prompt_for_platform_branch_mock.assert_not_called()
        get_custom_platform_from_customer_mock.assert_called_once_with(custom_platform_versions)
        self.assertEqual('Custom Platform v1', result)

    @mock.patch('ebcli.operations.platformops.list_custom_platform_versions')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_family')
    @mock.patch('ebcli.operations.platformops.get_custom_platform_from_customer')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_branch')
    def test_prompt_for_platform__with_custom_platforms_selected(
        self,
        prompt_for_platform_branch_mock,
        get_custom_platform_from_customer_mock,
        prompt_for_platform_family_mock,
        list_custom_platform_versions_mock,
    ):
        custom_platform_version = PlatformVersion(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.0')
        list_custom_platform_versions_mock.return_value = TestPlatformOperations.custom_platforms_list
        prompt_for_platform_family_mock.return_value = 'Custom Platform'
        get_custom_platform_from_customer_mock.return_value = custom_platform_version
        expected = custom_platform_version

        result = platformops.prompt_for_platform()

        list_custom_platform_versions_mock.assert_called_once_with()
        prompt_for_platform_family_mock.assert_called_once_with(include_custom=True)
        get_custom_platform_from_customer_mock.assert_called_once_with(TestPlatformOperations.custom_platforms_list)
        prompt_for_platform_branch_mock.assert_not_called()
        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.io.echo')
    @mock.patch('ebcli.operations.platformops.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.operations.platformops.list_nonretired_platform_families')
    @mock.patch('ebcli.operations.platformops.detect_platform_family')
    def test_prompt_for_platform_family(
        self,
        detect_platform_family_mock,
        list_nonretired_platform_families_mock,
        prompt_for_item_in_list_mock,
        echo_mock,
    ):
        families_unsorted = ['Python', 'Docker', 'Node.js', 'Golang']
        families_sorted = ['Docker', 'Golang', 'Node.js', 'Python']

        detect_platform_family_mock.return_value = None
        list_nonretired_platform_families_mock.return_value = families_unsorted
        prompt_for_item_in_list_mock.return_value = families_sorted[0]
        call_tracker = mock.Mock()
        call_tracker.attach_mock(prompt_for_item_in_list_mock, 'prompt_for_item_in_list_mock')
        call_tracker.attach_mock(echo_mock, 'echo_mock')
        expected = families_sorted[0]

        result = platformops.prompt_for_platform_family()

        detect_platform_family_mock.assert_called_once_with(families_sorted)
        list_nonretired_platform_families_mock.assert_called_once_with(cache=True)
        call_tracker.assert_has_calls(
            [
                mock.call.echo_mock('Select a platform.'),
                mock.call.prompt_for_item_in_list_mock(families_sorted, default=None),
            ],
            any_order=False
        )
        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.io.echo')
    @mock.patch('ebcli.operations.platformops.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.operations.platformops.list_nonretired_platform_families')
    @mock.patch('ebcli.operations.platformops.detect_platform_family')
    def test_prompt_for_platform_family__with_custom_platform(
        self,
        detect_platform_family_mock,
        list_nonretired_platform_families_mock,
        prompt_for_item_in_list_mock,
        echo_mock,
    ):
        families_unsorted = ['Python', 'Docker', 'Node.js', 'Golang']
        families_sorted = ['Docker', 'Golang', 'Node.js', 'Python']

        detect_platform_family_mock.return_value = None
        list_nonretired_platform_families_mock.return_value = families_unsorted
        prompt_for_item_in_list_mock.return_value = families_sorted[0]
        call_tracker = mock.Mock()
        call_tracker.attach_mock(prompt_for_item_in_list_mock, 'prompt_for_item_in_list_mock')
        call_tracker.attach_mock(echo_mock, 'echo_mock')
        expected = families_sorted[0]

        result = platformops.prompt_for_platform_family(include_custom=True)

        detect_platform_family_mock.assert_called_once_with(families_sorted + ['Custom Platform'])
        list_nonretired_platform_families_mock.assert_called_once_with(cache=True)
        call_tracker.assert_has_calls(
            [
                mock.call.echo_mock('Select a platform.'),
                mock.call.prompt_for_item_in_list_mock(families_sorted + ['Custom Platform'], default=None),
            ],
            any_order=False
        )
        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.io.echo')
    @mock.patch('ebcli.operations.platformops.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.operations.platformops.list_nonretired_platform_families')
    @mock.patch('ebcli.operations.platformops.detect_platform_family')
    def test_prompt_for_platform_family__with_detected_platform_family(
        self,
        detect_platform_family_mock,
        list_nonretired_platform_families_mock,
        prompt_for_item_in_list_mock,
        echo_mock,
    ):
        families_unsorted = ['Python', 'Docker', 'Node.js', 'Golang']
        families_sorted = ['Docker', 'Golang', 'Node.js', 'Python']

        detect_platform_family_mock.return_value = 'Python'
        list_nonretired_platform_families_mock.return_value = families_unsorted
        expected = 'Python'

        result = platformops.prompt_for_platform_family()

        list_nonretired_platform_families_mock.assert_called_once_with(cache=True)
        detect_platform_family_mock.assert_called_once_with(families_sorted)
        prompt_for_item_in_list_mock.assert_not_called()
        echo_mock.assert_not_called()
        self.assertEqual(expected, result)

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

    @mock.patch('ebcli.operations.platformops.platform_version_ops.get_platform_arn')
    def test_name_to_arn__is_valid_platform_name(
            self,
            get_platform_arn_mock
    ):
        get_platform_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3'

        self.assertEqual(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3',
            platformops._name_to_arn('custom-platform-1')
        )
        get_platform_arn_mock.assert_called_once_with('custom-platform-1', 'latest', owner='self')

    @mock.patch('ebcli.operations.platformops.platform_version_ops.get_platform_arn')
    def test_name_to_arn__is_valid_platform_short_name(
            self,
            get_platform_arn_mock
    ):
        get_platform_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3'

        self.assertEqual(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.3',
            platformops._name_to_arn('custom-platform-1/1.0.3')
        )
        get_platform_arn_mock.assert_called_once_with('custom-platform-1', '1.0.3', owner='self')

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.version_to_arn')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.describe_custom_platform_version')
    @mock.patch('ebcli.operations.platformops.io.echo')
    def test_get_version_status(
            self,
            echo_mock,
            describe_custom_platform_version_mock,
            version_to_arn_mock,
            get_platform_name_mock
    ):
        get_platform_name_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        version_to_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
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
    @mock.patch('ebcli.operations.platformops.platform_version_ops.version_to_arn')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.describe_custom_platform_version')
    @mock.patch('ebcli.operations.platformops.io.echo')
    def test_get_version_status__version_derived_from_config_yml(
            self,
            echo_mock,
            describe_custom_platform_version_mock,
            version_to_arn_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        get_platform_version_mock.return_value = '1.0.0'
        get_platform_name_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        version_to_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
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
    @mock.patch('ebcli.operations.platformops.platform_version_ops.version_to_arn')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.get_latest_platform_version')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.describe_custom_platform_version')
    @mock.patch('ebcli.operations.platformops.io.echo')
    def test_get_version_status__latest_version_retrieved_from_aws(
            self,
            echo_mock,
            describe_custom_platform_version_mock,
            get_latest_platform_version_mock,
            version_to_arn_mock,
            get_platform_version_mock,
            get_platform_name_mock,
            update_platform_version_mock
    ):
        get_latest_platform_version_mock.return_value = '1.0.0'
        get_platform_version_mock.return_value = None
        get_platform_name_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        version_to_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
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
    @mock.patch('ebcli.operations.platformops.platform_version_ops.version_to_arn')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.get_latest_platform_version')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.describe_custom_platform_version')
    def test_get_version_status__version_could_not_be_determined(
            self,
            describe_custom_platform_version_mock,
            get_latest_platform_version_mock,
            version_to_arn_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        get_latest_platform_version_mock.return_value = None
        get_platform_version_mock.return_value = None
        get_platform_name_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        version_to_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        describe_custom_platform_version_mock.return_value = self.describe_platform_result
        with self.assertRaises(platformops.InvalidPlatformVersionError) as context_manager:
            platformops.get_version_status(None)
        self.assertEqual(
            'No such version exists for the current platform.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.version_to_arn')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.describe_custom_platform_version')
    def test_get_version_status__invalid_platform_version(
            self,
            describe_custom_platform_version_mock,
            version_to_arn_mock,
            get_platform_name_mock,
    ):
        get_platform_name_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        version_to_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        describe_custom_platform_version_mock.return_value = []

        with self.assertRaises(platformops.InvalidPlatformVersionError) as context_manager:
            platformops.get_version_status('1.0.0')
        self.assertEqual(
            'No such version exists for the current platform.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_version')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.describe_custom_platform_version')
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
    @mock.patch('ebcli.operations.platformops.platform_version_ops.version_to_arn')
    def test_show_platform_events__version_provided(
            self,
            version_to_arn_mock,
            print_events_mock,
            get_platform_name_mock
    ):
        get_platform_name_mock.return_value = 'custom-platform-1'
        version_to_arn_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'

        platformops.show_platform_events(True, '1.0.0')

        version_to_arn_mock.assert_called_once_with('1.0.0')
        print_events_mock.assert_called_once_with(
            app_name=None,
            env_name=None,
            follow=True,
            platform_arn='arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-1/1.0.0'
        )

    @mock.patch('ebcli.operations.platformops.fileoperations.get_platform_name')
    @mock.patch('ebcli.operations.platformops.fileoperations.update_platform_version')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.get_latest_platform_version')
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

    @mock.patch('ebcli.operations.platformops.platform_version_ops.get_platforms')
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

    @mock.patch('ebcli.operations.platformops.platform_version_ops.get_platforms')
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
    @mock.patch('ebcli.operations.platformops.platform_branch_ops.is_platform_branch_name')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.get_preferred_platform_version_for_branch')
    @mock.patch('ebcli.operations.platformops.solution_stack_ops.find_solution_stack_from_string')
    def test_get_platform_for_platform_string__given_arn(
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

        result = platformops.get_platform_for_platform_string(platform_string)

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
    @mock.patch('ebcli.operations.platformops.platform_branch_ops.is_platform_branch_name')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.get_preferred_platform_version_for_branch')
    @mock.patch('ebcli.operations.platformops.solution_stack_ops.find_solution_stack_from_string')
    def test_get_platform_for_platform_string__given_branch_name(
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

        result = platformops.get_platform_for_platform_string(platform_string)

        is_valid_arn_mock.assert_called_once_with(platform_string)
        describe_platform_version_mock.assert_not_called()
        is_platform_branch_name_mock.assert_called_once_with(platform_string)
        get_preferred_platform_version_for_branch_mock.assert_called_with(platform_string)
        find_solution_stack_from_string_mock.assert_not_called()
        self.assertIsInstance(result, PlatformVersion)
        self.assertIs(platform_version, result)

    @mock.patch('ebcli.operations.platformops.PlatformVersion.is_valid_arn')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk.describe_platform_version')
    @mock.patch('ebcli.operations.platformops.platform_branch_ops.is_platform_branch_name')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.get_preferred_platform_version_for_branch')
    @mock.patch('ebcli.operations.platformops.solution_stack_ops.find_solution_stack_from_string')
    def test_get_platform_for_platform_string__given_solution_stack_string(
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

        result = platformops.get_platform_for_platform_string(platform_string)

        is_valid_arn_mock.assert_called_once_with(platform_string)
        describe_platform_version_mock.assert_not_called()
        is_platform_branch_name_mock.assert_called_once_with(platform_string)
        get_preferred_platform_version_for_branch_mock.assert_not_called()
        find_solution_stack_from_string_mock.assert_called_once_with(platform_string)
        self.assertIsInstance(result, SolutionStack)
        self.assertIs(solution_stack, result)

    def test__generate_platform_branch_prompt_text__supported(self):
        branch = {
            'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
            'LifecycleState': 'Supported',
        }
        expected = 'Python 3.6 running on 64bit Amazon Linux'

        result = platformops._generate_platform_branch_prompt_text(branch)

        self.assertEqual(expected, result)

    def test__generate_platform_branch_prompt_text__beta(self):
        branch = {
            'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
            'LifecycleState': 'Beta',
        }
        expected = 'Python 3.6 running on 64bit Amazon Linux (Beta)'

        result = platformops._generate_platform_branch_prompt_text(branch)

        self.assertEqual(expected, result)

    def test__generate_platform_branch_prompt_text__deprecated(self):
        branch = {
            'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
            'LifecycleState': 'Deprecated',
        }
        expected = 'Python 3.6 running on 64bit Amazon Linux (Deprecated)'

        result = platformops._generate_platform_branch_prompt_text(branch)

        self.assertEqual(expected, result)

    def test__generate_platform_branch_prompt_text__retired(self):
        branch = {
            'BranchName': 'Python 3.6 running on 64bit Amazon Linux',
            'LifecycleState': 'Retired',
        }
        expected = 'Python 3.6 running on 64bit Amazon Linux (Retired)'

        result = platformops._generate_platform_branch_prompt_text(branch)

        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.commonops.get_config_setting_from_branch_or_default')
    def test_get_configured_platform_string(
        self,
        get_config_setting_from_branch_or_default_mock,
    ):
        configured_platform_string = 'Python 3.6 running on 64bit Amazon Linux'
        get_config_setting_from_branch_or_default_mock.return_value = configured_platform_string

        result = platformops.get_configured_default_platform()

        get_config_setting_from_branch_or_default_mock.assert_called_once_with('default_platform')
        self.assertEqual(configured_platform_string, result)

    @mock.patch('ebcli.operations.platformops.platform_branch_ops.collect_families_from_branches')
    @mock.patch('ebcli.operations.platformops.platform_branch_ops.list_nonretired_platform_branches')
    def test_list_nonretired_platform_families(
        self,
        list_nonretired_platform_branches_mock,
        collect_families_from_branches_mock,
    ):
        branches = [
            {"BranchName": "Docker running on 64bit Amazon Linux",
                "LifecycleState": "Supported", "PlatformName": "Docker"},
            {"BranchName": "Go 1 running on 64bit Amazon Linux",
                "LifecycleState": "Supported", "PlatformName": "Golang"},
            {"BranchName": "Multi-container Docker running on 64bit Amazon Linux",
                "LifecycleState": "Supported", "PlatformName": "Docker"},
            {"BranchName": "Python 3.6 running on 64bit Amazon Linux",
                "LifecycleState": "Supported", "PlatformName": "Python"},
        ]
        expected = ['Docker', 'Golang', 'Python']

        list_nonretired_platform_branches_mock.return_value = branches
        collect_families_from_branches_mock.return_value = expected

        result = platformops.list_nonretired_platform_families()

        list_nonretired_platform_branches_mock.assert_called_once_with()
        collect_families_from_branches_mock.assert_called_once_with(branches)
        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.platform_version_ops.list_custom_platform_versions')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_family')
    @mock.patch('ebcli.operations.platformops.get_custom_platform_from_customer')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_branch')
    def test_prompt_for_platform(
        self,
        prompt_for_platform_branch_mock,
        get_custom_platform_from_customer_mock,
        prompt_for_platform_family_mock,
        list_custom_platform_versions_mock,
    ):
        platform_branch = PlatformBranch('Python 3.6 running on 64bit Amazon Linux')
        list_custom_platform_versions_mock.return_value = []
        prompt_for_platform_family_mock.return_value = 'Python'
        prompt_for_platform_branch_mock.return_value = platform_branch
        expected = plastform_branch

        result = platformops.prompt_for_platform()

        list_custom_platform_versions_mock.assert_called_once_with()
        prompt_for_platform_family_mock.assert_called_once_with(include_custom=False)
        get_custom_platform_from_customer_mock.assert_not_called()
        prompt_for_platform_branch_mock.assert_called_once_with('Python')
        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.platform_version_ops.list_custom_platform_versions')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_family')
    @mock.patch('ebcli.operations.platformops.get_custom_platform_from_customer')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_branch')
    def test_prompt_for_platform__with_custom_platforms(
        self,
        prompt_for_platform_branch_mock,
        get_custom_platform_from_customer_mock,
        prompt_for_platform_family_mock,
        list_custom_platform_versions_mock,
    ):
        platform_branch = PlatformBranch('Python 3.6 running on 64bit Amazon Linux')
        list_custom_platform_versions_mock.return_value = [{}, {}, {}]
        prompt_for_platform_family_mock.return_value = 'Python'
        prompt_for_platform_branch_mock.return_value = platform_branch
        expected = platform_branch

        result = platformops.prompt_for_platform()

        list_custom_platform_versions_mock.assert_called_once_with()
        prompt_for_platform_family_mock.assert_called_once_with(include_custom=True)
        get_custom_platform_from_customer_mock.assert_not_called()
        prompt_for_platform_branch_mock.assert_called_once_with('Python')
        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.platform_version_ops.list_custom_platform_versions')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_family')
    @mock.patch('ebcli.operations.platformops.get_custom_platform_from_customer')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_branch')
    def test_prompt_for_platform__with_custom_platforms_selected(
        self,
        prompt_for_platform_branch_mock,
        get_custom_platform_from_customer_mock,
        prompt_for_platform_family_mock,
        list_custom_platform_versions_mock,
    ):
        custom_platform_version = PlatformVersion(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.0')
        list_custom_platform_versions_mock.return_value = TestPlatformOperations.custom_platforms_list
        prompt_for_platform_family_mock.return_value = 'Custom Platform'
        get_custom_platform_from_customer_mock.return_value = custom_platform_version
        expected = custom_platform_version

        result = platformops.prompt_for_platform()

        list_custom_platform_versions_mock.assert_called_once_with()
        prompt_for_platform_family_mock.assert_called_once_with(include_custom=True)
        get_custom_platform_from_customer_mock.assert_called_once_with(TestPlatformOperations.custom_platforms_list)
        prompt_for_platform_branch_mock.assert_not_called()
        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.io.echo')
    @mock.patch('ebcli.operations.platformops.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.operations.platformops.list_nonretired_platform_families')
    @mock.patch('ebcli.operations.platformops.detect_platform_family')
    def test_prompt_for_platform_family(
        self,
        detect_platform_family_mock,
        list_nonretired_platform_families_mock,
        prompt_for_item_in_list_mock,
        echo_mock,
    ):
        families_unsorted = ['Python', 'Docker', 'Node.js', 'Golang']
        families_sorted = ['Docker', 'Golang', 'Node.js', 'Python']

        detect_platform_family_mock.return_value = None
        list_nonretired_platform_families_mock.return_value = families_unsorted
        prompt_for_item_in_list_mock.return_value = families_sorted[0]
        call_tracker = mock.Mock()
        call_tracker.attach_mock(prompt_for_item_in_list_mock, 'prompt_for_item_in_list_mock')
        call_tracker.attach_mock(echo_mock, 'echo_mock')
        expected = families_sorted[0]

        result = platformops.prompt_for_platform_family()

        detect_platform_family_mock.assert_called_once_with(families_sorted)
        list_nonretired_platform_families_mock.assert_called_once_with()
        call_tracker.assert_has_calls(
            [
                mock.call.echo_mock('Select a platform.'),
                mock.call.prompt_for_item_in_list_mock(families_sorted, default=None),
            ],
            any_order=False
        )
        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.io.echo')
    @mock.patch('ebcli.operations.platformops.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.operations.platformops.list_nonretired_platform_families')
    @mock.patch('ebcli.operations.platformops.detect_platform_family')
    def test_prompt_for_platform_family__with_custom_platform(
        self,
        detect_platform_family_mock,
        list_nonretired_platform_families_mock,
        prompt_for_item_in_list_mock,
        echo_mock,
    ):
        families_unsorted = ['Python', 'Docker', 'Node.js', 'Golang']
        families_sorted = ['Docker', 'Golang', 'Node.js', 'Python']

        detect_platform_family_mock.return_value = None
        list_nonretired_platform_families_mock.return_value = families_unsorted
        prompt_for_item_in_list_mock.return_value = families_sorted[0]
        call_tracker = mock.Mock()
        call_tracker.attach_mock(prompt_for_item_in_list_mock, 'prompt_for_item_in_list_mock')
        call_tracker.attach_mock(echo_mock, 'echo_mock')
        expected = families_sorted[0]

        result = platformops.prompt_for_platform_family(include_custom=True)

        detect_platform_family_mock.assert_called_once_with(families_sorted + ['Custom Platform'])
        list_nonretired_platform_families_mock.assert_called_once_with()
        call_tracker.assert_has_calls(
            [
                mock.call.echo_mock('Select a platform.'),
                mock.call.prompt_for_item_in_list_mock(families_sorted + ['Custom Platform'], default=None),
            ],
            any_order=False
        )
        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.io.echo')
    @mock.patch('ebcli.operations.platformops.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.operations.platformops.list_nonretired_platform_families')
    @mock.patch('ebcli.operations.platformops.detect_platform_family')
    def test_prompt_for_platform_family__with_detected_platform_family(
        self,
        detect_platform_family_mock,
        list_nonretired_platform_families_mock,
        prompt_for_item_in_list_mock,
        echo_mock,
    ):
        families_unsorted = ['Python', 'Docker', 'Node.js', 'Golang']
        families_sorted = ['Docker', 'Golang', 'Node.js', 'Python']

        detect_platform_family_mock.return_value = 'Python'
        list_nonretired_platform_families_mock.return_value = families_unsorted
        expected = 'Python'

        result = platformops.prompt_for_platform_family()

        list_nonretired_platform_families_mock.assert_called_once_with()
        detect_platform_family_mock.assert_called_once_with(families_sorted)
        prompt_for_item_in_list_mock.assert_not_called()
        echo_mock.assert_not_called()
        self.assertEqual(expected, result)

    def test__sort_platform_branches_for_prompt(self):
        branches = [
            {"BranchName": "Python 2.7 running on 64bit Amazon Linux",
                "LifecycleState": "Deprecated", "PlatformName": "Python",
                "BranchOrder": '9600'},
            {"BranchName": "Python 3.4 running on 64bit Amazon Linux",
                "LifecycleState": "Deprecated", "PlatformName": "Python",
                "BranchOrder": '9700'},
            {"BranchName": "Python 3.7 running on 64bit Amazon Linux 2",
                "LifecycleState": "Beta", "PlatformName": "Python",
                "BranchOrder": '9100'},
            {"BranchName": "Python 2.7 running on 32bit Amazon Linux",
                "LifecycleState": "Retired", "PlatformName": "Python",
                "BranchOrder": '9000'},
            {"BranchName": "Python 3.6 running on 64bit Amazon Linux",
                "LifecycleState": "Supported", "PlatformName": "Python",
                "BranchOrder": '9300'},
        ]
        expected = [
            branches[4],
            branches[2],
            branches[1],
            branches[0],
            branches[3],
        ]

        result = platformops._sort_platform_branches_for_prompt(branches)

        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.io.echo')
    @mock.patch('ebcli.operations.platformops.utils.prompt_for_index_in_list')
    @mock.patch('ebcli.operations.platformops._sort_platform_branches_for_prompt')
    @mock.patch('ebcli.operations.platformops.platform_branch_ops.list_nonretired_platform_branches')
    def test_prompt_for_platform_branch(
        self,
        list_nonretired_platform_branches_mock,
        _sort_platform_branches_for_prompt_mock,
        prompt_for_index_in_list_mock,
        echo_mock,
    ):
        family = 'Python'
        branches = [
            {"BranchName": "Python 3.7 running on 64bit Amazon Linux 2",
             "LifecycleState": "Beta", "PlatformName": "Python"},
            {"BranchName": "Python 2.7 running on 64bit Amazon Linux",
                "LifecycleState": "Deprecated", "PlatformName": "Python"},
            {"BranchName": "Multi-container Docker running on 64bit Amazon Linux",
                "LifecycleState": "Supported", "PlatformName": "Docker"},
            {"BranchName": "Python 3.4 running on 64bit Amazon Linux",
                "LifecycleState": "Deprecated", "PlatformName": "Python"},
            {"BranchName": "Python 3.6 running on 64bit Amazon Linux",
                "LifecycleState": "Supported", "PlatformName": "Python"},
            {"BranchName": "Go 1 running on 64bit Amazon Linux",
                "LifecycleState": "Supported", "PlatformName": "Golang"},
        ]
        branch_display_text = [
            'Python 3.6 running on 64bit Amazon Linux',
            'Python 3.7 running on 64bit Amazon Linux 2 (Beta)',
            'Python 3.4 running on 64bit Amazon Linux (Deprecated)',
            'Python 2.7 running on 64bit Amazon Linux (Deprecated)'
        ]

        list_nonretired_platform_branches_mock.return_value = branches
        _sort_platform_branches_for_prompt_mock.return_value = [
            branches[4],
            branches[0],
            branches[3],
            branches[1],
        ]
        prompt_for_index_in_list_mock.return_value = 0
        call_tracker = mock.Mock()
        call_tracker.attach_mock(prompt_for_index_in_list_mock, 'prompt_for_index_in_list_mock')
        call_tracker.attach_mock(echo_mock, 'echo_mock')
        expected = PlatformBranch.from_platform_branch_summary(branches[4])

        result = platformops.prompt_for_platform_branch(family)

        list_nonretired_platform_branches_mock.assert_called_with()
        _sort_platform_branches_for_prompt_mock.assert_called_with([
            branches[0],
            branches[1],
            branches[3],
            branches[4],
        ])
        call_tracker.assert_has_calls(
            [
                mock.call.echo_mock('Select a platform branch.'),
                mock.call.prompt_for_index_in_list_mock(branch_display_text, default=1),
            ],
            any_order=False
        )
        self.assertEqual(expected, result)

    @mock.patch('ebcli.operations.platformops.get_custom_platform_from_customer')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_branch')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_family')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.list_custom_platform_versions')
    def test_prompt_for_platform(
        self,
        list_custom_platform_versions_mock,
        prompt_for_platform_family_mock,
        prompt_for_platform_branch_mock,
        get_custom_platform_from_customer_mock
    ):
        custom_platform_versions = []
        list_custom_platform_versions_mock.return_value = custom_platform_versions
        prompt_for_platform_family_mock.return_value = 'Python'
        prompt_for_platform_branch_mock.return_value = 'Python 3.6 running on 64bit Amazon Linux'

        result = platformops.prompt_for_platform()

        list_custom_platform_versions_mock.assert_called_once_with()
        prompt_for_platform_family_mock.assert_called_once_with(include_custom=False)
        prompt_for_platform_branch_mock.assert_called_once_with('Python')
        get_custom_platform_from_customer_mock.assert_not_called()
        self.assertEqual('Python 3.6 running on 64bit Amazon Linux', result)

    @mock.patch('ebcli.operations.platformops.get_custom_platform_from_customer')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_branch')
    @mock.patch('ebcli.operations.platformops.prompt_for_platform_family')
    @mock.patch('ebcli.operations.platformops.platform_version_ops.list_custom_platform_versions')
    def test_prompt_for_platform__with_custom_platform_versions(
        self,
        list_custom_platform_versions_mock,
        prompt_for_platform_family_mock,
        prompt_for_platform_branch_mock,
        get_custom_platform_from_customer_mock
    ):
        custom_platform_versions = [
            {
                'PlatformOwner': 'self',
                'PlatformStatus': 'Ready',
            }
        ]
        list_custom_platform_versions_mock.return_value = custom_platform_versions
        prompt_for_platform_family_mock.return_value = 'Custom Platform'
        get_custom_platform_from_customer_mock.return_value = 'Custom Platform v1'

        result = platformops.prompt_for_platform()

        list_custom_platform_versions_mock.assert_called_once_with()
        prompt_for_platform_family_mock.assert_called_once_with(include_custom=True)
        prompt_for_platform_branch_mock.assert_not_called()
        get_custom_platform_from_customer_mock.assert_called_once_with(custom_platform_versions)
        self.assertEqual('Custom Platform v1', result)
