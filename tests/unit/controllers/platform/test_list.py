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
from ebcli.controllers.platform.list import GenericPlatformListController
from ebcli.lib import aws
from ebcli.core.ebpcore import EBP
from ebcli.objects.exceptions import (
    ApplicationWorkspaceNotSupportedError,
    InvalidOptionsError,
    NotInitializedError
)
from ebcli.objects.platform import PlatformVersion
from ebcli.objects.solutionstack import SolutionStack


class TestGenericPlatformListController(unittest.TestCase):
    def setUp(self):
        self.controller = GenericPlatformListController()
        self.controller.app = mock.MagicMock()

    @mock.patch('ebcli.controllers.platform.list.fileoperations.get_workspace_type')
    @mock.patch('ebcli.controllers.platform.list.GenericPlatformListController.custom_platforms')
    @mock.patch('ebcli.controllers.platform.list.echo')
    def test_do_command__platform_workspace(
        self,
        echo_mock,
        custom_platforms_mock,
        get_workspace_type_mock,
    ):
        workspace_type = 'Platform'
        custom_platforms_response = [
            'custom-platform-a',
            'custom-platform-b',
            'custom-platform-c',
        ]
        get_workspace_type_mock.return_value = workspace_type
        custom_platforms_mock.return_value = custom_platforms_response

        self.controller.do_command()

        get_workspace_type_mock.assert_called_once_with(None)
        custom_platforms_mock.assert_called_once_with()
        echo_mock.assert_called_once_with(custom_platforms_response)

    @mock.patch('ebcli.controllers.platform.list.fileoperations.get_workspace_type')
    @mock.patch('ebcli.controllers.platform.list.GenericPlatformListController.all_platforms')
    @mock.patch('ebcli.controllers.platform.list.echo')
    def test_do_command__application_workspace(
        self,
        echo_mock,
        all_platforms_mock,
        get_workspace_type_mock,
    ):
        workspace_type = 'Application'
        all_platforms_response = ['python-3.6', 'python-3.7', 'python-3.8']
        get_workspace_type_mock.return_value = workspace_type
        all_platforms_mock.return_value = all_platforms_response
        self.controller.app.pargs.status = False
        self.controller.app.pargs.all_platforms = False

        self.controller.do_command()

        get_workspace_type_mock.assert_called_once_with(None)
        all_platforms_mock.assert_called_once_with()
        echo_mock.assert_called_once_with(all_platforms_response)

    @mock.patch('ebcli.controllers.platform.list.fileoperations.get_workspace_type')
    @mock.patch('ebcli.controllers.platform.list.GenericPlatformListController.all_platforms')
    @mock.patch('ebcli.controllers.platform.list.echo')
    def test_do_command__application_workspace_with_status_option(
        self,
        echo_mock,
        all_platforms_mock,
        get_workspace_type_mock,
    ):
        workspace_type = 'Application'
        all_platforms_response = ['python-3.6', 'python-3.7', 'python-3.8']
        get_workspace_type_mock.return_value = workspace_type
        all_platforms_mock.return_value = all_platforms_response
        self.controller.app.pargs.status = True
        self.controller.app.pargs.all_platforms = False

        self.assertRaisesRegex(
            InvalidOptionsError,
            'You cannot use the "--status" option in application workspaces.',
            self.controller.do_command
        )

    @mock.patch('ebcli.controllers.platform.list.fileoperations.get_workspace_type')
    @mock.patch('ebcli.controllers.platform.list.GenericPlatformListController.all_platforms')
    @mock.patch('ebcli.controllers.platform.list.echo')
    def test_do_command__application_workspace_with_all_platforms_option(
        self,
        echo_mock,
        all_platforms_mock,
        get_workspace_type_mock,
    ):
        workspace_type = 'Application'
        all_platforms_response = ['python-3.6', 'python-3.7', 'python-3.8']
        get_workspace_type_mock.return_value = workspace_type
        all_platforms_mock.return_value = all_platforms_response
        self.controller.app.pargs.status = False
        self.controller.app.pargs.all_platforms = True

        self.assertRaisesRegex(
            InvalidOptionsError,
            'You cannot use the "--all-platforms" option in application workspaces.',
            self.controller.do_command
        )

    @mock.patch('ebcli.controllers.platform.list.fileoperations.get_workspace_type')
    @mock.patch('ebcli.controllers.platform.list.GenericPlatformListController.all_platforms')
    @mock.patch('ebcli.controllers.platform.list.echo')
    def test_do_command__no_workspace(
        self,
        echo_mock,
        all_platforms_mock,
        get_workspace_type_mock,
    ):
        workspace_type = None
        all_platforms_response = ['python-3.6', 'python-3.7', 'python-3.8']
        get_workspace_type_mock.return_value = workspace_type
        all_platforms_mock.return_value = all_platforms_response
        self.controller.app.pargs.status = None
        self.controller.app.pargs.all_platforms = None
        self.controller.app.pargs.region = 'us-east-1'

        self.controller.do_command()

        get_workspace_type_mock.assert_called_once_with(None)
        all_platforms_mock.assert_called_once_with()
        echo_mock.assert_called_once_with(all_platforms_response)

    @mock.patch('ebcli.controllers.platform.list.fileoperations.get_workspace_type')
    @mock.patch('ebcli.controllers.platform.list.GenericPlatformListController.all_platforms')
    @mock.patch('ebcli.controllers.platform.list.echo')
    def test_do_command__no_workspace_sans_region_option(
        self,
        echo_mock,
        all_platforms_mock,
        get_workspace_type_mock,
    ):
        workspace_type = None
        all_platforms_response = ['python-3.6', 'python-3.7', 'python-3.8']
        get_workspace_type_mock.return_value = workspace_type
        all_platforms_mock.return_value = all_platforms_response
        self.controller.app.pargs.status = False
        self.controller.app.pargs.all_platforms = False
        self.controller.app.pargs.region = None

        self.assertRaisesRegex(
            InvalidOptionsError,
            'You must provide the "--region" option when not in a workspace.',
            self.controller.do_command
        )


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


class TestEBPlatformListE2E(ListTest):
    @mock.patch('ebcli.controllers.platform.list.solution_stack_ops.get_all_solution_stacks')
    @mock.patch('ebcli.controllers.platform.list.platform_version_ops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.list.io.echo')
    def test_list__application_workspace__non_verbose_mode(
            self,
            echo_mock,
            list_custom_platform_versions_mock,
            get_all_solution_stacks_mock
    ):
        self.setup_application_workspace()

        get_all_solution_stacks_mock.return_value = [
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

    @mock.patch('ebcli.controllers.platform.list.solution_stack_ops.get_all_solution_stacks')
    @mock.patch('ebcli.controllers.platform.list.platform_version_ops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.list.io.echo')
    def test_list__application_workspace__verbose_mode(
            self,
            echo_mock,
            list_custom_platform_versions_mock,
            get_all_solution_stacks_mock
    ):
        self.setup_application_workspace()

        get_all_solution_stacks_mock.return_value = [
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
    @mock.patch('ebcli.controllers.platform.list.platform_version_ops.list_custom_platform_versions')
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
    @mock.patch('ebcli.controllers.platform.list.platform_version_ops.list_custom_platform_versions')
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
    @mock.patch('ebcli.controllers.platform.list.platform_version_ops.list_custom_platform_versions')
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


class TestEBPList(ListTest):
    @mock.patch('ebcli.controllers.platform.list.solution_stack_ops.get_all_solution_stacks')
    @mock.patch('ebcli.controllers.platform.list.platform_version_ops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.list.io.echo')
    def test_list__application_workspace__non_verbose_mode(
            self,
            echo_mock,
            list_custom_platform_versions_mock,
            get_all_solution_stacks_mock
    ):
        self.setup_application_workspace()

        get_all_solution_stacks_mock.return_value = [
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

    @mock.patch('ebcli.controllers.platform.list.solution_stack_ops.get_all_solution_stacks')
    @mock.patch('ebcli.controllers.platform.list.platform_version_ops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.list.io.echo')
    def test_list__application_workspace__verbose_mode(
            self,
            echo_mock,
            list_custom_platform_versions_mock,
            get_all_solution_stacks_mock
    ):
        self.setup_application_workspace()

        get_all_solution_stacks_mock.return_value = [
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
    @mock.patch('ebcli.controllers.platform.list.platform_version_ops.list_custom_platform_versions')
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
    @mock.patch('ebcli.controllers.platform.list.platform_version_ops.list_custom_platform_versions')
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
    @mock.patch('ebcli.controllers.platform.list.platform_version_ops.list_custom_platform_versions')
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
