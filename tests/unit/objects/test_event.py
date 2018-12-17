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
import unittest

from ebcli.objects.event import Event


class TestEvent(unittest.TestCase):
    def test_events__equal(self):
        event_1 = {
            'EventDate': '2018-03-12T22:14:14.292Z',
            'Message': 'Deleting SNS topic for environment my-environment.',
            'ApplicationName': 'application-name',
            'EnvironmentName': 'my-environment',
            'RequestId': '23141234-134adsfasdf-12341234',
            'Severity': 'INFO'
        }

        event_2 = {
            'EventDate': '2018-03-12T22:14:14.292Z',
            'Message': 'Deleting SNS topic for environment my-environment.',
            'ApplicationName': 'application-name',
            'EnvironmentName': 'my-environment',
            'RequestId': '23141234-134adsfasdf-12341234',
            'Severity': 'INFO'
        }

        events = Event.json_to_event_objects(
            [
                event_1,
                event_2
            ]
        )

        self.assertEqual(events[0], events[1])

    def test_events__unequal(self):
        # 'ApplicationName' is misspelt
        event_1 = {
            'EventDate': '2018-03-12T22:14:14.292Z',
            'Message': 'Deleting SNS topic for environment my-environment.',
            'ApplicationName': 'applicaion-name',
            'EnvironmentName': 'my-environment',
            'RequestId': '23141234-134adsfasdf-12341234',
            'Severity': 'INFO'
        }

        # 'Severity' differs
        event_2 = {
            'EventDate': '2018-03-12T22:14:14.292Z',
            'Message': 'Deleting SNS topic for environment my-environment.',
            'ApplicationName': 'applicaion-name',
            'EnvironmentName': 'my-environment',
            'RequestId': '23141234-134adsfasdf-12341234',
            'Severity': 'SEVERE'
        }

        # candidate Event object
        event_candidate = {
            'EventDate': '2018-03-12T22:14:14.292Z',
            'Message': 'Deleting SNS topic for environment my-environment.',
            'ApplicationName': 'application-name',
            'EnvironmentName': 'my-environment',
            'RequestId': '23141234-134adsfasdf-12341234',
            'Severity': 'INFO'
        }

        events = Event.json_to_event_objects(
            [
                event_1,
                event_candidate
            ]
        )

        self.assertNotEqual(events[0], events[1])

        events = Event.json_to_event_objects(
            [
                event_2,
                event_candidate
            ]
        )

        self.assertNotEqual(events[0], events[1])

