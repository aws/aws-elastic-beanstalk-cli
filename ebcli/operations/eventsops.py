# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import os

import time
from ..core import io
from ..lib import elasticbeanstalk
from ..resources.strings import prompts
from . import commonops


def print_events(app_name, env_name, follow):
    if follow:
        follow_events(app_name, env_name)
    else:

        events = elasticbeanstalk.get_new_events(
            app_name, env_name, None)

        data = []
        for event in reversed(events):
            data.append(commonops.get_event_string(event, long_format=True))
        io.echo_with_pager(os.linesep.join(data))


def follow_events(app_name, env_name):
    last_time = None
    streamer = io.get_event_streamer()
    try:
        while True:
            events = elasticbeanstalk.get_new_events(
                app_name, env_name, None, last_event_time=last_time
            )

            for event in reversed(events):
                message = commonops.get_event_string(event)
                streamer.stream_event(message)
                last_time = event.event_date

            time.sleep(4)
    finally:
        streamer.end_stream()