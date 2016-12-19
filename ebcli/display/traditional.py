# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.s
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

from . import term
from ..core import io
import locale

locale.setlocale(locale.LC_ALL, 'C')
from datetime import datetime
from cement.utils.misc import minimal_logger
from botocore.compat import six
from dateutil import tz
from ebcli.display.data_poller import DataPoller
from ebcli.display.screen import Screen
from ebcli.lib import elasticbeanstalk, elb, ec2

Queue = six.moves.queue.Queue
LOG = minimal_logger(__name__)


class TraditionalHealthDataPoller(DataPoller):
    """ Assumes we are using a LoadBalanced Environment  """

    def _get_health_data(self):
        timestamp = datetime.now(tz.tzutc())
        env = elasticbeanstalk.get_environment(self.app_name, self.env_name)
        env_dict = elasticbeanstalk.get_environment_resources(self.env_name)
        env_dict = env_dict['EnvironmentResources']
        load_balancers = env_dict.get('LoadBalancers', None)
        if load_balancers and len(load_balancers) > 0:
            load_balancer_name = env_dict.get('LoadBalancers')[0].get('Name')
            instance_states = elb.get_health_of_instances(load_balancer_name)
        else:
            instance_states = []
        instance_ids = [i['Id'] for i in
                        env_dict.get('Instances', [])]

        total_instances = len(instance_ids)
        total_in_service = len([i for i in instance_states
                                if i['State'] == 'InService'])
        env_data = {'EnvironmentName': env.name,
                    'Color': env.health,
                    'Status': env.status,
                    'Total': total_instances,
                    'InService': total_in_service,
                    'Other': total_instances - total_in_service}

        data = {'environment': env_data, 'instances': []}

        # Get Instance Health
        for i in instance_states:
            instance = {'id': i['InstanceId'], 'state': i['State'],
                        'description': i['Description']}
            ec2_health = ec2.describe_instance(instance['id'])
            instance['health'] = ec2_health['State']['Name']
            data['instances'].append(instance)

        # Get Health for instances not in Load Balancer yet
        for i in instance_ids:
            instance = {'id': i}
            if i not in [x['InstanceId'] for x in instance_states]:
                instance['description'] = 'N/A (Not registered ' \
                                          'with Load Balancer)'
                instance['state'] = 'n/a'
                ec2_health = ec2.describe_instance(i)
                instance['health'] = ec2_health['State']['Name']
                data['instances'].append(instance)

        data['environment']['RefreshedAt'] = timestamp
        return data


class TraditionalHealthScreen(Screen):
    def __init__(self):
        super(TraditionalHealthScreen, self).__init__()
        self.empty_row = 3

    def draw_banner_info_lines(self, lines, data):
        if lines > 2:
            # Get instance health count
            term.echo_line('instances:',
                           io.bold(data.get('Total', 0)), 'Total,',
                           io.bold(data.get('InService', 0)), 'InService,',
                           io.bold(data.get('Other', 0)), 'Other',
                           )
            lines -= 1
        if lines > 2:
            status = data.get('Status', 'Unknown')
            term.echo_line(' Status:', io.bold(status),
                           'Health', io.bold(data.get('Color', 'Grey')))
            lines -= 1
        return lines
