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

import six
from six import print_
from six.moves import input
import logging

from ebcli.core import globals

LOG = logging.getLogger(__name__)


def echo(*args):
    print_(*_convert_to_strings(args), sep=' ')


def _convert_to_strings(list_of_things):
    scalar_types = six.string_types + six.integer_types
    for data in list_of_things:
        if isinstance(data, scalar_types) or hasattr(data, '__str__'):
            yield str(data)
        else:
            LOG.error('echo called with an unsupported data type')


def log_info(message):
    globals.app.log.info(message)


def log_warning(message):
    globals.app.log.warn(message)


def log_error(message):
    globals.app.log.error(message)


def get_input(output):
    # Don't except blank inputs
    # Trim spaces
    while True:
        result = input(output + ': ').strip()
        if result:
            break
        else:
            echo('Blank inputs are not allowed. Please try again.')
    return result


def prompt(output):
    return get_input('(' + output + ')')


def prompt_for_environment_name():
    # Validate env_name: Spec says:
    # Constraint: Must be from 4 to 23 characters in length.
    # The name can contain only letters, numbers, and hyphens.
    # It cannot start or end with a hyphen.
    while True:
        env_name = prompt('environment name')
        if re.match('^[a-z0-9][a-z0-9-]{2,21}[a-z0-9]$', env_name.lower()):
            break
        else:
            echo('Environment name be 4 to 23 characters in length. It can'
                 ' only contain letters, numbers, and hyphens. It can not '
                 'start or end with a hyphen')

    return env_name


def prompt_for_cname():
    # Validate cname: spec says:
    # Constraint: Must be from 4 to 23 characters in length.
    # The name can contain only letters, numbers, and hyphens.
    # It cannot start or end with a hyphen.
    while True:
        cname = prompt('cname prefix')
        if re.match('^[a-z0-9][a-z0-9-]{2,61}[a-z0-9]$', cname.lower()):
            break
        else:
            echo('CNAME can be 4 to 63 characters in length. It can'
                 ' only contain letters, numbers, and hyphens. It can not '
                 'start or end with a hyphen')

    return cname