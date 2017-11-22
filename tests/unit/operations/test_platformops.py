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
import sys
import shutil
import mock
import unittest

from mock import Mock

from ebcli.core.ebglobals import Constants
from ebcli.operations import platformops
from ebcli.resources.strings import strings, responses, prompts
from ebcli.objects.exceptions import ValidationError
from ebcli.objects.environment import Environment
from ebcli.objects.platform import PlatformVersion

class TestPlatformOperations(unittest.TestCase):

    def setUp(self):
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
        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            shutil.rmtree('testDir')

    @mock.patch('ebcli.operations.platformops.io')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk')
    @mock.patch('ebcli.operations.platformops.commonops')
    def test_delete_no_environments(self, mock_io, mock_elasticbeanstalk, mock_commonops):
        platformops._version_to_arn = Mock(return_value=self.platform_arn)
        mock_elasticbeanstalk.get_environments.return_value = []
        mock_elasticbeanstalk.delete_platform.return_value = { 'ResponseMetadata': { 'RequestId': 'request-id' } }
        
        platformops.delete_platform_version(self.platform_arn, False)

        mock_elasticbeanstalk.get_environments.assert_called_with()
        mock_elasticbeanstalk.delete_platform.assert_called_with(self.platform_arn)

    @mock.patch('ebcli.operations.platformops.io')
    @mock.patch('ebcli.operations.platformops.elasticbeanstalk')
    @mock.patch('ebcli.operations.platformops.commonops')
    def test_delete_with_environments(self, mock_io, mock_elasticbeanstalk, mock_commonops):
        platformops._version_to_arn = Mock(return_value=self.platform_arn)
        environments = [ 
                Environment(name='env1', platform=PlatformVersion(self.platform_arn)),
                Environment(name='no match', platform=PlatformVersion('arn:aws:elasticbeanstalk:us-east-1:647823116501:platform/foo/2.0.0')),
                Environment(name='env2', platform=PlatformVersion(self.platform_arn))
        ]

        mock_elasticbeanstalk.get_environments.return_value = environments
        mock_elasticbeanstalk.delete_platform.return_value = { 'ResponseMetadata': { 'RequestId': 'request-id' } }
        
        self.assertRaises(ValidationError, platformops.delete_platform_version, self.platform_arn, False)

        mock_elasticbeanstalk.get_environments.assert_called_with()


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
