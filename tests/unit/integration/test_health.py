# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import datetime

from dateutil.tz import tzutc

from ebcli.core import fileoperations
from ebcli.operations import commonops

from .baseinttest import BaseIntegrationTest
from . import mockservice


class TestHealth(BaseIntegrationTest):

    def setUp(self):
        super(TestHealth, self).setUp()
        # Create all app stuff
        fileoperations.create_config_file('myEBCLItest', 'us-west-2',
                                          'my-stack-stack')
        commonops.set_environment_for_current_branch('my-env')

        mockservice.enqueue('elasticbeanstalk',
                            'DescribeInstancesHealth',
                            standard_instance_health())
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeEnvironmentHealth',
                            standard_health())
        mockservice.enqueue('elasticbeanstalk',
                            'DescribeConfigurationSettings',
                            enhanced_health_settings())

    def test_health_standard(self):
        self.run_command('health')


def enhanced_health_settings():
    d = mockservice.standard_describe_configuration_settings()
    option_settings = d['ConfigurationSettings'][0]['OptionSettings']
    option_settings.append({
        'OptionName': 'SystemType',
        'Namespace': 'aws:elasticbeanstalk:healthreporting:system',
        'Value': 'enhanced',
    })
    return d


def standard_health():
    return dict(Status='Ok', EnvironmentName='my-env',
                ResponseMetadata={'HTTPStatusCode': 200,
                                  'RequestId':
                                      'b6713e98-e9d8-11e4-a371-7b7d472eacbb'},
                Color='Green', ApplicationMetrics={u'RequestCount': 0},
                RefreshedAt=datetime.datetime(2015, 4, 23, 16, 49, 25,
                                              tzinfo=tzutc()),
                InstancesHealth={u'Info': 0, u'Ok': 1, u'Unknown': 0,
                                 u'Severe': 0, u'Warning': 0, u'Degraded': 0,
                                 u'NoData': 0, u'Pending': 0}, Causes=[])


def standard_instance_health():
    return dict(
        InstanceHealthList=[
            {u'Status': 'Ok', u'InstanceId': 'i-12345678',
             u'ApplicationMetrics': {u'RequestCount': 0},
             u'System': {u'Loadavg': [0.0, 0.03, 0.05],
                         u'CPUUtilization': {u'Softirq': 0.0, u'Iowait': 0.1,
                                             u'System': 0.1, u'Idle': 99.3,
                                             u'User': 0.5, u'Irq': 0.0,
                                             u'Nice': 0.0}}, u'Color': 'Green',
             u'LaunchedAt': datetime.datetime(2015, 4, 22, 23, 36, tzinfo=tzutc()),
             u'Causes': []}],
        ResponseMetadata={'HTTPStatusCode': 200,
                          'RequestId': 'b69cbbb4-e9d8-11e4-908c-175b2f42957b'},
        RefreshedAt=datetime.datetime(2015, 4, 23, 16, 49, 25,
                                      tzinfo=tzutc()))