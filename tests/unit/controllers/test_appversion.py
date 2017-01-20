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

import unittest

import mock

from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
from ebcli.objects.solutionstack import SolutionStack
from tests.unit.controllers.basecontrollertest import BaseControllerTest


@unittest.skip
class TestAppVersions(BaseControllerTest):
    app_name = 'awesomeApp'
    solution = SolutionStack('64bit Amazon Linux 2014.03 '
                             'v1.0.6 running PHP 5.5')

    def setUp(self):
        self.module_name = 'appversion'
        super(TestAppVersions, self).setUp()
        fileoperations.create_config_file(self.app_name, 'us-west-2',
                                          self.solution.string)

        self.patcher_versions_ops = mock.patch('ebcli.controllers.appversion.appversionops')
        self.patcher_gitops = mock.patch('ebcli.operations.gitops')
        self.mock_versions_ops = self.patcher_versions_ops.start()
        self.mock_gitops = self.patcher_gitops.start()

    def tearDown(self):
        self.patcher_versions_ops.stop()
        self.patcher_gitops.stop()
        super(TestAppVersions, self).tearDown()

    def test_delete_with_version_label(self):
        version_label = 'V1'

        EB.Meta.exit_on_close = False
        self.app = EB(argv=['appversion', '--delete', version_label])
        self.app.setup()
        self.app.run()
        self.app.close()

        self.mock_versions_ops.delete_app_version_label.assert_called_with(self.app_name, version_label)

    @mock.patch('ebcli.controllers.appversion.elasticbeanstalk')
    def test_enter_interactive_mode(self, mock_elasticbeanstalk):
        app_versions = [
            {u'ApplicationName': self.app_name, u'VersionLabel': 'v13'},
            {u'ApplicationName': self.app_name, u'VersionLabel': 'v8'}
        ]
        get_app_versions_response = {u'ApplicationVersions': app_versions}

        mock_elasticbeanstalk.get_application_versions.return_value = get_app_versions_response

        EB.Meta.exit_on_close = False
        self.app = EB(argv=['appversion'])
        self.app.setup()
        self.app.run()
        self.app.close()

        self.mock_versions_ops.display_versions.assert_called_with(self.app_name, None, app_versions)
