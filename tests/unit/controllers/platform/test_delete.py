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


class TestDelete(unittest.TestCase):
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


class TestEBPlatform(TestDelete):
    @mock.patch('ebcli.controllers.platform.delete.platform_version_ops.delete_platform_version')
    def test_delete__single_platform_version(
            self,
            delete_platform_version_mock
    ):
        app = EB(argv=['platform', 'delete', '1.1.1', '--force'])
        app.setup()
        app.run()

        delete_platform_version_mock.assert_called_once_with(
            '1.1.1',
            True
        )

    @mock.patch('ebcli.controllers.platform.delete.platform_version_ops.delete_platform_version')
    def test_delete__version_not_specified(
            self,
            delete_platform_version_mock
    ):
        app = EB(argv=['platform', 'delete', '--force'])
        app.setup()
        app.run()

        delete_platform_version_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.delete.platform_version_ops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.delete.platform_version_ops.delete_platform_version')
    @mock.patch('ebcli.controllers.platform.delete.io.validate_action')
    def test_delete__all_failed_versions(
            self,
            validate_action_mock,
            delete_platform_version_mock,
            list_custom_platform_versions_mock
    ):
        list_custom_platform_versions_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.1',
            'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.0'
        ]
        validate_action_mock.side_effect = None

        app = EB(argv=['platform', 'delete', '--cleanup', '--all-platforms'])
        app.setup()
        app.run()

        self.assertEqual(2, delete_platform_version_mock.call_count)
        self.assertEqual(1, validate_action_mock.call_count)
        delete_platform_version_mock.assert_has_calls(
            [
                mock.call(
                    'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.0',
                    force=True
                ),
                mock.call(
                    'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.1',
                    force=True
                )
            ]
        )

    @mock.patch('ebcli.controllers.platform.delete.platform_version_ops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.delete.platform_version_ops.delete_platform_version')
    @mock.patch('ebcli.controllers.platform.delete.io.validate_action')
    def test_delete__all_failed_versions__force(
            self,
            validate_action_mock,
            delete_platform_version_mock,
            list_custom_platform_versions_mock
    ):
        list_custom_platform_versions_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.1',
            'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.0'
        ]
        validate_action_mock.side_effect = None

        app = EB(argv=['platform', 'delete', '--cleanup', '--all-platforms', '--force'])
        app.setup()
        app.run()

        self.assertEqual(2, delete_platform_version_mock.call_count)
        validate_action_mock.assert_not_called()
        delete_platform_version_mock.assert_has_calls(
            [
                mock.call(
                    'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.0',
                    force=True
                ),
                mock.call(
                    'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.1',
                    force=True
                )
            ]
        )


class TestEBP(TestDelete):
    @mock.patch('ebcli.controllers.platform.delete.platform_version_ops.delete_platform_version')
    def test_delete__single_platform_version(
            self,
            delete_platform_version_mock
    ):
        app = EBP(argv=['delete', '1.1.1', '--force'])
        app.setup()
        app.run()

        delete_platform_version_mock.assert_called_once_with(
            '1.1.1',
            True
        )

    @mock.patch('ebcli.controllers.platform.delete.platform_version_ops.delete_platform_version')
    def test_delete__version_not_specified(
            self,
            delete_platform_version_mock
    ):
        app = EBP(argv=['delete', '--force'])
        app.setup()
        app.run()

        delete_platform_version_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.delete.platform_version_ops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.delete.platform_version_ops.delete_platform_version')
    @mock.patch('ebcli.controllers.platform.delete.io.validate_action')
    def test_delete__all_failed_versions(
            self,
            validate_action_mock,
            delete_platform_version_mock,
            list_custom_platform_versions_mock
    ):
        list_custom_platform_versions_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.1',
            'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.0'
        ]
        validate_action_mock.side_effect = None

        app = EBP(argv=['delete', '--cleanup', '--all-platforms'])
        app.setup()
        app.run()

        self.assertEqual(2, delete_platform_version_mock.call_count)
        self.assertEqual(1, validate_action_mock.call_count)

    @mock.patch('ebcli.controllers.platform.delete.platform_version_ops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.delete.platform_version_ops.delete_platform_version')
    @mock.patch('ebcli.controllers.platform.delete.io.validate_action')
    def test_delete__all_failed_versions__force(
            self,
            validate_action_mock,
            delete_platform_version_mock,
            list_custom_platform_versions_mock
    ):
        list_custom_platform_versions_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.1',
            'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.0'
        ]
        validate_action_mock.side_effect = None

        app = EBP(argv=['delete', '--cleanup', '--all-platforms', '--force'])
        app.setup()
        app.run()

        self.assertEqual(2, delete_platform_version_mock.call_count)
        validate_action_mock.assert_not_called()
        delete_platform_version_mock.assert_has_calls(
            [
                mock.call(
                    'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.0',
                    force=True
                ),
                mock.call(
                    'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.1',
                    force=True
                )
            ]
        )

    @mock.patch('ebcli.controllers.platform.delete.platform_version_ops.list_custom_platform_versions')
    @mock.patch('ebcli.controllers.platform.delete.platform_version_ops.delete_platform_version')
    @mock.patch('ebcli.controllers.platform.delete.io.validate_action')
    def test_delete__all_failed_versions__force(
            self,
            validate_action_mock,
            delete_platform_version_mock,
            list_custom_platform_versions_mock
    ):
        list_custom_platform_versions_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.1',
            'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.0'
        ]
        validate_action_mock.side_effect = None

        app = EB(argv=['platform', 'delete', '--cleanup', '--all-platforms', '--force'])
        app.setup()
        app.run()

        self.assertEqual(2, delete_platform_version_mock.call_count)
        validate_action_mock.assert_not_called()
        delete_platform_version_mock.assert_has_calls(
            [
                mock.call(
                    'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.0',
                    force=True
                ),
                mock.call(
                    'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/ibnlempnsr-custom-platform/1.0.1',
                    force=True
                )
            ]
        )