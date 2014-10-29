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

from ..core import io


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
    lst = list_to_columns(lst)
    index = 0
    for x in range(0, len(lst[0])):
        line = []
        for i in range(0, len(lst)):
            try:
                line.append(lst[i][x])
            except IndexError:
                pass

        #Note: This function is only intended for env_name, which are
        ## Guaranteed to be 23 characters or less
        io.echo_and_justify(25, *line)


def list_to_columns(lst):
    assert len(lst) > 4, "List size must be greater than 4"
    COLUMN_NUM = 4
    remainder = len(lst) % COLUMN_NUM
    column_size = len(lst) // COLUMN_NUM
    if remainder != 0:
        column_size += 1
    colunms = [[], [], [], []]
    index = 0
    stop = column_size
    for x in range(0, COLUMN_NUM):
        colunms[x] += lst[index:stop]
        index = stop
        stop += column_size
    return colunms


def is_ssh():
    return "SSH_CLIENT" in os.environ or "SSH_TTY" in os.environ
