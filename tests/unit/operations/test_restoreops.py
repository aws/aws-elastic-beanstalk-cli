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
from datetime import date, timedelta, datetime

import mock

from ebcli.lib.aws import InvalidParameterValueError
from ebcli.objects.application import Application
from ebcli.objects.environment import Environment
from ebcli.operations import restoreops

class TestRestoreEnvironment(unittest.TestCase):
    current_time = datetime.now()
    request_id = 'foo-request-id'
    env_id = 'e-1234567890'
    app = Application(name="some-app")
    env1 = {'EnvironmnetId': env_id, 'EnvironmentName': "env1", 'VersionLabel': "v1",
            'ApplicationName': "app1", 'Status' : 'Ready',
            'DateUpdated': (date.today() - timedelta(days=10))}
    env2 = {'EnvironmnetId': 'e-0987654321', 'EnvironmentName': "env2", 'VersionLabel': "v2",
            'ApplicationName': "some-app", 'Status': 'Terminated',
            'DateUpdated': (date.today())}
    env_object = Environment(id=env_id, name="env1", version_label="v1", app_name="app1",
                       date_updated=(date.today() - timedelta(days=10)), status='Terminated')

    def setUp(self):
        self.patcher_beanstalk = mock.patch('ebcli.operations.restoreops.elasticbeanstalk')
        self.mock_beanstalk = self.patcher_beanstalk.start()
        self.env_object.status = 'Terminated'

    def tearDown(self):
        self.patcher_beanstalk.stop()

    def test_validate_restore_bad_env(self):
        self.env_object.status = 'Ready'
        self.mock_beanstalk.get_environment.return_value = self.env_object
        self.assertRaises(InvalidParameterValueError, restoreops.validate_restore, self.env_id)

    @mock.patch('ebcli.operations.restoreops.get_date_cutoff')
    def test_validate_restore_good_env(self, mock_date):
        mock_date.return_value = self.current_time
        self.mock_beanstalk.get_environment.return_value = self.env_object
        restoreops.validate_restore(self.env_id)
        self.mock_beanstalk.get_environment.assert_called_with(env_id=self.env_id, include_deleted=True,
                                               deleted_back_to=self.current_time)

    @mock.patch('ebcli.operations.restoreops.commonops')
    def test_restore_with_good_env(self, mock_common_ops):
        self.mock_beanstalk.get_environment.return_value = self.env_object
        self.mock_beanstalk.rebuild_environment.return_value = self.request_id

        restoreops.restore(self.env_id)

        mock_common_ops.wait_for_success_events.assert_called_with(self.request_id, timeout_in_minutes=None,
                                                                   can_abort=True)

    def test_restore_with_bad_param_exception(self):
        self.env_object.status = 'Ready'
        self.mock_beanstalk.get_environment.return_value = self.env_object

        self.mock_beanstalk.rebuild_environment.side_effect = [
            InvalidParameterValueError('Could not rebuild environment some-name because the cname is taken')]

        self.assertRaises(InvalidParameterValueError, restoreops.restore, self.env_id)


    def test_fetch_restorable_envs(self):
        self.mock_beanstalk.get_raw_app_environments.return_value = [self.env1, self.env2]

        environments = restoreops.get_restorable_envs(self.app)

        self.assertNotIn(self.env1, environments,
                         "Non-terminated environment returned in restorable environments when it should not be")
        self.assertIn(self.env2, environments, "Terminated environment not in restorable environments when it should be")

