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
import os
import shutil

import mock
import unittest

from ebcli.core.ebcore import EB
from ebcli.core.ebpcore import EBP
from ebcli.core import fileoperations
from ebcli.objects.platform import PlatformVersion


class TestEvents(unittest.TestCase):
    platform = PlatformVersion(
        'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5'
    )

    def setUp(self):
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        os.chdir('testDir')

        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            self.platform.name,
            workspace_type='Platform'
        )

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')


class TestEB(TestEvents):
    @mock.patch('ebcli.controllers.platform.events.show_platform_events')
    def test_events(
            self,
            show_platform_events_mock
    ):
        app = EB(argv=['platform', 'events'])
        app.setup()
        app.run()

        show_platform_events_mock.assert_called_once_with(
            False,
            None
        )

    @mock.patch('ebcli.controllers.platform.events.show_platform_events')
    def test_events__follow(
            self,
            show_platform_events_mock
    ):
        app = EB(argv=['platform', 'events', '--follow'])
        app.setup()
        app.run()

        show_platform_events_mock.assert_called_once_with(
            True,
            None
        )


class TestEBP(TestEvents):
    @mock.patch('ebcli.controllers.platform.events.show_platform_events')
    def test_events(
            self,
            show_platform_events_mock
    ):
        app = EBP(argv=['events'])
        app.setup()
        app.run()

        show_platform_events_mock.assert_called_once_with(
            False,
            None
        )

    @mock.patch('ebcli.controllers.platform.events.show_platform_events')
    def test_events__follow(
            self,
            show_platform_events_mock
    ):
        app = EBP(argv=['events', '--follow'])
        app.setup()
        app.run()

        show_platform_events_mock.assert_called_once_with(
            True,
            None
        )