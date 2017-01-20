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
import copy
from datetime import datetime
import mock
from dateutil.tz import tzutc

from ebcli.objects.exceptions import InvalidOptionsError, NotFoundError
from ebcli.objects import lifecycleconfiguration
from ebcli.objects.lifecycleconfiguration import LifecycleConfiguration


class TestLifecycleConfiguration(unittest.TestCase):
    current_time = datetime.now()
    region = 'us-foo-1'
    app_name = 'foo_app'
    file_location = 'local/app/'
    service_role = 'arn:aws:iam::293615521073:role/aws-elasticbeanstalk-service-role'
    get_role_response = {u'Arn': service_role}
    api_model = {u'ApplicationName': app_name, u'Description': 'Application created from the EB CLI using "eb init"',
                 u'Versions': ['Sample Application'],
                 u'DateCreated': datetime(2016, 12, 20, 2, 48, 7, 938000, tzinfo=tzutc()),
                 u'ConfigurationTemplates': [],
                 u'DateUpdated': datetime(2016, 12, 20, 2, 48, 7, 938000, tzinfo=tzutc()),
                 u'ResourceLifecycleConfig': {u'VersionLifecycleConfig':
                                                  {u'MaxCountRule': {u'DeleteSourceFromS3': False, u'Enabled': False,
                                                                     u'MaxCount': 200},
                                                   u'MaxAgeRule': {u'DeleteSourceFromS3': False, u'Enabled': False,
                                                                   u'MaxAgeInDays': 180}},
                                              u'ServiceRole': service_role}}

    usr_model = {'ApplicationName': app_name,
                 'DateUpdated': datetime(2016, 12, 20, 2, 48, 7, 938000, tzinfo=tzutc()),
                 'Configurations': {u'VersionLifecycleConfig':
                                        {u'MaxCountRule': {u'DeleteSourceFromS3': False, u'Enabled': False,
                                                           u'MaxCount': 200},
                                         u'MaxAgeRule': {u'DeleteSourceFromS3': False, u'Enabled': False,
                                                         u'MaxAgeInDays': 180}},
                                    u'ServiceRole': service_role}}

    def setUp(self):
        self.patcher_get_role = mock.patch('ebcli.objects.lifecycleconfiguration.get_role')
        self.mock_get_role = self.patcher_get_role.start()

    def tearDown(self):
        self.patcher_get_role.stop()

    '''
        Testing collect_changes
    '''

    def test_collect_changes_no_service_role(self):
        # Mock out methods
        no_service_role_model = copy.deepcopy(self.usr_model)
        del no_service_role_model['Configurations']['ServiceRole']
        expected_changes = no_service_role_model['Configurations']

        # Make actual service call
        lifecycle_config = LifecycleConfiguration(self.api_model)
        changes = lifecycle_config.collect_changes(no_service_role_model)
        self.assertEqual(expected_changes, changes,
                         "Expected changes to be: {0}\n But was: {1}".format(expected_changes, changes))
        # Assert correct methods were called
        self.mock_get_role.assert_not_called()

    def test_collect_changes_with_service_role(self):
        # Make actual service call
        lifecycle_config = LifecycleConfiguration(self.api_model)
        changes = lifecycle_config.collect_changes(self.usr_model)
        expected_changed = self.usr_model['Configurations']
        self.assertEqual(expected_changed, changes,
                         "Expected changes to be: {0}\n But was: {1}".format(expected_changed, changes))
        # Assert correct methods were called
        self.mock_get_role.assert_called_with(self.service_role.split('/')[-1])

    def test_collect_changes_service_role_not_found(self):
        # Mock out methods
        self.mock_get_role.side_effect = NotFoundError("Could not find role")
        # Make actual service call
        lifecycle_config = LifecycleConfiguration(self.api_model)
        self.assertRaises(InvalidOptionsError, lifecycle_config.collect_changes, self.usr_model)

        # Assert correct methods were called
        self.mock_get_role.assert_called_with(self.service_role.split('/')[-1])

    '''
        Testing convert_api_to_usr_model
    '''
    def test_convert_api_to_usr_model_no_service_role(self):
        # Mock out methods
        self.mock_get_role.return_value = self.get_role_response
        no_service_role_model = copy.deepcopy(self.api_model)
        del no_service_role_model['ResourceLifecycleConfig']['ServiceRole']

        # Make actual service call
        lifecycle_config = LifecycleConfiguration(no_service_role_model)
        actual_usr_model = lifecycle_config.convert_api_to_usr_model()

        self.assertEqual(self.usr_model, actual_usr_model,
                         "Expected changes to be: {0}\n But was: {1}".format(self.usr_model, actual_usr_model))
        # Assert correct methods were called
        self.mock_get_role.assert_called_with(lifecycleconfiguration.DEFAULT_LIFECYCLE_SERVICE_ROLE)

    def test_convert_api_to_usr_model_default_role_does_not_exist(self):
        # Mock out methods
        self.mock_get_role.side_effect = NotFoundError("Could not find role")
        no_service_role_model = copy.deepcopy(self.api_model)
        del no_service_role_model['ResourceLifecycleConfig']['ServiceRole']

        # Make actual service call
        lifecycle_config = LifecycleConfiguration(no_service_role_model)
        actual_usr_model = lifecycle_config.convert_api_to_usr_model()
        expected_usr_model = copy.deepcopy(self.usr_model)
        expected_usr_model['Configurations'][u'ServiceRole'] = lifecycleconfiguration.DEFAULT_ARN_STRING

        self.assertEqual(expected_usr_model, actual_usr_model,
                         "Expected changes to be: {0}\n But was: {1}".format(expected_usr_model, actual_usr_model))
        # Assert correct methods were called
        self.mock_get_role.assert_called_with(lifecycleconfiguration.DEFAULT_LIFECYCLE_SERVICE_ROLE)

    def test_convert_api_to_usr_model_with_service_role(self):
        # Make actual service call
        lifecycle_config = LifecycleConfiguration(self.api_model)
        actual_usr_model = lifecycle_config.convert_api_to_usr_model()
        self.assertEqual(self.usr_model, actual_usr_model,
                         "Expected changes to be: {0}\n But was: {1}".format(self.usr_model, actual_usr_model))
        # Assert correct methods were called
        self.mock_get_role.assert_not_called()
