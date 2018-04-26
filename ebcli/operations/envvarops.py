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
import re
from six import iteritems

from ebcli.lib import elasticbeanstalk, utils
from ebcli.core import io
from ebcli.objects.exceptions import InvalidOptionsError, InvalidSyntaxError
from ebcli.resources.strings import strings
from ebcli.operations import commonops


def get_and_print_environment_vars(app_name, env_name):
    settings = elasticbeanstalk.describe_configuration_settings(
        app_name, env_name
    )['OptionSettings']
    namespace = 'aws:elasticbeanstalk:application:environment'
    vars = {n['OptionName']: n['Value'] for n in settings
            if n["Namespace"] == namespace}
    print_environment_vars(vars)


def sanitize_environment_variables_from_customer_input(environment_variables_input):
    """
    Returns a list of the sanitized key-value pairs in the `environment_variables_input` string,
    where pairs are comma-separated, by removing leading and trailing spaces and double quotes
    from and the key and value of each pair.

    :param environment_variables_input: a string of the form "KEY_1=VALUE_1,...,KYE_N=VALUE_N"
    :return: a list of the sanitized key-value pairs
    """
    if not environment_variables_input:
        return []

    key_value_pairs = environment_variables_input.split(',')

    environment_variables = []
    for key_value_pair in key_value_pairs:
        if '=' not in key_value_pair:
            raise InvalidSyntaxError(strings['setenv.invalidformat'])

        key, value = key_value_pair.split('=', maxsplit=1)
        key = key.strip().strip('"')
        value = value.strip().strip('"')

        if not key:
            raise InvalidSyntaxError(strings['setenv.invalidformat'])

        environment_variables.append('='.join([key, value]))

    return environment_variables


def create_environment_variables_list(environment_variables, as_option_settings=True):
    """
    Returns a pair of environment variables to add and remove from a list of sanitized environment variables.

    If `as_option_settings` is set to `True`, the list of environment variables to add is transformed
    into option settings in the 'aws:elasticbeanstalk:application:environment' namespace.

    :param environment_variables: a list of the sanitized environment variables specified in the format KEY_i=VALUE_i
    :param as_option_settings: boolean indicating whether to transform `environment_variables` into option settings
    :return: a pair of environment variables to add and remove in the format dictated by `as_option_settings`
    """
    namespace = 'aws:elasticbeanstalk:application:environment'

    options = dict()
    options_to_remove = set()
    for environment_variable_string in environment_variables:
        if (
            not re.match('^[\w\\_.:/+@-][^=]*=.*$', environment_variable_string)
            or '=' not in environment_variable_string
        ):
            raise InvalidSyntaxError(strings['setenv.invalidformat'])

        environment_variable, value = environment_variable_string.split('=', maxsplit=1)

        if value:
            options[environment_variable] = value
        else:
            options_to_remove.add(environment_variable)

    if as_option_settings:
        option_dict = options
        options = list()
        remove_list = options_to_remove
        options_to_remove = list()
        for k, v in iteritems(option_dict):
            options.append(
                dict(Namespace=namespace,
                     OptionName=k,
                     Value=v))

        for k in remove_list:
            options_to_remove.append(
                dict(Namespace=namespace,
                     OptionName=k))

    return options, options_to_remove


def print_environment_vars(vars):
    io.echo(' Environment Variables:')
    for key, value in iteritems(vars):
        key, value = utils.mask_vars(key, value)
        io.echo('    ', key, '=', value)


def setenv(app_name, env_name, var_list, timeout=None):

    options, options_to_remove = create_environment_variables_list(var_list)

    request_id = elasticbeanstalk.update_environment(env_name, options,
                                                     remove=options_to_remove)

    if timeout is None:
        # specify a lower timeout duration because the `UpdateEnvironment`
        # workflow does not take very long to just set environment variables.
        timeout = 4

    commonops.wait_for_success_events(request_id,
                                      timeout_in_minutes=timeout,
                                      can_abort=True)
