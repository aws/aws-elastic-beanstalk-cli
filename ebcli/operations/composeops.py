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

import time

from ..lib import elasticbeanstalk
from ..core import io
from ..objects.exceptions import TimeoutError
from ..resources.strings import strings
from . import commonops


def compose(app_name, version_labels, grouped_env_names, group_name=None,
            nohang=False, timeout=None):

    success = commonops.wait_for_processed_app_versions(app_name, version_labels)
    if not success:
        return

    request_id = compose_apps(app_name, version_labels, group_name)

    if nohang:
        return

    try:
        commonops.wait_for_compose_events(request_id, app_name, grouped_env_names, timeout)
    except TimeoutError:
        io.log_error(strings['timeout.error'])


def compose_apps(app_name, version_labels, group_name=None):
    io.echo('--- Creating modules ---')
    request_id = elasticbeanstalk.compose_environments(app_name, version_labels,
                                                       group_name)
    return request_id


def compose_no_events(app_name, version_labels, group_name=None):
    success = commonops.wait_for_processed_app_versions(app_name, version_labels)
    if not success:
        return None

    return compose_apps(app_name, version_labels, group_name)

