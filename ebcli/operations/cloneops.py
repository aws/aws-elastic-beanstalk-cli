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

import re

from cement.utils.misc import minimal_logger

from ..lib import elasticbeanstalk, utils
from ..lib.aws import InvalidParameterValueError
from ..core import io
from ..objects.exceptions import TimeoutError
from ..resources.strings import strings, responses, prompts
from . import commonops


LOG = minimal_logger(__name__)


def make_cloned_env(clone_request, nohang=False, timeout=None):
    io.log_info('Cloning environment')
    # get app version from environment
    env = elasticbeanstalk.get_environment(clone_request.app_name,
                                           clone_request.original_name)
    clone_request.version_label = env.version_label
    result, request_id = clone_env(clone_request)

    # Print status of env
    commonops.print_env_details(result, health=False)

    if nohang:
        return

    io.echo('Printing Status:')
    try:
        commonops.wait_for_success_events(request_id, timeout_in_minutes=timeout)
    except TimeoutError:
        io.log_error(strings['timeout.error'])


def clone_env(clone_request):
    while True:
        try:
            return elasticbeanstalk.clone_environment(clone_request)
        except InvalidParameterValueError as e:
            LOG.debug('cloning env returned error: ' + e.message)
            if re.match(responses['env.cnamenotavailable'], e.message):
                io.echo(prompts['cname.unavailable'])
                clone_request.cname = io.prompt_for_cname()
            elif re.match(responses['env.nameexists'], e.message):
                io.echo(strings['env.exists'])
                current_environments = commonops.get_env_names(
                    clone_request.app_name)
                unique_name = utils.get_unique_name(clone_request.env_name,
                                                    current_environments)
                clone_request.env_name = io.prompt_for_environment_name(
                    default_name=unique_name)
            else:
                raise

            # try again