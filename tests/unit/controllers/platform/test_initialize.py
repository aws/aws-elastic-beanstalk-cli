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
from pytest_socket import disable_socket, enable_socket
import unittest

from ebcli.core.ebcore import EB
from ebcli.core.ebpcore import EBP
from ebcli.controllers.platform import initialize
from ebcli.lib import aws
from ebcli.objects.platform import PlatformVersion


class TestInitialize(unittest.TestCase):
    platform = PlatformVersion(
        'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5'
    )

    def setUp(self):
        disable_socket()
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        aws.set_region(None)
        os.chdir('testDir')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

        enable_socket()


class TestEBPlatform(TestInitialize):
    @mock.patch('ebcli.controllers.platform.initialize.platformops.set_workspace_to_latest')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.write_keyname')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.touch_config_folder')
    @mock.patch('ebcli.controllers.platform.initialize.get_region_from_inputs')
    @mock.patch('ebcli.controllers.platform.initialize.set_up_credentials')
    @mock.patch('ebcli.controllers.platform.initialize.aws.set_region')
    @mock.patch('ebcli.controllers.platform.initialize.initializeops.setup')
    @mock.patch('ebcli.controllers.platform.initialize.get_platform_name_and_version')
    def test_init__non_interactive_mode(
            self,
            get_platform_name_and_version_mock,
            setup_mock,
            set_region_mock,
            set_up_credentials_mock,
            get_region_from_inputs_mock,
            touch_config_folder_mock,
            write_keyname_mock,
            set_workspace_to_latest_mock
    ):
        get_region_from_inputs_mock.return_value = 'us-west-2'
        get_platform_name_and_version_mock.return_value = ('my-custom-platform', None)
        set_up_credentials_mock.return_value = 'us-west-2'

        app = EB(argv=['platform', 'init', 'my-custom-platform'])
        app.setup()
        app.run()

        set_region_mock.assert_has_calls([mock.call(None), mock.call('us-west-2')])
        set_up_credentials_mock.assert_called_once_with(None, 'us-west-2', False)
        setup_mock.assert_called_once_with(
            'Custom Platform Builder',
            'us-west-2',
            None,
            platform_name='my-custom-platform',
            platform_version=None,
            workspace_type='Platform'
        )
        touch_config_folder_mock.assert_called_once_with()
        write_keyname_mock.assert_called_once_with(None)
        set_workspace_to_latest_mock.assert_called_once_with()

    @mock.patch('ebcli.controllers.platform.initialize.platformops.set_workspace_to_latest')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.write_keyname')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.touch_config_folder')
    @mock.patch('ebcli.controllers.platform.initialize.get_region_from_inputs')
    @mock.patch('ebcli.controllers.platform.initialize.set_up_credentials')
    @mock.patch('ebcli.controllers.platform.initialize.aws.set_region')
    @mock.patch('ebcli.controllers.platform.initialize.initializeops.setup')
    @mock.patch('ebcli.controllers.platform.initialize.get_platform_name_and_version')
    def test_init__non_interactive_mode__keyname_specified(
            self,
            get_platform_name_and_version_mock,
            setup_mock,
            set_region_mock,
            set_up_credentials_mock,
            get_region_from_inputs_mock,
            touch_config_folder_mock,
            write_keyname_mock,
            set_workspace_to_latest_mock
    ):
        get_region_from_inputs_mock.return_value = 'us-west-2'
        get_platform_name_and_version_mock.return_value = ('my-custom-platform', '1.0.3')
        set_up_credentials_mock.return_value = 'us-west-2'

        app = EB(argv=['platform', 'init', 'my-custom-platform', '-k', 'keyname'])
        app.setup()
        app.run()

        set_region_mock.assert_has_calls([mock.call(None), mock.call('us-west-2')])
        set_up_credentials_mock.assert_called_once_with(None, 'us-west-2', False)
        setup_mock.assert_called_once_with(
            'Custom Platform Builder',
            'us-west-2',
            None,
            platform_name='my-custom-platform',
            platform_version='1.0.3',
            workspace_type='Platform'
        )
        touch_config_folder_mock.assert_called_once_with()
        write_keyname_mock.assert_called_once_with('keyname')
        set_workspace_to_latest_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.initialize.platformops.set_workspace_to_latest')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.write_keyname')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.touch_config_folder')
    @mock.patch('ebcli.controllers.platform.initialize.get_region')
    @mock.patch('ebcli.controllers.platform.initialize.set_up_credentials')
    @mock.patch('ebcli.controllers.platform.initialize.aws.set_region')
    @mock.patch('ebcli.controllers.platform.initialize.initializeops.setup')
    @mock.patch('ebcli.controllers.platform.initialize.get_platform_name_and_version')
    @mock.patch('ebcli.controllers.platform.initialize.get_keyname')
    def test_init__force_interactive_mode_by_not_specifying_the_platform(
            self,
            get_keyname_mock,
            get_platform_name_and_version_mock,
            setup_mock,
            set_region_mock,
            set_up_credentials_mock,
            get_region_mock,
            touch_config_folder_mock,
            write_keyname_mock,
            set_workspace_to_latest_mock
    ):
        get_region_mock.return_value = 'us-west-2'
        get_platform_name_and_version_mock.return_value = ('my-custom-platform', '1.0.3')
        set_up_credentials_mock.return_value = 'us-west-2'
        get_keyname_mock.return_value = 'keyname'

        app = EB(argv=['platform', 'init'])
        app.setup()
        app.run()

        set_region_mock.assert_has_calls([mock.call(None), mock.call('us-west-2')])
        set_up_credentials_mock.assert_called_once_with(None, 'us-west-2', True)
        setup_mock.assert_called_once_with(
            'Custom Platform Builder',
            'us-west-2',
            None,
            platform_name='my-custom-platform',
            platform_version='1.0.3',
            workspace_type='Platform'
        )
        get_region_mock.assert_called_once_with(None, True)
        touch_config_folder_mock.assert_called_once_with()
        write_keyname_mock.assert_called_once_with('keyname')
        set_workspace_to_latest_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.initialize.platformops.set_workspace_to_latest')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.write_keyname')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.touch_config_folder')
    @mock.patch('ebcli.controllers.platform.initialize.get_region')
    @mock.patch('ebcli.controllers.platform.initialize.set_up_credentials')
    @mock.patch('ebcli.controllers.platform.initialize.aws.set_region')
    @mock.patch('ebcli.controllers.platform.initialize.initializeops.setup')
    @mock.patch('ebcli.controllers.platform.initialize.get_platform_name_and_version')
    @mock.patch('ebcli.controllers.platform.initialize.get_keyname')
    def test_init__force_interactive_mode_by_passing_interactive_argument(
            self,
            get_keyname_mock,
            get_platform_name_and_version_mock,
            setup_mock,
            set_region_mock,
            set_up_credentials_mock,
            get_region_mock,
            touch_config_folder_mock,
            write_keyname_mock,
            set_workspace_to_latest_mock
    ):
        get_region_mock.return_value = 'us-west-2'
        get_platform_name_and_version_mock.return_value = ('my-custom-platform', '1.0.3')
        set_up_credentials_mock.return_value = 'us-west-2'
        get_keyname_mock.return_value = 'keyname'

        app = EB(argv=['platform', 'init', 'my-custom-platform', '-i'])
        app.setup()
        app.run()

        set_region_mock.assert_has_calls([mock.call(None), mock.call('us-west-2')])
        set_up_credentials_mock.assert_called_once_with(None, 'us-west-2', True)
        setup_mock.assert_called_once_with(
            'Custom Platform Builder',
            'us-west-2',
            None,
            platform_name='my-custom-platform',
            platform_version='1.0.3',
            workspace_type='Platform'
        )
        get_region_mock.assert_called_once_with(None, True)
        touch_config_folder_mock.assert_called_once_with()
        write_keyname_mock.assert_called_once_with('keyname')
        set_workspace_to_latest_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.initialize.platformops.set_workspace_to_latest')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.write_keyname')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.touch_config_folder')
    @mock.patch('ebcli.controllers.platform.initialize.get_region')
    @mock.patch('ebcli.controllers.platform.initialize.set_up_credentials')
    @mock.patch('ebcli.controllers.platform.initialize.aws.set_region')
    @mock.patch('ebcli.controllers.platform.initialize.initializeops.setup')
    @mock.patch('ebcli.controllers.platform.initialize.get_platform_name_and_version')
    @mock.patch('ebcli.controllers.platform.initialize.get_keyname')
    def test_init__force_interactive_mode_by_passing_interactive_argument_and_omitting_platform_argument(
            self,
            get_keyname_mock,
            get_platform_name_and_version_mock,
            setup_mock,
            set_region_mock,
            set_up_credentials_mock,
            get_region_mock,
            touch_config_folder_mock,
            write_keyname_mock,
            set_workspace_to_latest_mock
    ):
        get_region_mock.return_value = 'us-west-2'
        get_platform_name_and_version_mock.return_value = ('my-custom-platform', '1.0.3')
        set_up_credentials_mock.return_value = 'us-west-2'
        get_keyname_mock.return_value = 'keyname'

        app = EB(argv=['platform', 'init', '-i'])
        app.setup()
        app.run()

        set_region_mock.assert_has_calls([mock.call(None), mock.call('us-west-2')])
        set_up_credentials_mock.assert_called_once_with(None, 'us-west-2', True)
        setup_mock.assert_called_once_with(
            'Custom Platform Builder',
            'us-west-2',
            None,
            platform_name='my-custom-platform',
            platform_version='1.0.3',
            workspace_type='Platform'
        )
        get_region_mock.assert_called_once_with(None, True)
        touch_config_folder_mock.assert_called_once_with()
        write_keyname_mock.assert_called_once_with('keyname')
        set_workspace_to_latest_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.initialize.platformops.set_workspace_to_latest')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.write_keyname')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.touch_config_folder')
    @mock.patch('ebcli.controllers.platform.initialize.get_region')
    @mock.patch('ebcli.controllers.platform.initialize.set_up_credentials')
    @mock.patch('ebcli.controllers.platform.initialize.aws.set_region')
    @mock.patch('ebcli.controllers.platform.initialize.initializeops.setup')
    @mock.patch('ebcli.controllers.platform.initialize.get_platform_name_and_version')
    @mock.patch('ebcli.controllers.platform.initialize.get_keyname')
    def test_init__interactive_mode__pass_keyname_in_interactive(
            self,
            get_keyname_mock,
            get_platform_name_and_version_mock,
            setup_mock,
            set_region_mock,
            set_up_credentials_mock,
            get_region_mock,
            touch_config_folder_mock,
            write_keyname_mock,
            set_workspace_to_latest_mock
    ):
        get_region_mock.return_value = 'us-west-2'
        get_platform_name_and_version_mock.return_value = ('my-custom-platform', '1.0.3')
        set_up_credentials_mock.return_value = 'us-west-2'

        app = EB(argv=['platform', 'init', '-k', 'keyname'])
        app.setup()
        app.run()

        set_region_mock.assert_has_calls([mock.call(None), mock.call('us-west-2')])
        set_up_credentials_mock.assert_called_once_with(None, 'us-west-2', True)
        setup_mock.assert_called_once_with(
            'Custom Platform Builder',
            'us-west-2',
            None,
            platform_name='my-custom-platform',
            platform_version='1.0.3',
            workspace_type='Platform'
        )
        get_region_mock.assert_called_once_with(None, True)
        touch_config_folder_mock.assert_called_once_with()
        write_keyname_mock.assert_called_once_with('keyname')
        set_workspace_to_latest_mock.assert_not_called()
        get_keyname_mock.assert_not_called()


class TestEBP(TestInitialize):
    @mock.patch('ebcli.controllers.platform.initialize.platformops.set_workspace_to_latest')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.write_keyname')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.touch_config_folder')
    @mock.patch('ebcli.controllers.platform.initialize.get_region_from_inputs')
    @mock.patch('ebcli.controllers.platform.initialize.set_up_credentials')
    @mock.patch('ebcli.controllers.platform.initialize.aws.set_region')
    @mock.patch('ebcli.controllers.platform.initialize.initializeops.setup')
    @mock.patch('ebcli.controllers.platform.initialize.get_platform_name_and_version')
    def test_init__non_interactive_mode(
            self,
            get_platform_name_and_version_mock,
            setup_mock,
            set_region_mock,
            set_up_credentials_mock,
            get_region_from_inputs_mock,
            touch_config_folder_mock,
            write_keyname_mock,
            set_workspace_to_latest_mock
    ):
        get_region_from_inputs_mock.return_value = 'us-west-2'
        get_platform_name_and_version_mock.return_value = ('my-custom-platform', None)
        set_up_credentials_mock.return_value = 'us-west-2'

        app = EBP(argv=['init', 'my-custom-platform'])
        app.setup()
        app.run()

        set_region_mock.assert_has_calls([mock.call(None), mock.call('us-west-2')])
        set_up_credentials_mock.assert_called_once_with(None, 'us-west-2', False)
        setup_mock.assert_called_once_with(
            'Custom Platform Builder',
            'us-west-2',
            None,
            platform_name='my-custom-platform',
            platform_version=None,
            workspace_type='Platform'
        )
        touch_config_folder_mock.assert_called_once_with()
        write_keyname_mock.assert_called_once_with(None)
        set_workspace_to_latest_mock.assert_called_once_with()

    @mock.patch('ebcli.controllers.platform.initialize.platformops.set_workspace_to_latest')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.write_keyname')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.touch_config_folder')
    @mock.patch('ebcli.controllers.platform.initialize.get_region_from_inputs')
    @mock.patch('ebcli.controllers.platform.initialize.set_up_credentials')
    @mock.patch('ebcli.controllers.platform.initialize.aws.set_region')
    @mock.patch('ebcli.controllers.platform.initialize.initializeops.setup')
    @mock.patch('ebcli.controllers.platform.initialize.get_platform_name_and_version')
    def test_init__non_interactive_mode__keyname_specified(
            self,
            get_platform_name_and_version_mock,
            setup_mock,
            set_region_mock,
            set_up_credentials_mock,
            get_region_from_inputs_mock,
            touch_config_folder_mock,
            write_keyname_mock,
            set_workspace_to_latest_mock
    ):
        get_region_from_inputs_mock.return_value = 'us-west-2'
        get_platform_name_and_version_mock.return_value = ('my-custom-platform', '1.0.3')
        set_up_credentials_mock.return_value = 'us-west-2'

        app = EBP(argv=['init', 'my-custom-platform', '-k', 'keyname'])
        app.setup()
        app.run()

        set_region_mock.assert_has_calls([mock.call(None), mock.call('us-west-2')])
        set_up_credentials_mock.assert_called_once_with(None, 'us-west-2', False)
        setup_mock.assert_called_once_with(
            'Custom Platform Builder',
            'us-west-2',
            None,
            platform_name='my-custom-platform',
            platform_version='1.0.3',
            workspace_type='Platform'
        )
        touch_config_folder_mock.assert_called_once_with()
        write_keyname_mock.assert_called_once_with('keyname')
        set_workspace_to_latest_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.initialize.platformops.set_workspace_to_latest')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.write_keyname')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.touch_config_folder')
    @mock.patch('ebcli.controllers.platform.initialize.get_region')
    @mock.patch('ebcli.controllers.platform.initialize.set_up_credentials')
    @mock.patch('ebcli.controllers.platform.initialize.aws.set_region')
    @mock.patch('ebcli.controllers.platform.initialize.initializeops.setup')
    @mock.patch('ebcli.controllers.platform.initialize.get_platform_name_and_version')
    @mock.patch('ebcli.controllers.platform.initialize.get_keyname')
    def test_init__force_interactive_mode_by_not_specifying_the_platform(
            self,
            get_keyname_mock,
            get_platform_name_and_version_mock,
            setup_mock,
            set_region_mock,
            set_up_credentials_mock,
            get_region_mock,
            touch_config_folder_mock,
            write_keyname_mock,
            set_workspace_to_latest_mock
    ):
        get_region_mock.return_value = 'us-west-2'
        get_platform_name_and_version_mock.return_value = ('my-custom-platform', '1.0.3')
        set_up_credentials_mock.return_value = 'us-west-2'
        get_keyname_mock.return_value = 'keyname'

        app = EBP(argv=['init'])
        app.setup()
        app.run()

        set_region_mock.assert_has_calls([mock.call(None), mock.call('us-west-2')])
        set_up_credentials_mock.assert_called_once_with(None, 'us-west-2', True)
        setup_mock.assert_called_once_with(
            'Custom Platform Builder',
            'us-west-2',
            None,
            platform_name='my-custom-platform',
            platform_version='1.0.3',
            workspace_type='Platform'
        )
        get_region_mock.assert_called_once_with(None, True)
        touch_config_folder_mock.assert_called_once_with()
        write_keyname_mock.assert_called_once_with('keyname')
        set_workspace_to_latest_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.initialize.platformops.set_workspace_to_latest')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.write_keyname')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.touch_config_folder')
    @mock.patch('ebcli.controllers.platform.initialize.get_region')
    @mock.patch('ebcli.controllers.platform.initialize.set_up_credentials')
    @mock.patch('ebcli.controllers.platform.initialize.aws.set_region')
    @mock.patch('ebcli.controllers.platform.initialize.initializeops.setup')
    @mock.patch('ebcli.controllers.platform.initialize.get_platform_name_and_version')
    @mock.patch('ebcli.controllers.platform.initialize.get_keyname')
    def test_init__force_interactive_mode_by_passing_interactive_argument(
            self,
            get_keyname_mock,
            get_platform_name_and_version_mock,
            setup_mock,
            set_region_mock,
            set_up_credentials_mock,
            get_region_mock,
            touch_config_folder_mock,
            write_keyname_mock,
            set_workspace_to_latest_mock
    ):
        get_region_mock.return_value = 'us-west-2'
        get_platform_name_and_version_mock.return_value = ('my-custom-platform', '1.0.3')
        set_up_credentials_mock.return_value = 'us-west-2'
        get_keyname_mock.return_value = 'keyname'

        app = EBP(argv=['init', 'my-custom-platform', '-i'])
        app.setup()
        app.run()

        set_region_mock.assert_has_calls([mock.call(None), mock.call('us-west-2')])
        set_up_credentials_mock.assert_called_once_with(None, 'us-west-2', True)
        setup_mock.assert_called_once_with(
            'Custom Platform Builder',
            'us-west-2',
            None,
            platform_name='my-custom-platform',
            platform_version='1.0.3',
            workspace_type='Platform'
        )
        get_region_mock.assert_called_once_with(None, True)
        touch_config_folder_mock.assert_called_once_with()
        write_keyname_mock.assert_called_once_with('keyname')
        set_workspace_to_latest_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.initialize.platformops.set_workspace_to_latest')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.write_keyname')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.touch_config_folder')
    @mock.patch('ebcli.controllers.platform.initialize.get_region')
    @mock.patch('ebcli.controllers.platform.initialize.set_up_credentials')
    @mock.patch('ebcli.controllers.platform.initialize.aws.set_region')
    @mock.patch('ebcli.controllers.platform.initialize.initializeops.setup')
    @mock.patch('ebcli.controllers.platform.initialize.get_platform_name_and_version')
    @mock.patch('ebcli.controllers.platform.initialize.get_keyname')
    def test_init__force_interactive_mode_by_passing_interactive_argument_and_omitting_platform_argument(
            self,
            get_keyname_mock,
            get_platform_name_and_version_mock,
            setup_mock,
            set_region_mock,
            set_up_credentials_mock,
            get_region_mock,
            touch_config_folder_mock,
            write_keyname_mock,
            set_workspace_to_latest_mock
    ):
        get_region_mock.return_value = 'us-west-2'
        get_platform_name_and_version_mock.return_value = ('my-custom-platform', '1.0.3')
        set_up_credentials_mock.return_value = 'us-west-2'
        get_keyname_mock.return_value = 'keyname'

        app = EBP(argv=['init', '-i'])
        app.setup()
        app.run()

        set_region_mock.assert_has_calls([mock.call(None), mock.call('us-west-2')])
        set_up_credentials_mock.assert_called_once_with(None, 'us-west-2', True)
        setup_mock.assert_called_once_with(
            'Custom Platform Builder',
            'us-west-2',
            None,
            platform_name='my-custom-platform',
            platform_version='1.0.3',
            workspace_type='Platform'
        )
        get_region_mock.assert_called_once_with(None, True)
        touch_config_folder_mock.assert_called_once_with()
        write_keyname_mock.assert_called_once_with('keyname')
        set_workspace_to_latest_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.initialize.platformops.set_workspace_to_latest')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.write_keyname')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.touch_config_folder')
    @mock.patch('ebcli.controllers.platform.initialize.get_region')
    @mock.patch('ebcli.controllers.platform.initialize.set_up_credentials')
    @mock.patch('ebcli.controllers.platform.initialize.aws.set_region')
    @mock.patch('ebcli.controllers.platform.initialize.initializeops.setup')
    @mock.patch('ebcli.controllers.platform.initialize.get_platform_name_and_version')
    @mock.patch('ebcli.controllers.platform.initialize.get_keyname')
    def test_init__interactive_mode__pass_keyname_in_interactive(
            self,
            get_keyname_mock,
            get_platform_name_and_version_mock,
            setup_mock,
            set_region_mock,
            set_up_credentials_mock,
            get_region_mock,
            touch_config_folder_mock,
            write_keyname_mock,
            set_workspace_to_latest_mock
    ):
        get_region_mock.return_value = 'us-west-2'
        get_platform_name_and_version_mock.return_value = ('my-custom-platform', '1.0.3')
        set_up_credentials_mock.return_value = 'us-west-2'

        app = EBP(argv=['init', '-k', 'keyname'])
        app.setup()
        app.run()

        set_region_mock.assert_has_calls([mock.call(None), mock.call('us-west-2')])
        set_up_credentials_mock.assert_called_once_with(None, 'us-west-2', True)
        setup_mock.assert_called_once_with(
            'Custom Platform Builder',
            'us-west-2',
            None,
            platform_name='my-custom-platform',
            platform_version='1.0.3',
            workspace_type='Platform'
        )
        get_region_mock.assert_called_once_with(None, True)
        touch_config_folder_mock.assert_called_once_with()
        write_keyname_mock.assert_called_once_with('keyname')
        set_workspace_to_latest_mock.assert_not_called()
        get_keyname_mock.assert_not_called()


class TestGenericPlatformInitController(unittest.TestCase):
    @mock.patch('ebcli.controllers.platform.initialize.commonops.get_default_keyname')
    @mock.patch('ebcli.controllers.platform.initialize.sshops.prompt_for_ec2_keyname')
    def test_get_keyname__found_default_keyname(
            self,
            prompt_for_ec2_keyname_mock,
            get_default_keyname_mock
    ):
        get_default_keyname_mock.return_value = 'keyname'

        self.assertEqual(
            'keyname',
            initialize.get_keyname()
        )

        prompt_for_ec2_keyname_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.initialize.commonops.get_default_keyname')
    @mock.patch('ebcli.controllers.platform.initialize.sshops.prompt_for_ec2_keyname')
    def test_get_keyname__could_not_find_default_keyname(
            self,
            prompt_for_ec2_keyname_mock,
            get_default_keyname_mock
    ):
        get_default_keyname_mock.return_value = None
        prompt_for_ec2_keyname_mock.return_value = 'keyname'

        self.assertEqual(
            'keyname',
            initialize.get_keyname()
        )

        prompt_for_ec2_keyname_mock.assert_called_once_with(
            message='Would you like to be able to log into your platform packer environment?'
        )

    @mock.patch('ebcli.controllers.platform.initialize.platformops.get_platform_name_and_version_interactive')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.get_platform_version')
    def test_get_platform_name_and_version__platform_name_specified__non_interactive_flow(
            self,
            get_platform_version_mock,
            get_platform_name_mock,
            get_platform_name_and_version_interactive_mock
    ):
        self.assertEqual(
            ('my-custom-platform', None),
            initialize.get_platform_name_and_version('my-custom-platform')
        )

        get_platform_version_mock.assert_not_called()
        get_platform_name_mock.assert_not_called()
        get_platform_name_and_version_interactive_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.initialize.platformops.get_platform_name_and_version_interactive')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.get_platform_version')
    def test_get_platform_name_and_version__platform_name_not_specified__force_interactive_flow__default_platform_found(
            self,
            get_platform_version_mock,
            get_platform_name_mock,
            get_platform_name_and_version_interactive_mock
    ):
        get_platform_name_mock.return_value = 'my-custom-platform'
        get_platform_version_mock.return_value = '1.0.3'

        self.assertEqual(
            ('my-custom-platform', '1.0.3'),
            initialize.get_platform_name_and_version(None)
        )

        get_platform_name_mock.assert_called_once_with(default=None)
        get_platform_version_mock.assert_called_once_with()
        get_platform_name_and_version_interactive_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.initialize.platformops.get_platform_name_and_version_interactive')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.initialize.fileoperations.get_platform_version')
    def test_get_platform_name_and_version__platform_name_not_specified__default_platform_not_found__customer_prompted_for_paltform_name(
            self,
            get_platform_version_mock,
            get_platform_name_mock,
            get_platform_name_and_version_interactive_mock
    ):
        get_platform_name_mock.side_effect = initialize.NotInitializedError
        get_platform_name_and_version_interactive_mock.return_value = ('my-custom-platform', '1.0.3')

        self.assertEqual(
            ('my-custom-platform', '1.0.3'),
            initialize.get_platform_name_and_version(None)
        )

        get_platform_name_mock.assert_called_once_with(default=None)
        get_platform_version_mock.assert_not_called()
        get_platform_name_and_version_interactive_mock.assert_called_once_with()
