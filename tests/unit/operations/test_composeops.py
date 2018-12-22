# -*- coding: utf-8 -*-

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

import mock
from mock import Mock
import unittest

from ebcli.operations import composeops


class TestComposeOps(unittest.TestCase):
    @mock.patch('ebcli.operations.composeops.commonops.wait_for_processed_app_versions')
    @mock.patch('ebcli.operations.composeops.compose_apps')
    def test_compose_no_events__app_versions_processing_was_successful(
            self,
            compose_apps_mock,
            wait_for_processed_app_versions_mock
    ):
        wait_for_processed_app_versions_mock.return_value = True
        compose_apps_mock.return_value = 'request-id'

        self.assertEqual(
            'request-id',
            composeops.compose_no_events(
                'my-application',
                ['version-label-1', 'version-label-2'],
                'dev'
            )
        )

        wait_for_processed_app_versions_mock.assert_called_once_with(
            'my-application',
            ['version-label-1', 'version-label-2']
        )
        compose_apps_mock.assert_called_once_with(
            'my-application',
            ['version-label-1', 'version-label-2'],
            'dev'
        )

    @mock.patch('ebcli.operations.composeops.commonops.wait_for_processed_app_versions')
    @mock.patch('ebcli.operations.composeops.compose_apps')
    def test_compose_no_events__app_versions_processing_was_unsuccessful(
            self,
            compose_apps_mock,
            wait_for_processed_app_versions_mock
    ):
        wait_for_processed_app_versions_mock.return_value = False
        compose_apps_mock.return_value = 'request-id'

        self.assertIsNone(
            composeops.compose_no_events(
                'my-application',
                ['version-label-1', 'version-label-2'],
                'dev'
            )
        )

        wait_for_processed_app_versions_mock.assert_called_once_with(
            'my-application',
            ['version-label-1', 'version-label-2']
        )
        compose_apps_mock.assert_not_called()

    @mock.patch('ebcli.operations.composeops.elasticbeanstalk.compose_environments')
    def test_compose_apps(
            self,
            compose_environments_mock
    ):
        compose_environments_mock.return_value = 'request-id'

        self.assertEqual(
            'request-id',
            composeops.compose_apps(
                'my-application',
                ['version-label-1', 'version-label-2'],
                group_name='dev'
            )
        )

        compose_environments_mock.assert_called_once_with(
            'my-application',
            ['version-label-1', 'version-label-2'],
            'dev'
        )

    @mock.patch('ebcli.operations.composeops.commonops.wait_for_processed_app_versions')
    @mock.patch('ebcli.operations.composeops.compose_apps')
    def test_compose__wait_for_processed_app_versions_was_unsuccessful(
            self,
            compose_apps_mock,
            wait_for_processed_app_versions_mock
    ):
        wait_for_processed_app_versions_mock.return_value = False

        self.assertIsNone(
            composeops.compose(
                'my-application',
                ['version-label-1', 'version-label-2'],
                ['environment-1', 'environment-2'],
                group_name='dev',
                timeout=6
            )
        )

        wait_for_processed_app_versions_mock.assert_called_once_with(
            'my-application',
            ['version-label-1', 'version-label-2'],
            timeout=6
        )
        compose_apps_mock.assert_not_called()

    @mock.patch('ebcli.operations.composeops.commonops.wait_for_processed_app_versions')
    @mock.patch('ebcli.operations.composeops.commonops.wait_for_compose_events')
    @mock.patch('ebcli.operations.composeops.compose_apps')
    def test_compose(
            self,
            compose_apps_mock,
            wait_for_compose_events_mock,
            wait_for_processed_app_versions_mock
    ):
        wait_for_processed_app_versions_mock.return_value = True
        compose_apps_mock.return_value = 'request-id'

        self.assertIsNone(
            composeops.compose(
                'my-application',
                ['version-label-1', 'version-label-2'],
                ['environment-1', 'environment-2'],
                group_name='dev',
                timeout=10
            )
        )

        wait_for_processed_app_versions_mock.assert_called_once_with(
            'my-application',
            ['version-label-1', 'version-label-2'],
            timeout=10
        )
        compose_apps_mock.assert_called_once_with(
            'my-application',
            [
                'version-label-1',
                'version-label-2'
            ],
            'dev'
        )
        wait_for_compose_events_mock.assert_called_once_with(
            'request-id',
            'my-application',
            [
                'environment-1',
                'environment-2'
            ],
            10
        )

    @mock.patch('ebcli.operations.composeops.commonops.wait_for_processed_app_versions')
    @mock.patch('ebcli.operations.composeops.commonops.wait_for_compose_events')
    @mock.patch('ebcli.operations.composeops.compose_apps')
    def test_compose__nohang(
            self,
            compose_apps_mock,
            wait_for_compose_events_mock,
            wait_for_processed_app_versions_mock
    ):
        wait_for_processed_app_versions_mock.return_value = True
        compose_apps_mock.return_value = 'request-id'

        self.assertIsNone(
            composeops.compose(
                'my-application',
                ['version-label-1', 'version-label-2'],
                ['environment-1', 'environment-2'],
                group_name='dev',
                nohang=True
            )
        )

        wait_for_processed_app_versions_mock.assert_called_once_with(
            'my-application',
            ['version-label-1', 'version-label-2'],
            timeout=10
        )
        compose_apps_mock.assert_called_once_with(
            'my-application',
            [
                'version-label-1',
                'version-label-2'
            ],
            'dev'
        )
        wait_for_compose_events_mock.assert_not_called()
