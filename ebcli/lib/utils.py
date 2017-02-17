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
import argparse
import os
import re
import pkg_resources
import sys
from datetime import datetime

from dateutil import tz

from botocore.compat import six
from cement.utils.misc import minimal_logger
from subprocess import Popen, PIPE, STDOUT
urllib = six.moves.urllib

from ebcli.objects.exceptions import CommandError, InvalidOptionsError
from ebcli.core import io, fileoperations

LOG = minimal_logger(__name__)

def prompt_for_item_in_list(lst, default=1):
    ind = prompt_for_index_in_list(lst, default)
    return lst[ind]


def prompt_for_index_in_list(lst, default=1):
    lst = list(lst)
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
    return choice - 1


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

            io.echo_and_justify(42, *line)
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


def get_delta_from_now_and_datetime(date):
    return datetime.now(tz.tzlocal()) - get_local_time(date)


def get_local_time(utctime):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utctime = utctime.replace(tzinfo=from_zone)
    return utctime.astimezone(to_zone)


def get_local_time_as_string(utctime):
    localtime = get_local_time(utctime)
    return localtime.strftime("%Y-%m-%d %H:%M:%S")


def is_ssh():
    return "SSH_CLIENT" in os.environ or "SSH_TTY" in os.environ


def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate


def exec_cmd(args, live_output=True):
    """
    Execute a child program (args) in a new process. Displays
    live output by default.
    :param args: list: describes the command to be run
    :param live_output: bool: whether to print live output
    :return str: child program output
    """

    LOG.debug(' '.join(args))

    process = Popen(args, stdout=PIPE, stderr=STDOUT)
    output = []

    for line in iter(process.stdout.readline, b''):
        line = line.decode('utf-8')
        if line != os.linesep:
            if live_output:
                sys.stdout.write(line)
                sys.stdout.flush()
            else:
                LOG.debug(line)

        output.append(line)

    process.stdout.close()
    process.wait()

    returncode = process.returncode
    error_msg = 'Exited with return code {}'.format(returncode)
    output_str = ''.join(output)

    if returncode:
        raise CommandError(error_msg, output_str, returncode)
    return output_str


exec_cmd_live_output = exec_cmd


def exec_cmd_quiet(args):
    return exec_cmd(args, False)


def flatten(lists):
    """
    Return a new (shallow) flattened list.
    :param lists: list: a list of lists
    :return list
    """

    return [item for sublist in lists for item in sublist]


def anykey(d):
    """
    Return any key in dictionary.
    :param d: dict: dictionary
    :return object
    """
    return next(six.iterkeys(d))


def last_modified_file(filepaths):
    """
    Return the most recently modified file.
    :param filepaths: list: paths to files
    :return str
    """

    return max(filepaths, key=os.path.getmtime)


def get_data_from_url(url, timeout=20):
    return urllib.request.urlopen(url, timeout=timeout).read()


def print_from_url(url):
    result = get_data_from_url(url)
    io.echo(result)


def parse_version(version_string):
    """
    Parse string as a verison object for comparison
    Example: parse_version('1.9.2') > parse_version('1.9.alpha')
    See docs for pkg_resource.parse_version as this is just a wrapper
    """
    return pkg_resources.parse_version(version_string)


def save_file_from_url(url, location, filename):
    result = get_data_from_url(url)

    return fileoperations.save_to_file(result, location, filename)


# http://stackoverflow.com/a/5164027
def prettydate(d):
    """
    Return a human readable str of how long d was compared to now.
    :param d: datetime/float: datetime or unix timestamp
    :return str
    """

    if isinstance(d, float):  # epoch timestamp
        d = datetime.utcfromtimestamp(d)

    diff = datetime.utcnow() - d
    s = diff.seconds
    if diff.days > 7 or diff.days < 0:
        return d.strftime('%d %b %y')
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{0} days ago'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{0} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{0} minutes ago'.format(s // 60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{0} hours ago'.format(s // 3600)


def merge_dicts(low_priority, high_priority):
    """
    Return a new dict that is a merge of low_priority and high_priority dicts.
    When keys collide, takes the value of higher_priority dict.
    :param low_priority: dict: shallow dictionary
    :param high_priority: dict: shallow dictionary
    :return dict
    """

    result_dict = low_priority.copy()
    result_dict.update(high_priority)
    return result_dict


def retract_string(string):
    try:
        string_len = len(string)
        keep_characters = range(0, 4)
        keep_characters.extend(range(string_len - 4, string_len))
        retracted_string = []
        for i, c in enumerate(string):
            if i in keep_characters:
                retracted_string.append(c)
            else:
                retracted_string.append('*')
        return ''.join(retracted_string)
    except:
        return ''


def check_source(value):
    match = re.match(r"([^/]+/[^/]+/[^/]+)", value)
    if match is None or len(value.split("/")) > 3:
        raise argparse.ArgumentTypeError(
            "%s is a invalid source. Example source would be something like: codecommit/repo/branch" % value)
    return value


def parse_source(source):
    # Source is already validated by the check_source method.
    if source is None:
        return

    split_source = source.split('/')

    # Validate that we support the source location
    source_location = split_source[0].lower()
    validate_source_location(source_location)

    repository = split_source[1]
    branch = split_source[2]
    return source_location, repository, branch


def validate_source_location(source_location):
    valid_source_locations = ['codecommit']
    if source_location in valid_source_locations:
        return
    else:
        raise InvalidOptionsError("Source location '{0}' is not in the list of valid locations: {1}".format(source_location, valid_source_locations))


def encode_to_ascii(unicode_value):
    empty_string = ""
    if unicode_value is None:
        return empty_string
    return unicode_value.encode('ascii', 'ignore')


def decode_bytes(value):
    if sys.version_info[0] >= 3:
        if isinstance(value, bytes):
            value = value.decode('utf8')
    return value