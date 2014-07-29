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

import six
from six import print_
from six.moves import input
import logging

from ebcli.core import globals

LOG = logging.getLogger(__name__)


def echo(*args):
    for data in args:
        if isinstance(data, six.string_types) \
                    or isinstance(data, six.integer_types):
            print_(data, end=' ')
        else:
            op = getattr(data, '__str__', None)
            if op:
                print_(data.__str__(), end=' ')
            else:
                LOG.error("echo called with an unsupported data type")
    print_('')


def log_info(message):
    globals.app.log.info(message)


def log_warning(message):
    globals.app.log.warn(message)


def log_error(message):
    globals.app.log.error(message)


def get_input(output):
    return input(output + ': ')


def prompt(output):
    return get_input('(' + output + ')')