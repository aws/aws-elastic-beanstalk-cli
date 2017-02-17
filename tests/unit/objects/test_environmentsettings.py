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
from ebcli.objects.environmentsettings import EnvironmentSettings


class TestEnvironmentSettings(unittest.TestCase):
    # This allows for larger error printouts
    maxDiff = None
    api_model = {u'ApplicationName': 'lifecycle', u'EnvironmentName': 'lifecycle-dev',
                       u'Description': 'Environment created from the EB CLI using "eb create"',
                       u'DeploymentStatus': 'deployed',
                       u'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/Platform Name/1.0.0',
                       u'OptionSettings': [{u'OptionName': 'Availability Zones', u'ResourceName': 'AWSEBAutoScalingGroup', u'Namespace': 'aws:autoscaling:asg', u'Value': 'Any'},
                                           {u'OptionName': 'Cooldown', u'ResourceName': 'AWSEBAutoScalingGroup', u'Namespace': 'aws:autoscaling:asg', u'Value': '360'},
                                           {u'OptionName': 'Custom Availability Zones', u'ResourceName': 'AWSEBAutoScalingGroup', u'Namespace': 'aws:autoscaling:asg', u'Value': ''},
                                           {u'OptionName': 'MaxSize', u'ResourceName': 'AWSEBAutoScalingGroup', u'Namespace': 'aws:autoscaling:asg', u'Value': '4'},
                                           {u'OptionName': 'MinSize', u'ResourceName': 'AWSEBAutoScalingGroup', u'Namespace': 'aws:autoscaling:asg', u'Value': '2'},
                                           {u'OptionName': 'ManagedActionsEnabled', u'Namespace': 'aws:elasticbeanstalk:managedactions', u'Value': 'false'},
                                           {u'OptionName': 'PreferredStartTime', u'Namespace': 'aws:elasticbeanstalk:managedactions'},
                                           {u'OptionName': 'InstanceRefreshEnabled', u'Namespace': 'aws:elasticbeanstalk:managedactions:platformupdate', u'Value': 'false'},
                                           {u'OptionName': 'UpdateLevel', u'Namespace': 'aws:elasticbeanstalk:managedactions:platformupdate'}],
                 u'Tier': {u'Version': ' ', u'Type': 'Standard', u'Name': 'WebServer'},
                       u'DateUpdated': datetime(2016, 12, 20, 5, 47, 5, tzinfo=tzutc()),
                       u'DateCreated': datetime(2016, 12, 20, 5, 24, 30, tzinfo=tzutc())}
    usr_model = {'ApplicationName': 'lifecycle', 'EnvironmentName': 'lifecycle-dev',
                 'DateUpdated': datetime(2016, 12, 20, 5, 47, 5, tzinfo=tzutc()),
                 'settings': {'aws:autoscaling:asg':
                                  {'MinSize': '2', 'Availability Zones': 'Any', 'Cooldown': '360',
                                   'Custom Availability Zones': '', 'MaxSize': '4'},
                              'aws:elasticbeanstalk:managedactions:platformupdate':
                                  {'UpdateLevel': None, 'InstanceRefreshEnabled': 'false'},
                              'aws:elasticbeanstalk:managedactions':
                                  {'PreferredStartTime': None, 'ManagedActionsEnabled': 'false'}},
                 'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/Platform Name/1.0.0'}

    '''
        Testing collect_changes
    '''
    @mock.patch('ebcli.objects.environmentsettings._get_option_setting_dict')
    @mock.patch('ebcli.objects.environmentsettings._get_namespace_and_resource_name')
    def test_collect_no_changes(self, mock_get_namespace, mock_get_option_dict):
        # Mock out methods
        mock_get_option_dict.return_value = None

        # Make actual call
        env_settings = EnvironmentSettings(copy.deepcopy(self.api_model))
        changes, remove = env_settings.collect_changes(copy.deepcopy(self.usr_model))

        # Make sure the correct methods were called
        self.assertEqual((changes, remove), ([], []))

    @mock.patch('ebcli.objects.environmentsettings._get_namespace_and_resource_name')
    def test_collect_added_changes(self, mock_get_namespace):
        # Mock out methods
        change_asg_max_size = copy.deepcopy(self.usr_model)
        change_asg_max_size['settings']['aws:autoscaling:asg']['MaxSize'] = 3
        change_asg_max_size['settings']['aws:autoscaling:updatepolicy:rollingupdate'] = {'MinInstancesInService': 2}
        mock_get_namespace.return_value = 'updatepolicy', 'rollingupdate'

        # Make actual call
        env_settings = EnvironmentSettings(copy.deepcopy(self.api_model))
        changes, remove = env_settings.collect_changes(change_asg_max_size)

        # Make sure the correct methods were called
        self.assertEqual((changes, remove), ([{u'OptionName': 'MaxSize', u'Namespace': 'aws:autoscaling:asg', u'Value': 3},
                                              {'OptionName': 'MinInstancesInService', 'Namespace': 'updatepolicy', 'Value': 2, 'ResourceName': 'rollingupdate'}], []))

    @mock.patch('ebcli.objects.environmentsettings._get_namespace_and_resource_name')
    def test_collect_removed_changes(self, mock_get_namespace):
        # Mock out methods
        change_asg_max_size = copy.deepcopy(self.usr_model)
        del change_asg_max_size['settings']['aws:autoscaling:asg']
        mock_get_namespace.return_value = None, None

        # Make actual call
        env_settings = EnvironmentSettings(copy.deepcopy(self.api_model))
        changes, remove = env_settings.collect_changes(change_asg_max_size)

        # Make sure the correct methods were called
        self.assertEqual((changes, remove), ([], [{'OptionName': 'Availability Zones', 'Namespace': 'aws:autoscaling:asg'},
                                                  {'OptionName': 'Cooldown', 'Namespace': 'aws:autoscaling:asg'},
                                                  {'OptionName': 'Custom Availability Zones', 'Namespace': 'aws:autoscaling:asg'},
                                                  {'OptionName': 'MaxSize', 'Namespace': 'aws:autoscaling:asg'},
                                                  {'OptionName': 'MinSize', 'Namespace': 'aws:autoscaling:asg'}]))
        self.assertEqual(len(remove), len(self.usr_model['settings']['aws:autoscaling:asg']))

    '''
        Testing convert_api_to_usr_model
    '''
    def test_convert_api_to_usr_model(self):
        # Make actual call
        env_settings = EnvironmentSettings(copy.deepcopy(self.api_model))
        actual_usr_model = env_settings.convert_api_to_usr_model()

        # Assert correct methods weere called
        self.assertEqual(self.usr_model, actual_usr_model)
