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
