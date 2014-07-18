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

import os

from yaml import load, dump
from six.moves import configparser
from six.moves.configparser import NoSectionError
from six.moves.configparser import NoOptionError
from cement.utils.misc import minimal_logger

from ebcli.objects.exceptions import NotInitializedError

LOG = minimal_logger(__name__)


def get_aws_home():
    p = '~' + os.path.sep + '.aws' + os.path.sep
    return os.path.expanduser(p)


beanstalk_directory = '.elasticbeanstalk' + os.path.sep
global_config_file = beanstalk_directory + 'config.global.yaml'
local_config_file = beanstalk_directory + 'config.yaml'
aws_config_folder = get_aws_home()
aws_config_location = aws_config_folder + 'config'
aws_access_key = 'aws_access_key_id'
aws_secret_key = 'aws_secret_access_key'
aws_region = 'region'
default_section = 'default'


def read_aws_config_credentials():
    config = configparser.ConfigParser()
    config.read(aws_config_location)
    try:
        access_key = config.get(default_section,aws_access_key)
    except NoSectionError, NoOptionError:
        access_key = None
    try:
        secret_key = config.get(default_section, aws_secret_key)
    except NoSectionError, NoOptionError:
        secret_key = None
    try:
        region = config.get(default_section, aws_region)
    except NoSectionError, NoOptionError:
        region = None
    return access_key, secret_key, region


def save_to_aws_config(access_key, secret_key, region):
    config = configparser.ConfigParser()
    if not os.path.exists(aws_config_folder):
        os.makedirs(aws_config_folder)

    config.read(aws_config_location)
    if default_section not in config.sections():
        config.add_section(default_section)

    config.set(default_section, aws_access_key, access_key)
    config.set(default_section, aws_secret_key, secret_key)
    config.set(default_section, aws_region, region)

    with open(aws_config_location, 'wb') as f:
        config.write(f)


def _try_read_credential_file():
    pass

def read_credential_file():
    location = '.elasticbeanstalk' + os.path.sep + 'config'

def get_directory_name():
    pass



def get_application_name():
    return get_config_setting('global', 'application_name')


def create_config_file(app_name):
    """
        We want to make sure we do not override the file if it already exists,
         but we do want to fill in all missing pieces
    :param app_name: name of the application
    :return: VOID: no return value
    """
    LOG.debug('Creating config file at ' + os.getcwd())
    location = local_config_file

    if not os.path.exists(beanstalk_directory):
        os.makedirs(beanstalk_directory)

    # add to global without writing over any settings if they exist
    write_config_setting('global', 'application_name', app_name)


def _traverse_to_project_root():
    cwd = os.getcwd()
    if not os.path.exists(beanstalk_directory):
        LOG.debug('beanstalk directory not found in ' + cwd +
                  '  -Going up a level')
        os.chdir(os.path.pardir)  # Go up one directory

        if cwd == os.getcwd():  # We can't move any further
            LOG.debug('Still at the same directory ' + cwd)
            raise NotInitializedError('EB is not yet initialized')

        _traverse_to_project_root()

    else:
        LOG.debug('Project root found at: ' + cwd)


def write_config_setting(section, key_name, value):
    cwd = os.getcwd()  # save working directory
    try:
        _traverse_to_project_root()

        config = _get_yaml_dict(local_config_file)
        if not config:
            config = {}
        config.setdefault(section, {})[key_name] = value

        with open(local_config_file, 'w') as f:
            f.write(dump(config, default_flow_style=False))

    finally:
        os.chdir(cwd)  # go back to working directory


def get_config_setting(section, key_name):
    # get setting from global if it exists
    cwd = os.getcwd()  # save working directory
    try:
        _traverse_to_project_root()

        config_global = _get_yaml_dict(global_config_file)
        config_local = _get_yaml_dict(local_config_file)

        # Grab value, local gets priority
        try:
            value = config_global[section][key_name]
        except KeyError:
            value = None

        try:
            if config_local:
                value = config_local[section][key_name]
        except KeyError:
            pass  # Revert to global value

    finally:
        os.chdir(cwd)  # move back to working directory
    return value


def _get_yaml_dict(filename):
    try:
        with open(filename, 'r') as f:
            return load(f)
    except IOError:
        return {}