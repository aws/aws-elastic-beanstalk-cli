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

import mock
import unittest
from mock import call
from datetime import datetime
from dateutil.tz import tzutc

from ebcli.operations import lifecycleops
from ebcli.objects.exceptions import InvalidSyntaxError

class TestLifecycleOperations(unittest.TestCase):
    current_time = datetime.now()
    region = 'us-foo-1'
    app_name = 'foo_app'
    file_location = 'local/app/'
    app_response = {u'ApplicationName': app_name, u'Description': 'Application created from the EB CLI using "eb init"',
           u'Versions': ['Sample Application'],
           u'DateCreated': datetime(2016, 12, 20, 2, 48, 7, 938000, tzinfo=tzutc()),
           u'ConfigurationTemplates': [],
           u'DateUpdated': datetime(2016, 12, 20, 2, 48, 7, 938000, tzinfo=tzutc()),
           u'ResourceLifecycleConfig': {u'VersionLifecycleConfig':
                                            {u'MaxCountRule': {u'DeleteSourceFromS3': False, u'Enabled': False,
                                                               u'MaxCount': 200},
                                             u'MaxAgeRule': {u'DeleteSourceFromS3': False, u'Enabled': False,
                                                             u'MaxAgeInDays': 180}},
                                        u'ServiceRole': 'arn:aws:iam::293615521073:role/aws-elasticbeanstalk-service-role'}}

    usr_model = {u'ResourceLifecycleConfig': {u'VersionLifecycleConfig':
                                            {u'MaxCountRule': {u'DeleteSourceFromS3': False, u'Enabled': False,
                                                               u'MaxCount': 200},
                                             u'MaxAgeRule': {u'DeleteSourceFromS3': False, u'Enabled': False,
                                                             u'MaxAgeInDays': 180}},
                                        u'ServiceRole': 'arn:aws:iam::293615521073:role/aws-elasticbeanstalk-service-role'}}

    def setUp(self):
        self.patcher_io = mock.patch('ebcli.operations.lifecycleops.io')
        self.patcher_beanstalk = mock.patch('ebcli.operations.lifecycleops.elasticbeanstalk')
        self.patcher_fileops = mock.patch('ebcli.operations.lifecycleops.fileoperations')
        self.mock_io = self.patcher_io.start()
        self.mock_beanstalk = self.patcher_beanstalk.start()
        self.mock_fileops = self.patcher_fileops.start()

    def tearDown(self):
        self.patcher_io.stop()
        self.patcher_beanstalk.stop()
        self.patcher_fileops.stop()

    @mock.patch('ebcli.operations.lifecycleops.recursive_print_api_dict')
    @mock.patch('ebcli.operations.lifecycleops.aws.get_region_name')
    def test_print_lifecycle_policy(self, mock_region, mock_recursive_print):
        # Mock out methods
        self.mock_beanstalk.describe_application.return_value = self.app_response
        mock_region.return_value = self.region

        # Make actual call
        lifecycleops.print_lifecycle_policy(self.app_name)

        # Assert methods were called
        self.mock_beanstalk.describe_application.assert_called_with(self.app_name)
        mock_recursive_print.assert_called_with(self.app_response[u'ResourceLifecycleConfig'])

    def test_recursive_print(self):
        # Make actual call
        lifecycleops.recursive_print_api_dict(self.app_response[u'ResourceLifecycleConfig'])

        # Assert correct methods were called
        io_echo_calls = [call('{0}VersionLifecycleConfig:'.format(lifecycleops.SPACER * 2)),
                         call('{0}MaxCountRule:'.format(lifecycleops.SPACER * 3)),
                         call('{0}DeleteSourceFromS3: False'.format(lifecycleops.SPACER * 4)),
                         call('{0}Enabled: False'.format(lifecycleops.SPACER * 4)),
                         call('{0}MaxCount: 200'.format(lifecycleops.SPACER * 4)),
                         call('{0}MaxAgeRule:'.format(lifecycleops.SPACER * 3)),
                         call('{0}DeleteSourceFromS3: False'.format(lifecycleops.SPACER * 4)),
                         call('{0}Enabled: False'.format(lifecycleops.SPACER * 4)),
                         call('{0}MaxAgeInDays: 180'.format(lifecycleops.SPACER * 4)),
                         call('{0}ServiceRole: arn:aws:iam::293615521073:role/aws-elasticbeanstalk-service-role'.format(lifecycleops.SPACER * 2))]
        self.mock_io.echo.assert_has_calls(io_echo_calls, any_order=True)

    @mock.patch('ebcli.operations.lifecycleops.LifecycleConfiguration')
    def test_interactive_update_lifecycle_policy(self, mock_lifecycle_config):
        # Mock out methods
        self.mock_beanstalk.describe_application.return_value = self.app_response
        mock_lifecycle_config.return_value = mock_lifecycle_config
        mock_lifecycle_config.convert_api_to_usr_model.return_value = self.usr_model
        self.mock_fileops.save_app_file.return_value = self.file_location
        self.mock_fileops.get_application_from_file.return_value = self.usr_model
        mock_lifecycle_config.collect_changes.return_value = self.usr_model

        # Make actual call
        lifecycleops.interactive_update_lifcycle_policy(self.app_name)

        # Assert correct methods were called
        self.mock_beanstalk.describe_application.assert_called_with(self.app_name)
        mock_lifecycle_config.assert_called_with(self.app_response)
        self.mock_fileops.save_app_file.assert_called_with(self.usr_model)
        self.mock_fileops.open_file_for_editing.assert_called_with(self.file_location)
        self.mock_fileops.get_application_from_file.assert_called_with(self.app_name)
        mock_lifecycle_config.collect_changes.assert_called_with(self.usr_model)
        self.mock_fileops.delete_app_file.assert_called_with(self.app_name)
        self.mock_beanstalk.update_application_resource_lifecycle.assert_called_with(self.app_name, self.usr_model)

    @mock.patch('ebcli.operations.lifecycleops.LifecycleConfiguration')
    def test_interactive_update_lifecycle_policy_no_changes(self, mock_lifecycle_config):
        # Mock out methods
        self.mock_beanstalk.describe_application.return_value = self.app_response
        mock_lifecycle_config.return_value = mock_lifecycle_config
        mock_lifecycle_config.convert_api_to_usr_model.return_value = self.usr_model
        self.mock_fileops.save_app_file.return_value = self.file_location
        self.mock_fileops.get_application_from_file.return_value = self.usr_model
        mock_lifecycle_config.collect_changes.return_value = {}

        # Make actual call
        lifecycleops.interactive_update_lifcycle_policy(self.app_name)

        # Assert correct methods were called
        self.mock_beanstalk.describe_application.assert_called_with(self.app_name)
        mock_lifecycle_config.assert_called_with(self.app_response)
        self.mock_fileops.save_app_file.assert_called_with(self.usr_model)
        self.mock_fileops.open_file_for_editing.assert_called_with(self.file_location)
        self.mock_fileops.get_application_from_file.assert_called_with(self.app_name)
        mock_lifecycle_config.collect_changes.assert_called_with(self.usr_model)
        self.mock_fileops.delete_app_file.assert_called_with(self.app_name)
        self.mock_beanstalk.update_application_resource_lifecycle.assert_not_called()

    @mock.patch('ebcli.operations.lifecycleops.LifecycleConfiguration')
    def test_interactive_update_lifecycle_policy_bad_user_input(self, mock_lifecycle_config):
        # Mock out methods
        self.mock_beanstalk.describe_application.return_value = self.app_response
        mock_lifecycle_config.return_value = mock_lifecycle_config
        mock_lifecycle_config.convert_api_to_usr_model.return_value = self.usr_model
        self.mock_fileops.save_app_file.return_value = self.file_location
        self.mock_fileops.get_application_from_file.side_effect = InvalidSyntaxError("Bad syntax in config.")

        # Make actual call
        lifecycleops.interactive_update_lifcycle_policy(self.app_name)

        # Assert correct methods were called
        self.mock_beanstalk.describe_application.assert_called_with(self.app_name)
        mock_lifecycle_config.assert_called_with(self.app_response)
        self.mock_fileops.save_app_file.assert_called_with(self.usr_model)
        self.mock_fileops.open_file_for_editing.assert_called_with(self.file_location)
        self.mock_fileops.get_application_from_file.assert_called_with(self.app_name)
        mock_lifecycle_config.collect_changes.assert_not_called()
        self.mock_fileops.delete_app_file.assert_called_with(self.app_name)
        self.mock_beanstalk.update_application_resource_lifecycle.assert_not_called()
