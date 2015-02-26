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
import warnings
import sys
import os
import platform
import subprocess

from botocore.compat import six
from six.moves import urllib

from ..core import io, fileoperations


def prompt_for_item_in_list(lst, default=1):
    for x in range(0, len(lst)):
        io.echo(str(x + 1) + ')', lst[x])

    while True:
        try:
            choice = int(io.prompt('default is ' + str(default),
                                   default=default))
            if not (0 < choice <= len(lst)):
                raise ValueError  # Also thrown by non int numbers
            else:
                break
        except ValueError:
            io.echo('Sorry, that is not a valid choice. '
                    'Please choose a number between 1 and ' +
                    str(len(lst)) + '.')
    return lst[choice - 1]


def get_unique_name(name, current_uniques):
    # with warnings.catch_warnings():
    #     warnings.simplefilter('ignore')
    #     if sys.version_info[0] >= 3:
    #         base_name = name
    #     else:
    #         base_name = name.decode('utf8')
    base_name = name

    number = 2
    while base_name in current_uniques:
        base_name = name + str(number)
        number += 1

    return base_name


def mask_vars(key, value):
    if (re.match('.*_CONNECTION_STRING', key) or
                key == 'AWS_ACCESS_KEY_ID' or
                key == 'AWS_SECRET_KEY') \
        and value is not None:
            value = "*****"

    return key, value


def print_list_in_columns(lst):
    """
    This function is currently only intended for environmant names,
    which are guaranteed to be 23 characters or less.
    :param lst: List of env names
    """
    if sys.stdout.isatty():
        lst = list_to_columns(lst)
        index = 0
        for x in range(0, len(lst[0])):
            line = []
            for i in range(0, len(lst)):
                try:
                    line.append(lst[i][x])
                except IndexError:
                    pass

            io.echo_and_justify(25, *line)
    else:
        # Dont print in columns if using pipe
        for i in lst:
            io.echo(i)


def list_to_columns(lst):
    COLUMN_NUM = 3
    assert len(lst) > COLUMN_NUM, "List size must be greater than {0}".\
        format(COLUMN_NUM)
    remainder = len(lst) % COLUMN_NUM
    column_size = len(lst) // COLUMN_NUM
    if remainder != 0:
        column_size += 1
    colunms = [[] for i in range(0, COLUMN_NUM)]
    index = 0
    stop = column_size
    for x in range(0, COLUMN_NUM):
        colunms[x] += lst[index:stop]
        index = stop
        stop += column_size
    return colunms


def url_encode(data):
    return urllib.parse.quote(data)


def is_ssh():
    return "SSH_CLIENT" in os.environ or "SSH_TTY" in os.environ


def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate


def get_data_from_url(url, timeout=20):
    return urllib.request.urlopen(url, timeout=timeout).read()


def print_from_url(url):
    result = get_data_from_url(url)
    io.echo(result)


def save_file_from_url(url, location, filename):
    result = get_data_from_url(url)

    return fileoperations.save_to_file(result, location, filename)