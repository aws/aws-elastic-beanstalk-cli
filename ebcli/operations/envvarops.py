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


from botocore.compat import six
from six import iteritems

from ..lib import elasticbeanstalk, utils
from ..core import io
from ..resources.strings import strings
from ..objects.exceptions import TimeoutError
from . import commonops


def get_and_print_environment_vars(app_name, env_name):
    settings = elasticbeanstalk.describe_configuration_settings(
        app_name, env_name
    )['OptionSettings']
    namespace = 'aws:elasticbeanstalk:application:environment'
    vars = {n['OptionName']: n['Value'] for n in settings
            if n["Namespace"] == namespace}
    print_environment_vars(vars)


def print_environment_vars(vars):
    io.echo(' Environment Variables:')
    for key, value in iteritems(vars):
        key, value = utils.mask_vars(key, value)
        io.echo('    ', key, '=', value)


def setenv(app_name, env_name, var_list, timeout=None):

    options, options_to_remove = commonops.create_envvars_list(var_list)

    request_id = elasticbeanstalk.update_environment(env_name, options,
                                                     remove=options_to_remove)
    try:
        if timeout is None:
            timeout = 4
        commonops.wait_for_success_events(request_id,
                                          timeout_in_minutes=timeout,
                                          can_abort=True)
    except TimeoutError:
        io.log_error(strings['timeout.error'])
