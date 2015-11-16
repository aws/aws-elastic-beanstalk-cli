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

import locale
locale.setlocale(locale.LC_ALL, 'C')

import time
import threading
from collections import defaultdict
from datetime import timedelta
from datetime import datetime
from dateutil import tz
import traceback
from copy import copy

from cement.utils.misc import minimal_logger
from botocore.compat import six

from ..lib import elasticbeanstalk, utils, elb, ec2
from ..lib.aws import InvalidParameterValueError
from ..resources.strings import responses
Queue = six.moves.queue.Queue

LOG = minimal_logger(__name__)


class DataPoller(object):

    def __init__(self, app_name, env_name):
        self.app_name = app_name
        self.env_name = env_name
        self.data_queue = Queue()
        self.data = None
        self.t = None
        self.running = False
        self.no_instances_time = None
        self.instance_info = defaultdict(dict)

    def get_fresh_data(self):
        new_data = self.data
        while not self.data_queue.empty() or new_data is None:
            # Block on the first call.
            block = new_data is None
            new_data = self.data_queue.get(block=block)

        self.data = new_data
        return new_data

    def start_background_polling(self):
        self.running = True
        self.t = threading.Thread(
            target=self._poll_for_health_data
        )
        self.t.daemon = True
        self.t.start()

    def _poll_for_health_data(self):
        LOG.debug('Starting data poller child thread')
        try:
            LOG.debug('Polling for data')
            while True:
                # Grab data
                try:
                    data = self._get_health_data()

                    # Put it in queue
                    self.data_queue.put(data)
                except Exception as e:
                    if e.message == responses['health.nodescribehealth']:
                        # Environment probably switching between health monitoring types
                        LOG.debug('Swallowing \'DescribeEnvironmentHealth is not supported\' exception')
                        LOG.debug('Nothing to do as environment should be transitioning')
                    else:
                        # Not a recoverable error, raise it
                        raise e

                # Now sleep while we wait for more data
                refresh_time = data['environment'].get('RefreshedAt', None)
                time.sleep(self._get_sleep_time(refresh_time))

        except (SystemError, SystemExit, KeyboardInterrupt) as e:
            LOG.debug('Exiting due to: {}'.format(e))
        except InvalidParameterValueError as e:
            # Environment no longer exists, exit
            LOG.debug(e)
        except Exception as e:
            traceback.print_exc()
        finally:
            self.data_queue.put({})

    def _get_sleep_time(self, refresh_time):
        if refresh_time is None:
            LOG.debug('No refresh time. (11 seconds until next refresh)')
            return 2
        delta = utils.get_delta_from_now_and_datetime(refresh_time)

        countdown = 11 - delta.seconds
        LOG.debug('health time={}. '
                  'current={}. ({} seconds until next refresh)'
                  .format(utils.get_local_time_as_string(refresh_time),
                          utils.get_local_time_as_string(
                              datetime.now()), countdown))
        return max(0.5, min(countdown, 11))  # x in range [0.5, 11]

    def _account_for_clock_drift(self, environment_health):
        time_str = environment_health['ResponseMetadata']['date']
        time = datetime.strptime(time_str, '%a, %d %b %Y %H:%M:%S %Z')
        delta = utils.get_delta_from_now_and_datetime(time)
        LOG.debug(u'Clock offset={0}'.format(delta))
        LOG.debug(delta)

        try:
            environment_health['RefreshedAt'] += delta
        except KeyError:
            environment_health['RefreshedAt'] = None

    def _get_health_data(self):
        environment_health = elasticbeanstalk.\
            get_environment_health(self.env_name)
        instance_health = elasticbeanstalk.get_instance_health(self.env_name)
        LOG.debug('EnvironmentHealth-data:{}'.format(environment_health))
        LOG.debug('InstanceHealth-data:{}'.format(instance_health))
        self._account_for_clock_drift(environment_health)

        token = instance_health.get('NextToken', None)
        # Collapse data into flatter tables/dicts
        environment_health = collapse_environment_health_data(
            environment_health)
        instance_health = collapse_instance_health_data(instance_health)

        while token is not None:
            paged_health = elasticbeanstalk.get_instance_health(
                self.env_name, next_token=token)
            token = paged_health.get('NextToken', None)
            instance_health += collapse_instance_health_data(paged_health)

        # Timeout if 0 instances for more than 15 minutes
        if environment_health['Total'] == 0:
            if self.no_instances_time is None:
                self.no_instances_time = datetime.now()
            else:
                timediff = timedelta(seconds=15 * 60)
                if (datetime.now() - self.no_instances_time) > timediff:
                    return {}
        else:
            self.no_instances_time = None

        # Get AZ info for each instance
        self._get_instance_azs(instance_health)

        # Return all the data as a single object
        data = {'environment': environment_health,
                'instances': instance_health}
        LOG.debug('collapsed-data:{}'.format(data))
        return data

    def _get_instance_azs(self, data_dict):
        instance_ids = [i.get('InstanceId') for i in data_dict]
        ids_with_no_az_info = []
        for id in instance_ids:
            if 'az' not in self.instance_info[id]:
                ids_with_no_az_info.append(id)

        instances = ec2.describe_instances(ids_with_no_az_info)
        for i in instances:
            id = i.get('InstanceId', None)
            az = i.get('Placement', {}).get('AvailabilityZone', None)
            if az:
                self.instance_info[id]['az'] = az

        for instance_data in data_dict:
            id = instance_data.get('InstanceId')
            instance_data['az'] = self.instance_info.get(id, {}).get('az', 'no-data')


def collapse_environment_health_data(environment_health):
    result = dict()
    request_count = environment_health.get('ApplicationMetrics', {}) \
        .get('RequestCount', 0)

    latency_dict = environment_health.get('ApplicationMetrics', {})\
        .pop('Latency', {})
    result.update(_format_latency_dict(latency_dict, request_count))

    result['requests'] = request_count/10.0
    statuses = environment_health.get('ApplicationMetrics', {})\
        .pop('StatusCodes', {})
    for k, v in six.iteritems(statuses):
        convert_data_to_percentage(statuses, k, request_count)
    result.update(statuses)
    result.update(environment_health.pop('ApplicationMetrics', {}))
    total = 0
    for k, v in six.iteritems(environment_health.get('InstancesHealth', {})):
        total += v
    result['Total'] = total
    result.update(environment_health.pop('InstancesHealth', {}))
    result.update(environment_health)

    causes = result.get('Causes', [])
    cause = causes[0] if causes else ''
    result['Cause'] = cause

    return result


def collapse_instance_health_data(instances_health):
    instance_list = instances_health.get('InstanceHealthList', [])
    result = list()
    for i in instance_list:
        instance = dict()
        request_count = i.get('ApplicationMetrics', {}) \
            .get('RequestCount', 0)
        latency = i.get('ApplicationMetrics', {}).pop('Latency', {})
        instance.update(_format_latency_dict(latency, request_count))
        instance.update(i.get('ApplicationMetrics', {}).pop('StatusCodes', {}))
        instance.update(i.pop('ApplicationMetrics', {}))

        instance.update(i.get('System', {}).pop('CPUUtilization', {}))
        instance.update(i.pop('System', {}))
        instance.update(i)
        causes = instance.get('Causes', [])
        cause = causes[0] if causes else ''
        instance['Cause'] = cause

        instance['load1'] = instance['LoadAverage'][0] \
            if 'LoadAverage' in instance else '-'
        instance['load5'] = instance['LoadAverage'][1] \
            if 'LoadAverage' in instance else '-'

        try:
            delta = datetime.now(tz.tzlocal()) - utils.get_local_time(instance['LaunchedAt'])
            instance['launched'] = utils.get_local_time_as_string(instance['LaunchedAt'])

            days = delta.days
            minutes = delta.seconds // 60
            hours = minutes // 60

            if days > 0:
                instance['running'] = '{0} day{s}'\
                    .format(days, s=_get_s(days))
            elif hours > 0:
                instance['running'] = '{0} hour{s}'\
                    .format(hours, s=_get_s(hours))
            elif minutes > 0:
                instance['running'] = '{0} min{s}'\
                    .format(minutes, s=_get_s(minutes))
            else:
                instance['running'] = '{0} secs'.format(delta.seconds)
        except KeyError as e:
            instance['running'] = '-'

        # Calculate requests per second
        duration = instance.get('Duration', 10)
        instance['requests'] = request_count / (duration * 1.0)

        # Convert counts to percentages
        for key in {'Status_2xx', 'Status_3xx', 'Status_4xx', 'Status_5xx'}:
            convert_data_to_percentage(instance, key, request_count,
                                       add_sort_column=True)

        # Add status sort index
        instance['status_sort'] = _get_health_sort_order(instance['HealthStatus'])

        result.append(instance)

    return result


def _format_latency_dict(latency_dict, request_count):
    new_dict = copy(latency_dict)
    for k, v in six.iteritems(latency_dict):
        new_dict[k + '_sort'] = v
        representation = format_float(v, 3)

        if (k == 'P99' and request_count < 100) or \
                (k == 'P90' and request_count < 10):
            representation += '*'
        elif k in ['P99', 'P90']:
            representation += ' '
        new_dict[k] = representation

    return new_dict


def _get_s(number):
    return 's' if number > 1 else ''


def convert_data_to_percentage(data, index, total, add_sort_column=False):
    if total > 0:
        percent = (data.get(index, 0) / (total * 1.0)) * 100.0
        # Now convert to string
        representation = format_float(percent, 1)
        data[index] = representation

        # Convert back to float for sorting
        if add_sort_column:
            data[index + '_sort'] = float(representation)


def format_float(flt, number_of_places):
    format_string = '{0:.' + str(number_of_places) + 'f}'
    return format_string.format(flt)


def _get_health_sort_order(health):
    health_order = dict(
        (v, k) for k, v in enumerate([
            'Severe',
            'Degraded',
            'Unknown',
            'Warning',
            'NoData',
            'No Data',
            'Info',
            'Pending',
            'Ok',
        ])
    )
    return health_order[health]


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