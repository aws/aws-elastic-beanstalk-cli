# -*- coding: utf-8 -*-

# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import unittest
from pytest_socket import disable_socket, enable_socket
import mock

from ebcli.operations import appversionops
from ebcli.objects.exceptions import ValidationError, NotFoundError
from ebcli.objects.environment import Environment

class TestAppVersionsOperations(unittest.TestCase):
    app_name = 'ebcli-app'
    version_to_delete = 'delete-me'
    version_deployed = 'deployed'
    version_nonexist = 'nonexisting'

    def setUp(self):
        disable_socket()
        self.patcher_elasticbeanstalk = mock.patch('ebcli.operations.appversionops.elasticbeanstalk')
        self.patcher_io = mock.patch('ebcli.operations.appversionops.io')
        self.mock_elasticbeanstalk = self.patcher_elasticbeanstalk.start()
        self.mock_io = self.patcher_io.start()

        # define mock get app_versions behaviour
        self.mock_elasticbeanstalk.get_application_versions.return_value = {u'ApplicationVersions': [
            {u'ApplicationName': self.app_name, u'VersionLabel': self.version_to_delete},
            {u'ApplicationName': self.app_name, u'VersionLabel': self.version_deployed}
        ]}
        # define mock get_app_environments behaviour
        self.mock_elasticbeanstalk.get_app_environments.return_value = \
            [Environment(version_label=self.version_deployed, app_name=self.app_name, name='wow')]

    def tearDown(self):
        enable_socket()
        self.patcher_elasticbeanstalk.stop()
        self.patcher_io.stop()

    def test_delete_none_app_version_label(self):
        # if version label is not defined, throw exception
        self.assertRaises(NotFoundError, appversionops.delete_app_version_label, self.app_name, None)

    def test_delete_nonexist_app_version_label(self):
        # if version label does not exist at all, throw exception
        self.assertRaises(ValidationError, appversionops.delete_app_version_label, self.app_name, self.version_nonexist)

    def test_delete_deployed_app_version_label(self):
        # if version label is deployed, throw exception
        self.assertRaises(ValidationError, appversionops.delete_app_version_label, self.app_name, self.version_deployed)

    def test_delete_correct_app_version_label(self):
        appversionops.delete_app_version_label(self.app_name, self.version_to_delete)
        self.mock_elasticbeanstalk.delete_application_version.assert_called_with(self.app_name, self.version_to_delete)

    @mock.patch('ebcli.operations.appversionops.VersionDataPoller')
    @mock.patch('ebcli.operations.appversionops.VersionScreen')
    @mock.patch('ebcli.operations.appversionops._create_version_table')
    @mock.patch('ebcli.operations.appversionops.term')
    def test_display_versions(
            self,
            term_mock,
            _create_version_table_mock,
            VersionScreen_mock,
            VersionDataPoller_mock
    ):
        poller_mock = mock.MagicMock()
        VersionDataPoller_mock.return_value = poller_mock
        screen_mock = mock.MagicMock()
        VersionScreen_mock.return_value = screen_mock
        VersionScreen_mock.APP_VERSIONS_TABLE_NAME = 'appversion'
        version_data_mock = mock.MagicMock()
        poller_mock.get_version_data.return_value = version_data_mock
        _create_version_table_mock.side_effect = None

        appversionops.display_versions(
            'my-application',
            'environment-1',
            ['version-label-1', 'version-label-2']
        )

        screen_mock.start_version_screen.assert_called_once_with(
            version_data_mock,
            'appversion'
        )
        term_mock.return_cursor_to_normal.assert_called_once()

    @mock.patch('ebcli.operations.appversionops.Table')
    @mock.patch('ebcli.operations.appversionops.VersionScreen')
    @mock.patch('ebcli.operations.appversionops.ViewlessHelpTable')
    @mock.patch('ebcli.operations.appversionops.Column')
    def test_create_version_table(
            self,
            Column_mock,
            ViewlessHelpTable_mock,
            VersionScreen_mock,
            Table_mock
    ):
        screen_mock = mock.MagicMock()
        VersionScreen_mock.APP_VERSIONS_TABLE_NAME = 'appversion'
        table_mock = mock.MagicMock()
        Table_mock.return_value = table_mock
        help_table_mock = mock.MagicMock()
        ViewlessHelpTable_mock.return_value = help_table_mock

        appversionops._create_version_table(screen_mock)

        appversion_table_columns = [
            mock.call('#', None, 'DeployNum', 'left'),
            mock.call('Version Label', None, 'VersionLabel', 'left'),
            mock.call('Date Created', None, 'DateCreated', 'left'),
            mock.call('Age', None, 'SinceCreated', 'left'),
            mock.call('Description', None, 'Description', 'left')
        ]
        Column_mock.assert_has_calls(appversion_table_columns)
        screen_mock.add_table.assert_called_once_with(table_mock)
        screen_mock.add_help_table.assert_called_once_with(help_table_mock)
