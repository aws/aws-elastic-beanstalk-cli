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
from ebcli.core import fileoperations
from ebcli.objects.platform import PlatformVersion


class TestCreate(unittest.TestCase):
    platform = PlatformVersion(
        'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5'
    )

    def setUp(self):
        disable_socket()
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

        enable_socket()


class TestEBPlatform(TestCreate):
    @mock.patch('ebcli.controllers.platform.create.fileoperations.get_instance_profile')
    @mock.patch('ebcli.controllers.platform.create.create_platform_version')
    def test_create__pass_major_minor_and_patch_versions(
            self,
            create_platform_version_mock,
            get_instance_profile_mock
    ):
        get_instance_profile_mock.return_value = 'my-instance-profile'

        app = EB(argv=['platform', 'create', '1.1.1', '-M', '-m', '-p'])
        app.setup()
        app.run()

        create_platform_version_mock.assert_called_once_with(
            '1.1.1',
            True,
            True,
            True,
            None,
            {
                'id': None,
                'subnets': None,
                'publicip': False
            }
        )

    @mock.patch('ebcli.controllers.platform.create.fileoperations.get_instance_profile')
    @mock.patch('ebcli.controllers.platform.create.create_platform_version')
    def test_create__pass_instance_type(
            self,
            create_platform_version_mock,
            get_instance_profile_mock
    ):
        get_instance_profile_mock.return_value = 'my-instance-profile'

        app = EB(argv=['platform', 'create', '-i', 'c4x.large'])
        app.setup()
        app.run()

        create_platform_version_mock.assert_called_once_with(
            None,
            False,
            False,
            False,
            'c4x.large',
            {
                'id': None,
                'subnets': None,
                'publicip': False
            }
        )

    @mock.patch('ebcli.controllers.platform.create.fileoperations.get_instance_profile')
    @mock.patch('ebcli.controllers.platform.create.create_platform_version')
    def test_create__pass_instance_type_instance_profile_and_vpc_parameters(
            self,
            create_platform_version_mock,
            get_instance_profile_mock
    ):
        get_instance_profile_mock.return_value = 'my-instance-profile'

        app = EB(
            argv=[
                'platform',
                'create',
                '-i', 'c4x.large',
                '-ip', 'my-instance-profile',
                '--vpc.id', 'vpc-123124',
                '--vpc.subnets', 'subnet-123123,subnet-2334545',
                '--vpc.publicip'
            ])
        app.setup()
        app.run()

        create_platform_version_mock.assert_called_once_with(
            None,
            False,
            False,
            False,
            'c4x.large',
            {
                'id': 'vpc-123124',
                'subnets': 'subnet-123123,subnet-2334545',
                'publicip': True
            }
        )


class TestEBP(TestCreate):
    @mock.patch('ebcli.controllers.platform.create.fileoperations.get_instance_profile')
    @mock.patch('ebcli.controllers.platform.create.create_platform_version')
    def test_create__pass_major_minor_and_patch_versions(
            self,
            create_platform_version_mock,
            get_instance_profile_mock
    ):
        get_instance_profile_mock.return_value = 'my-instance-profile'

        app = EBP(argv=['create', '1.1.1', '-M', '-m', '-p'])
        app.setup()
        app.run()

        create_platform_version_mock.assert_called_once_with(
            '1.1.1',
            True,
            True,
            True,
            None,
            {
                'id': None,
                'subnets': None,
                'publicip': False
            }
        )

    @mock.patch('ebcli.controllers.platform.create.fileoperations.get_instance_profile')
    @mock.patch('ebcli.controllers.platform.create.create_platform_version')
    def test_create__pass_instance_type(
            self,
            create_platform_version_mock,
            get_instance_profile_mock
    ):
        get_instance_profile_mock.return_value = 'my-instance-profile'

        app = EBP(argv=['create', '-i', 'c4x.large'])
        app.setup()
        app.run()

        create_platform_version_mock.assert_called_once_with(
            None,
            False,
            False,
            False,
            'c4x.large',
            {
                'id': None,
                'subnets': None,
                'publicip': False
            }
        )

    @mock.patch('ebcli.controllers.platform.create.fileoperations.get_instance_profile')
    @mock.patch('ebcli.controllers.platform.create.create_platform_version')
    def test_create__pass_instance_type_instance_profile_and_vpc_parameters(
            self,
            create_platform_version_mock,
            get_instance_profile_mock
    ):
        get_instance_profile_mock.return_value = 'my-instance-profile'

        app = EBP(
            argv=[
                'create',
                '-i', 'c4x.large',
                '-ip', 'my-instance-profile',
                '--vpc.id', 'vpc-123124',
                '--vpc.subnets', 'subnet-123123,subnet-2334545',
                '--vpc.publicip'
            ])
        app.setup()
        app.run()

        create_platform_version_mock.assert_called_once_with(
            None,
            False,
            False,
            False,
            'c4x.large',
            {
                'id': 'vpc-123124',
                'subnets': 'subnet-123123,subnet-2334545',
                'publicip': True
            }
        )
