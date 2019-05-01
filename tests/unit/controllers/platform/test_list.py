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

from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
from ebcli.lib import aws
from ebcli.core.ebpcore import EBP
from ebcli.objects.exceptions import (
    ApplicationWorkspaceNotSupportedError,
    InvalidOptionsError,
    NotInitializedError
)
from ebcli.objects.platform import PlatformVersion
from ebcli.objects.solutionstack import SolutionStack


class ListTest(unittest.TestCase):
    platform = PlatformVersion(
        'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5'
    )
    solution_stack = SolutionStack(
        '64bit Amazon Linux 2017.09 v4.4.0 running Node.js'
    )

    def setUp(self):
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        os.chdir('testDir')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')
        aws.set_region(None)

    def setup_platform_workspace(self):
        fileoperations.create_config_file(
            'my-platform',
            'us-west-2',
            self.platform.name,
            workspace_type='Platform'
        )

    def setup_application_workspace(self):
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            self.solution_stack.name,
            workspace_type='Application'
        )


class TestEBPlatformList(ListTest):
    @mock.patch('ebcli.controllers.platform.list.platformops.get_all_platforms')
    @mock.patch('ebcli.controllers.platform.list.platformops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.list.io.echo')
    def test_list__application_workspace__non_verbose_mode(
            self,
            echo_mock,
            list_custom_platform_versions_mock,
            get_all_platforms_mock
    ):
        self.setup_application_workspace()

        get_all_platforms_mock.return_value = [
            SolutionStack('64bit Amazon Linux 2017.09 v4.4.0 running Node.js'),
            SolutionStack('64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4')

        ]
        list_custom_platform_versions_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-5/1.3.6'
        ]

        app = EB(argv=['platform', 'list'])
        app.setup()
        app.run()

        echo_mock.assert_called_once_with(
            'node.js', 'php-5.4', 'custom-platform-4', 'custom-platform-5', sep='{linesep}'.format(linesep=os.linesep)
        )

    @mock.patch('ebcli.controllers.platform.list.platformops.get_all_platforms')
    @mock.patch('ebcli.controllers.platform.list.platformops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.list.io.echo')
    def test_list__application_workspace__verbose_mode(
            self,
            echo_mock,
            list_custom_platform_versions_mock,
            get_all_platforms_mock
    ):
        self.setup_application_workspace()

        get_all_platforms_mock.return_value = [
            SolutionStack('64bit Amazon Linux 2017.09 v4.4.0 running Node.js'),
            SolutionStack('64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4')

        ]
        list_custom_platform_versions_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-5/1.3.6'
        ]

        app = EB(argv=['platform', 'list', '--verbose'])
        app.setup()
        app.run()

        echo_mock.assert_called_once_with(
            '64bit Amazon Linux 2017.09 v4.4.0 running Node.js',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-5/1.3.6',
            sep='{linesep}'.format(linesep=os.linesep)
        )

    @mock.patch('ebcli.controllers.platform.list.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.list.platformops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.list.io.echo')
    def test_list__platform_workspace__all_versions_of_this_platform(
            self,
            echo_mock,
            list_custom_platform_versions_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        get_platform_name_mock.return_value = 'custom-platform-4'
        list_custom_platform_versions_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.3.6'
        ]

        app = EB(argv=['platform', 'list'])
        app.setup()
        app.run()

        list_custom_platform_versions_mock.assert_called_once_with(
            platform_name='custom-platform-4',
            show_status=True,
            status=None
        )
        echo_mock.assert_called_once_with(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.3.6',
            sep='{linesep}'.format(linesep=os.linesep)
        )

    @mock.patch('ebcli.controllers.platform.list.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.list.platformops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.list.io.echo')
    def test_list__platform_workspace__all_versions_of_all_platforms(
            self,
            echo_mock,
            list_custom_platform_versions_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        list_custom_platform_versions_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.3.6'
        ]

        app = EB(argv=['platform', 'list', '-a'])
        app.setup()
        app.run()

        get_platform_name_mock.assert_not_called()
        list_custom_platform_versions_mock.assert_called_once_with(
            platform_name=None,
            show_status=True,
            status=None
        )
        echo_mock.assert_called_once_with(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.3.6',
            sep='{linesep}'.format(linesep=os.linesep)
        )

    @mock.patch('ebcli.controllers.platform.list.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.list.platformops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.list.io.echo')
    def test_list__platform_workspace__filter_by_status(
            self,
            echo_mock,
            list_custom_platform_versions_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        list_custom_platform_versions_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.3.6'
        ]

        app = EB(argv=['platform', 'list', '-a', '-s', 'READY'])
        app.setup()
        app.run()

        get_platform_name_mock.assert_not_called()
        list_custom_platform_versions_mock.assert_called_once_with(
            platform_name=None,
            show_status=True,
            status='READY'
        )
        echo_mock.assert_called_once_with(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.3.6',
            sep='{linesep}'.format(linesep=os.linesep)
        )

    def test_list__neutral_workspace__all_platforms_and_status_filters_are_not_applicable(self):
        self.setup_platform_workspace()
        fileoperations.write_config_setting(
            'global',
            'workspace_type',
            None
        )

        app = EB(argv=['platform', 'list', '-a', '-s', 'READY'])
        app.setup()
        app.run()


class TestEBPList(ListTest):
    @mock.patch('ebcli.controllers.platform.list.platformops.get_all_platforms')
    @mock.patch('ebcli.controllers.platform.list.platformops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.list.io.echo')
    def test_list__application_workspace__non_verbose_mode(
            self,
            echo_mock,
            list_custom_platform_versions_mock,
            get_all_platforms_mock
    ):
        self.setup_application_workspace()

        get_all_platforms_mock.return_value = [
            SolutionStack('64bit Amazon Linux 2017.09 v4.4.0 running Node.js'),
            SolutionStack('64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4')

        ]
        list_custom_platform_versions_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-5/1.3.6'
        ]

        app = EBP(argv=['list'])
        app.setup()
        app.run()

        echo_mock.assert_called_once_with(
            'node.js', 'php-5.4', 'custom-platform-4', 'custom-platform-5', sep='{linesep}'.format(linesep=os.linesep)
        )

    @mock.patch('ebcli.controllers.platform.list.platformops.get_all_platforms')
    @mock.patch('ebcli.controllers.platform.list.platformops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.list.io.echo')
    def test_list__application_workspace__verbose_mode(
            self,
            echo_mock,
            list_custom_platform_versions_mock,
            get_all_platforms_mock
    ):
        self.setup_application_workspace()

        get_all_platforms_mock.return_value = [
            SolutionStack('64bit Amazon Linux 2017.09 v4.4.0 running Node.js'),
            SolutionStack('64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4')

        ]
        list_custom_platform_versions_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-5/1.3.6'
        ]

        app = EBP(argv=['list', '--verbose'])
        app.setup()
        app.run()

        echo_mock.assert_called_once_with(
            '64bit Amazon Linux 2017.09 v4.4.0 running Node.js',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-5/1.3.6',
            sep='{linesep}'.format(linesep=os.linesep)
        )

    @mock.patch('ebcli.controllers.platform.list.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.list.platformops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.list.io.echo')
    def test_list__platform_workspace__all_versions_of_this_platform(
            self,
            echo_mock,
            list_custom_platform_versions_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        get_platform_name_mock.return_value = 'custom-platform-4'
        list_custom_platform_versions_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.3.6'
        ]

        app = EBP(argv=['list'])
        app.setup()
        app.run()

        list_custom_platform_versions_mock.assert_called_once_with(
            platform_name='custom-platform-4',
            show_status=True,
            status=None
        )
        echo_mock.assert_called_once_with(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.3.6',
            sep='{linesep}'.format(linesep=os.linesep)
        )

    @mock.patch('ebcli.controllers.platform.list.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.list.platformops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.list.io.echo')
    def test_list__platform_workspace__all_versions_of_all_platforms(
            self,
            echo_mock,
            list_custom_platform_versions_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        list_custom_platform_versions_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.3.6'
        ]

        app = EBP(argv=['list', '-a'])
        app.setup()
        app.run()

        get_platform_name_mock.assert_not_called()
        list_custom_platform_versions_mock.assert_called_once_with(
            platform_name=None,
            show_status=True,
            status=None
        )
        echo_mock.assert_called_once_with(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.3.6',
            sep='{linesep}'.format(linesep=os.linesep)
        )

    @mock.patch('ebcli.controllers.platform.list.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.list.platformops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.list.io.echo')
    def test_list__platform_workspace__filter_by_status(
            self,
            echo_mock,
            list_custom_platform_versions_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        list_custom_platform_versions_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.3.6'
        ]

        app = EBP(argv=['list', '-a', '-s', 'READY'])
        app.setup()
        app.run()

        get_platform_name_mock.assert_not_called()
        list_custom_platform_versions_mock.assert_called_once_with(
            platform_name=None,
            show_status=True,
            status='READY'
        )
        echo_mock.assert_called_once_with(
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3',
            'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.3.6',
            sep='{linesep}'.format(linesep=os.linesep)
        )

    def test_list__neutral_workspace__command_is_not_applicable(self):
        self.setup_platform_workspace()
        fileoperations.write_config_setting(
            'global',
            'workspace_type',
            None
        )

        app = EBP(argv=['list'])
        app.setup()
        app.run()
