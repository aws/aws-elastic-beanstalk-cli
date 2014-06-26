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

from datetime import datetime, timedelta

from lib.elasticbeanstalk import get_new_events

def wait_and_print_status(timeout_in_seconds):
    start = datetime.now()
    timediff = timedelta(seconds = timeout_in_seconds)

    status_green = False
    while not status_green and (datetime.now() - start) > timediff:
        #sleep a little
        last_time = ''
        results = get_new_events('testappname', last_event_time=last_time)

        for event in results:
            #print each event message
            #save event time as last_time
            pass

        #compare for green message last
        # message is in strings.responses['event.greenmessage']



