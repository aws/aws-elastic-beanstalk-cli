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
    def test_delete_no_environments(
            self,
            commonops_mock,
            elasticbeanstalk_mock,
            io_mock
    ):
        platformops._version_to_arn = mock.Mock(return_value=self.platform_arn)
        elasticbeanstalk_mock.get_environments.return_value = []
        elasticbeanstalk_mock.delete_platform.return_value = { 'ResponseMetadata': { 'RequestId': 'request-id' } }
        
        platformops.delete_platform_version(self.platform_arn, False)

        elasticbeanstalk_mock.get_environments.assert_called_with()
        elasticbeanstalk_mock.delete_platform.assert_called_with(self.platform_arn)

    @mock.patch('ebcli.operations.platformops.io')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk')
    @mock.patch('ebcli.operations.platformops.commonops')
    def test_delete_with_environments(
            self,
            commonops_mock,
            elasticbeanstalk_mock,
            io_mock
    ):
        platformops._version_to_arn = mock.Mock(return_value=self.platform_arn)
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
