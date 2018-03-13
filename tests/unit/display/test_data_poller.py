# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
from dateutil import tz

import unittest
import mock

from ebcli.display import data_poller


class TestDataPoller(unittest.TestCase):
	maxDiff = None
	ENVIRONMENT_HEALTH = environment_health = {
		'EnvironmentName': 'health-tests-test-1',
		'HealthStatus': 'Ok',
		'Status': 'Ready',
		'Color': 'Green',
		'Causes': ['Fake cause 1', 'Fake cause 2'],
		'ApplicationMetrics': {
			'RequestCount': 0
		},
		'InstancesHealth': {
			'NoData': 0,
			'Unknown': 0,
			'Pending': 1,
			'Ok': 1,
			'Info': 0,
			'Warning': 0,
			'Degraded': 0,
			'Severe': 0
		},
		'RefreshedAt': datetime.datetime(2018, 3, 12, 22, 19, 1, tzinfo=tz.tzutc()),
		'ResponseMetadata': {
			'RequestId': 'fc611309-224f-489c-af04-c21e4cc70100',
			'HTTPStatusCode': 200,
			'date': 'Mon, 12 Mar 2018 22:19:04 GMT',
			'RetryAttempts': 0
		}
	}

	DESCRIBE_INSTANCES_HEALTH = {
		'InstanceHealthList': [
			{
				'InstanceId': 'i-0f111c68ca2eb9ce2',
				'HealthStatus': 'Severe',
				'Color': 'Red',
				'Causes':[
					'Instance initialization failed.'
				],
				'LaunchedAt':datetime.datetime(2018, 3, 13, 19, 12, 27, tzinfo=tz.tzutc()),
				'ApplicationMetrics': {
					'Duration': 10,
					'RequestCount': 6,
					'StatusCodes': {
						'Status2xx': 6,
						'Status3xx': 0,
						'Status4xx': 0,
						'Status5xx': 0
					},
					'Latency': {
						'P999': 15.6,
						'P99': 15.6,
						'P95': 15.6,
						'P90': 15.6,
						'P85': 14.3,
						'P75': 11.7,
						'P50': 5.2,
						'P10': 0.0
					}
				},
				'System': {
					'CPUUtilization': {
						'User': 0.0,
						'System': 0.0,
						'Idle': 100.0
					}
				},
				'Deployment': {

				},
				'AvailabilityZone': 'us-east-1d',
				'InstanceType': 't2.micro'
			}
		],
		'RefreshedAt': datetime.datetime(2018, 3, 14, 0, 8, 46, tzinfo=tz.tzutc()),
		'ResponseMetadata': {
			'RequestId': '26fdf953-1700-4c4f-8009-19fba9b4d2e8',
			'HTTPStatusCode': 200,
			'date': 'Wed, 14 Mar 2018 00: 08:48 GMT',
			'RetryAttempts': 0
		}
	}

	GET_HEALTH_DATA_RESULT = {
		'environment': {
			'Cause': 'Fake cause 1',
			'Causes': ['Fake cause 1', 'Fake cause 2'],
			'Color': 'Green',
			'EnvironmentName': 'health-tests-test-1',
			'HealthStatus': 'Ok',
			'RefreshedAt': datetime.datetime(2018, 3, 12, 22, 20, 1, tzinfo=tz.tzutc()),
			'ResponseMetadata': {
				'HTTPStatusCode': 200,
				'RequestId': 'fc611309-224f-489c-af04-c21e4cc70100',
				'RetryAttempts': 0,
				'date': 'Mon, 12 Mar 2018 22:19:04 GMT'
			},
			'Status': 'Ready',
			'Total': 0,
			'requests': 0.0
		},
		'instances': [
			{
				'AvailabilityZone': '1d',
				'Cause': 'Instance initialization failed.',
				'Causes': ['Instance initialization failed.'],
				'Color': 'Red',
				'Deployment': {},
				'HealthStatus': 'Severe',
				'InstanceId': 'i-0f111c68ca2eb9ce2',
				'InstanceType': 't2.micro',
				'LaunchedAt': datetime.datetime(2018, 3, 13, 19, 12, 27, tzinfo=tz.tzutc()),
				'launched': '2018-03-14 04:12:27',
				'load1': '-',
				'load5': '-',
				'requests': 0.0,
				'running': '1 day',
				'status_sort': 0
			}
		]
	}

	def test_format_float(self):
		self.assertEqual('1.0', data_poller.format_float(flt=1, number_of_places=1))
		self.assertEqual('1.0', data_poller.format_float(flt=1.0, number_of_places=1))
		self.assertEqual('1.0', data_poller.format_float(flt=1.00, number_of_places=1))
		self.assertEqual('1.009', data_poller.format_float(flt=1.009, number_of_places=3))
		self.assertEqual('1.01', data_poller.format_float(flt=1.009, number_of_places=2))
		self.assertEqual('1.0', data_poller.format_float(flt=1.001, number_of_places=1))
		self.assertEqual('1.500', data_poller.format_float(flt=1.4999, number_of_places=3))
		self.assertEqual('1.5', data_poller.format_float(flt=1.51, number_of_places=1))
		self.assertEqual('1.6', data_poller.format_float(flt=1.55, number_of_places=1))
		self.assertEqual('2.0', data_poller.format_float(flt=1.99, number_of_places=1))

	def test_collapse_environment_health_data(self):
		self.assertEqual(
			{
				'Cause': 'Fake cause 1',
				'Causes': ['Fake cause 1', 'Fake cause 2'],
				'Color': 'Green',
				'Degraded': 0,
				'EnvironmentName': 'health-tests-test-1',
				'HealthStatus': 'Ok',
				'Info': 0,
				'NoData': 0,
				'Ok': 1,
				'Pending': 1,
				'RefreshedAt': datetime.datetime(2018, 3, 12, 22, 19, 1, tzinfo=tz.tzutc()),
				'RequestCount': 0,
				'Severe': 0,
				'Status': 'Ready',
				'Total': 2,
				'Unknown': 0,
				'Warning': 0,
				'requests': 0.0,
				'ResponseMetadata': {
					'RequestId': 'fc611309-224f-489c-af04-c21e4cc70100',
					'HTTPStatusCode': 200,
					'date': 'Mon, 12 Mar 2018 22:19:04 GMT',
					'RetryAttempts': 0
				}
			},
			data_poller.collapse_environment_health_data(TestDataPoller.ENVIRONMENT_HEALTH))

	@mock.patch('ebcli.display.data_poller.format_time_since')
	def test_collapse_instance_health_data(self, format_time_since_mock):
		self.maxDiff = None
		format_time_since_mock.return_value = '4 hours'

		self.assertEqual(
			[
				{
					'AvailabilityZone': '1d',
					'Cause': 'Instance initialization failed.',
					'Causes': ['Instance initialization failed.'],
					'Color': 'Red',
					'Deployment': {},
					'Duration': 10,
					'HealthStatus': 'Severe',
					'Idle': 100.0,
					'InstanceId': 'i-0f111c68ca2eb9ce2',
					'InstanceType': 't2.micro',
					'LaunchedAt': datetime.datetime(2018, 3, 13, 19, 12, 27, tzinfo=tz.tzutc()),
					'P10': '0.000',
					'P10_sort': 0.0,
					'P50': '5.200',
					'P50_sort': 5.2,
					'P75': '11.700',
					'P75_sort': 11.7,
					'P85': '14.300',
					'P85_sort': 14.3,
					'P90': '15.600*',
					'P90_sort': 15.6,
					'P95': '15.600',
					'P95_sort': 15.6,
					'P99': '15.600*',
					'P999': '15.600',
					'P999_sort': 15.6,
					'P99_sort': 15.6,
					'RequestCount': 6,
					'Status2xx': 6,
					'Status3xx': 0,
					'Status4xx': 0,
					'Status5xx': 0,
					'Status_2xx': '0.0',
					'Status_2xx_sort': 0.0,
					'Status_3xx': '0.0',
					'Status_3xx_sort': 0.0,
					'Status_4xx': '0.0',
					'Status_4xx_sort': 0.0,
					'Status_5xx': '0.0',
					'Status_5xx_sort': 0.0,
					'System': 0.0,
					'User': 0.0,
					'launched': '2018-03-14 04:12:27',
					'load1': '-',
					'load5': '-',
					'requests': 0.6,
					'running': '4 hours',
					'status_sort': 0
				}
			],
			data_poller.collapse_instance_health_data(TestDataPoller.DESCRIBE_INSTANCES_HEALTH)
		)

	def test_format_time_since(self):
		now = datetime.datetime.now()
		five_seconds_ago = now - datetime.timedelta(seconds=5)
		one_minute_ago = now - datetime.timedelta(minutes=1)
		five_minutes_ago = now - datetime.timedelta(minutes=5)
		one_hour_ago = now - datetime.timedelta(hours=1)
		five_hours_ago = now - datetime.timedelta(hours=5)
		one_day_ago = now - datetime.timedelta(days=1)
		five_days_ago = now - datetime.timedelta(days=5)

		with mock.patch('ebcli.display.data_poller._datetime_utcnow_wrapper') as datetime_now_mock:
			datetime_now_mock.return_value = now

			self.assertEqual('-', data_poller.format_time_since(None))
			self.assertEqual('-', data_poller.format_time_since(''))
			self.assertEqual('5 secs', data_poller.format_time_since(five_seconds_ago))
			self.assertEqual('1 min', data_poller.format_time_since(one_minute_ago))
			self.assertEqual('5 mins', data_poller.format_time_since(five_minutes_ago))
			self.assertEqual('1 hour', data_poller.format_time_since(one_hour_ago))
			self.assertEqual('5 hours', data_poller.format_time_since(five_hours_ago))
			self.assertEqual('1 day', data_poller.format_time_since(one_day_ago))
			self.assertEqual('5 days', data_poller.format_time_since(five_days_ago))

	@mock.patch('ebcli.display.data_poller.format_time_since')
	@mock.patch('ebcli.lib.elasticbeanstalk.get_environment_health')
	@mock.patch('ebcli.lib.elasticbeanstalk.get_instance_health')
	def test_get_health_data(
			self,
			get_instance_health_mock,
			get_environment_health_mock,
			format_time_since_mock
	):
		get_environment_health_mock.return_value = TestDataPoller.ENVIRONMENT_HEALTH
		get_instance_health_mock.return_value = TestDataPoller.DESCRIBE_INSTANCES_HEALTH
		format_time_since_mock.return_value = '1 day'

		poller = data_poller.DataPoller('some_app_name', 'some_env_name')
		poller._account_for_clock_drift = mock.MagicMock(return_value=datetime.timedelta(minutes=1))

		self.assertEqual(
			TestDataPoller.GET_HEALTH_DATA_RESULT,
			poller._get_health_data()
		)

	@mock.patch('ebcli.display.data_poller._get_sleep_time')
	@mock.patch('ebcli.display.data_poller.LOG')
	def test_poll_for_health_data(
			self,
			log_mock,
			get_sleep_time_mock
	):
		poller = data_poller.DataPoller('some_app_name', 'some_env_name')
		poller._get_health_data = mock.MagicMock(
			side_effect=[
				mock.MagicMock(return_value=TestDataPoller.GET_HEALTH_DATA_RESULT),
				KeyboardInterrupt
			]
		)
		get_sleep_time_mock.side_effect = [0, 0, KeyboardInterrupt]

		poller._poll_for_health_data()

		calls = [
			mock.call('Starting data poller child thread'),
			mock.call("Sleeping for 0 second(s)"),
			mock.call('Exiting due to: KeyboardInterrupt')
		]

		log_mock.debug.assert_has_calls(calls)
