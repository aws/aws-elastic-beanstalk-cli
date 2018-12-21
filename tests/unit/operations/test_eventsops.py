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
import os

from dateutil import tz
import mock
from pytest_socket import enable_socket, disable_socket
import unittest

from ebcli.operations import eventsops
from ebcli.objects.event import Event


class TestEventOps(unittest.TestCase):
    def setUp(self):
        disable_socket()

    def tearDown(self):
        enable_socket()

    @mock.patch('ebcli.operations.eventsops.io.get_event_streamer')
    @mock.patch('ebcli.operations.eventsops.elasticbeanstalk.get_new_events')
    @mock.patch('ebcli.operations.eventsops._sleep')
    def test_follow_events(
            self,
            _sleep_mock,
            get_new_events_mock,
            get_event_streamer_mock
    ):
        get_new_events_mock.side_effect = [
            [event]
            for event in
            Event.json_to_event_objects(
                [
                    {
                        'EventDate': datetime.datetime(2018, 7, 19, 21, 50, 21, 623000, tzinfo=tz.tzutc()),
                        'Message': 'Successfully launched environment: eb-locust-example-windows-server-dev',
                        'ApplicationName': 'eb-locust-example-windows-server',
                        'EnvironmentName': 'eb-locust-example-windows-server-dev',
                        'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
                        'Severity': 'INFO'
                    },
                    {
                        'EventDate': datetime.datetime(2018, 7, 19, 21, 50, 0, 909000, tzinfo=tz.tzutc()),
                        'Message': 'Environment health has transitioned from Pending to Ok. Initialization completed 26 seconds ago and took 5 minutes.',
                        'ApplicationName': 'eb-locust-example-windows-server',
                        'EnvironmentName': 'eb-locust-example-windows-server-dev',
                        'Severity': 'INFO'
                    },
                    {
                        'EventDate': datetime.datetime(2018, 7, 19, 21, 49, 10, tzinfo=tz.tzutc()),
                        'Message': "Nginx configuration detected in the '.ebextensions/nginx' directory. AWS Elastic Beanstalk will no longer manage the Nginx configuration for this environment.",
                        'ApplicationName': 'eb-locust-example-windows-server',
                        'EnvironmentName': 'eb-locust-example-windows-server-dev',
                        'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
                        'Severity': 'INFO'
                    }
                ]
            )
        ]
        _sleep_mock.side_effect = [
            mock.MagicMock(),
            mock.MagicMock(),
            eventsops.EndOfTestError
        ]
        streamer_mock = eventsops.io.get_event_streamer()
        streamer_mock.stream_event = mock.MagicMock()
        get_event_streamer_mock.return_value = streamer_mock

        eventsops.follow_events('my-application', 'environment-1')

        streamer_mock.stream_event.assert_has_calls(
            [
                mock.call('2018-07-19 21:50:21    INFO    Successfully launched environment: eb-locust-example-windows-server-dev'),
                mock.call('2018-07-19 21:50:00    INFO    Environment health has transitioned from Pending to Ok. Initialization completed 26 seconds ago and took 5 minutes.'),
                mock.call("2018-07-19 21:49:10    INFO    Nginx configuration detected in the '.ebextensions/nginx' directory. AWS Elastic Beanstalk will no longer manage the Nginx configuration for this environment.")
            ]
        )
        streamer_mock.end_stream.assert_called_once_with()

    @mock.patch('ebcli.operations.eventsops.io.echo_with_pager')
    @mock.patch('ebcli.operations.eventsops.elasticbeanstalk.get_new_events')
    def test_print_events(
            self,
            get_new_events_mock,
            echo_with_pager_mock
    ):
        get_new_events_mock.return_value = Event.json_to_event_objects(
            [
                {
                    'EventDate': datetime.datetime(2018, 7, 19, 21, 50, 21, 623000, tzinfo=tz.tzutc()),
                    'Message': 'Successfully launched environment: eb-locust-example-windows-server-dev',
                    'ApplicationName': 'eb-locust-example-windows-server',
                    'EnvironmentName': 'eb-locust-example-windows-server-dev',
                    'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
                    'Severity': 'INFO'
                },
                {
                    'EventDate': datetime.datetime(2018, 7, 19, 21, 50, 0, 909000, tzinfo=tz.tzutc()),
                    'Message': 'Environment health has transitioned from Pending to Ok. Initialization completed 26 seconds ago and took 5 minutes.',
                    'ApplicationName': 'eb-locust-example-windows-server',
                    'EnvironmentName': 'eb-locust-example-windows-server-dev',
                    'Severity': 'INFO'
                },
                {
                    'EventDate': datetime.datetime(2018, 7, 19, 21, 49, 10, tzinfo=tz.tzutc()),
                    'Message': "Nginx configuration detected in the '.ebextensions/nginx' directory. AWS Elastic Beanstalk will no longer manage the Nginx configuration for this environment.",
                    'ApplicationName': 'eb-locust-example-windows-server',
                    'EnvironmentName': 'eb-locust-example-windows-server-dev',
                    'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
                    'Severity': 'INFO'
                }
            ]
        )

        eventsops.print_events('my-application', 'environment-1', False)

        get_new_events_mock.assert_called_once_with('my-application', 'environment-1', None, platform_arn=None)
        echo_with_pager_mock.assert_called_once_with(
            os.linesep.join(
                [
                    "2018-07-19 21:49:10    INFO    Nginx configuration detected in the '.ebextensions/nginx' directory. AWS Elastic Beanstalk will no longer manage the Nginx configuration for this environment.",
                    '2018-07-19 21:50:00    INFO    Environment health has transitioned from Pending to Ok. Initialization completed 26 seconds ago and took 5 minutes.',
                    '2018-07-19 21:50:21    INFO    Successfully launched environment: eb-locust-example-windows-server-dev',
                ]
            )
        )

    @mock.patch('ebcli.operations.eventsops.follow_events')
    def test_print_events__follow_events(
            self,
            follow_events_mock
    ):
        eventsops.print_events('my-application', 'environment-1', True)

        follow_events_mock.assert_called_once_with('my-application', 'environment-1', None)
