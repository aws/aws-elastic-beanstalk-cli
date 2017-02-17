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


class Event():
    def __init__(self, message=None, event_date=None, version_label=None,
                 app_name=None, environment_name=None, severity=None, platform=None):
        self.message = message
        self.event_date = event_date
        self.version_label = version_label
        self.app_name = app_name
        self.environment_name = environment_name
        self.severity = severity
        self.platform = platform
