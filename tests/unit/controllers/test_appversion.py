# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
from ebcli.objects.solutionstack import SolutionStack


class TestAppVersions(unittest.TestCase):
    app_name = 'awesomeApp'
    solution = '64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5'

    def setUp(self):
        disable_socket()
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

        enable_socket()

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
