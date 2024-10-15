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
import unittest

from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
from ebcli.objects.exceptions import InvalidOptionsError


class TestAppVersions(unittest.TestCase):
    app_name = 'awesomeApp'
    solution = '64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5'

    def setUp(self):
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        os.chdir('testDir')

        fileoperations.create_config_file(
            self.app_name,
            'us-west-2',
            self.solution
        )

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

    @mock.patch('ebcli.controllers.appversion.appversionops')
    def test_delete_particular_version_label(
            self,
            appversionops_mock
    ):
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['appversion', '--delete', 'version-label-1'])
        self.app.setup()
        self.app.run()
        self.app.close()

        appversionops_mock.delete_app_version_label.assert_called_with(self.app_name, 'version-label-1')

    @mock.patch('ebcli.controllers.appversion.appversionops')
    @mock.patch('ebcli.controllers.appversion.elasticbeanstalk.get_application_versions')
    def test_enter_interactive_mode(
            self,
            get_application_versions_mock,
            appversionops_mock
    ):
        app_versions = [
            {u'ApplicationName': self.app_name, u'VersionLabel': 'v13'},
            {u'ApplicationName': self.app_name, u'VersionLabel': 'v8'}
        ]
        get_app_versions_response = {u'ApplicationVersions': app_versions}

        get_application_versions_mock.return_value = get_app_versions_response

        EB.Meta.exit_on_close = False
        self.app = EB(argv=['appversion'])
        self.app.setup()
        self.app.run()
        self.app.close()

        appversionops_mock.display_versions.assert_called_with(self.app_name, None, app_versions)

    @mock.patch('ebcli.controllers.appversion.AppVersionController.get_app_name')
    @mock.patch('ebcli.controllers.appversion.AppVersionController.get_env_name')
    def test_create_and_delete_specified_together(
            self,
            get_env_name_mock,
            get_app_name_mock,
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['appversion', '--create', '--delete', 'version-to-delete'])
        app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            app.run()

        self.assertEqual(
            'You can\'t use the "--create" and "--delete" options together.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.controllers.appversion.AppVersionController.get_env_name')
    @mock.patch('ebcli.controllers.appversion.appversionops.create_app_version_without_deployment')
    def test_create_with_application_name(
            self,
            appversion_create_mock,
            get_env_name_mock,
    ):
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['appversion', '--create', '--application', 'user-defined-name'])
        app.setup()
        app.run()

        appversion_create_mock.assert_called_with(
            'user-defined-name',
            None,
            False,
            False,
            None,
            None,
            5
        )

    @mock.patch('ebcli.core.fileoperations.env_yaml_exists')
    @mock.patch('ebcli.controllers.appversion.AppVersionController.get_app_name')
    @mock.patch('ebcli.controllers.appversion.AppVersionController.get_env_name')
    @mock.patch('ebcli.controllers.appversion.appversionops.create_app_version_without_deployment')
    def test_create_with_label_and_description(
            self,
            appversion_create_mock,
            get_env_name_mock,
            get_app_name_mock,
            file_exists_mock
    ):
        file_exists_mock.return_value = False
        get_env_name_mock.return_value = 'environment-1'
        get_app_name_mock.return_value = 'my-application'

        app = EB(argv=['appversion', '--create', '--application', 'user-defined-name', '--process'])
        app.setup()
        app.run()

        appversion_create_mock.assert_called_with(
            'user-defined-name',
            None,
            False,
            True,
            None,
            None,
            5
        )

    @mock.patch('ebcli.core.fileoperations.env_yaml_exists')
    @mock.patch('ebcli.controllers.appversion.AppVersionController.get_app_name')
    @mock.patch('ebcli.controllers.appversion.AppVersionController.get_env_name')
    @mock.patch('ebcli.controllers.appversion.appversionops.create_app_version_without_deployment')
    def test_create_with_env_yaml_exists(
            self,
            appversion_create_mock,
            get_env_name_mock,
            get_app_name_mock,
            file_exists_mock
    ):

        get_env_name_mock.return_value = 'environment-1'
        get_app_name_mock.return_value = 'my-application'
        file_exists_mock.return_value = True

        app = EB(argv=['appversion', '--create'])
        app.setup()
        app.run()

        appversion_create_mock.assert_called_with(
            'my-application',
            None,
            False,
            True,
            None,
            None,
            5
        )

    @mock.patch('ebcli.core.fileoperations.env_yaml_exists')
    @mock.patch('ebcli.controllers.appversion.AppVersionController.get_app_name')
    @mock.patch('ebcli.controllers.appversion.AppVersionController.get_env_name')
    @mock.patch('ebcli.controllers.appversion.appversionops.create_app_version_without_deployment')
    def test_create_with_staged_files(
            self,
            appversion_create_mock,
            get_env_name_mock,
            get_app_name_mock,
            file_exists_mock
    ):
        get_env_name_mock.return_value = 'environment-1'
        get_app_name_mock.return_value = 'my-application'
        file_exists_mock.return_value = False

        app = EB(argv=['appversion', '--create', '--staged'])
        app.setup()
        app.run()

        appversion_create_mock.assert_called_with(
            'my-application',
            None,
            True,
            False,
            None,
            None,
            5
        )

    @mock.patch('ebcli.core.fileoperations.env_yaml_exists')
    @mock.patch('ebcli.controllers.appversion.AppVersionController.get_app_name')
    @mock.patch('ebcli.controllers.appversion.AppVersionController.get_env_name')
    @mock.patch('ebcli.controllers.appversion.appversionops.create_app_version_without_deployment')
    def test_create_with_codecommit_source(
            self,
            appversion_create_mock,
            get_env_name_mock,
            get_app_name_mock,
            file_exists_mock
    ):
        get_env_name_mock.return_value = 'environment-1'
        get_app_name_mock.return_value = 'my-application'
        file_exists_mock.return_value = False

        app = EB(argv=['appversion', '--create', '--source', 'codecommit/my-repository/my-branch'])
        app.setup()
        app.run()

        appversion_create_mock.assert_called_with(
            'my-application',
            None,
            False,
            False,
            None,
            'codecommit/my-repository/my-branch',
            5
        )

    @mock.patch('ebcli.core.fileoperations.env_yaml_exists')
    @mock.patch('ebcli.controllers.appversion.AppVersionController.get_app_name')
    @mock.patch('ebcli.controllers.appversion.AppVersionController.get_env_name')
    @mock.patch('ebcli.controllers.appversion.appversionops.create_app_version_without_deployment')
    def test_create_with_codecommit_source_that_has_forward_slash(
            self,
            appversion_create_mock,
            get_env_name_mock,
            get_app_name_mock,
            file_exists_mock
    ):
        get_env_name_mock.return_value = 'environment-1'
        get_app_name_mock.return_value = 'my-application'
        file_exists_mock.return_value = False

        app = EB(argv=['appversion', '--create', '--source', 'codecommit/my-repository/my-branch/feature'])
        app.setup()
        app.run()

        appversion_create_mock.assert_called_with(
            'my-application',
            None,
            False,
            False,
            None,
            'codecommit/my-repository/my-branch/feature',
            5
        )
