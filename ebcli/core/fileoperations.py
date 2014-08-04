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
from collections import defaultdict

from yaml import load, dump, safe_dump
from six.moves import configparser
from six.moves.configparser import NoSectionError, NoOptionError
from cement.utils.misc import minimal_logger

from ebcli.objects.exceptions import NotInitializedError, NoRegionError

LOG = minimal_logger(__name__)


def get_aws_home():
    sep = os.path.sep
    p = '~' + sep + '.aws' + sep
    return os.path.expanduser(p)


beanstalk_directory = '.elasticbeanstalk' + os.path.sep
global_config_file = beanstalk_directory + 'config.global.yml'
local_config_file = beanstalk_directory + 'config.yml'
aws_config_folder = get_aws_home()
aws_config_location = aws_config_folder + 'config'
aws_access_key = 'aws_access_key_id'
aws_secret_key = 'aws_secret_access_key'
default_section = 'default'
app_version_folder = beanstalk_directory + 'app_versions'


def _get_option(config, section, key, default):
    try:
        return config.get(section, key)
    except (NoSectionError, NoOptionError):
        return default


def read_aws_config_credentials():
    config = configparser.ConfigParser()
    config.read(aws_config_location)

    access_key = _get_option(config, default_section, aws_access_key, None)
    secret_key = _get_option(config, default_section, aws_secret_key, None)

    return access_key, secret_key


def _set_not_none(config, section, option, value):
    if value:
        config.set(section, option, value)


def save_to_aws_config(access_key, secret_key):
    config = configparser.ConfigParser()
    if not os.path.exists(aws_config_folder):
        os.makedirs(aws_config_folder)

    config.read(aws_config_location)
    if default_section not in config.sections():
        config.add_section(default_section)

    _set_not_none(config, default_section, aws_access_key, access_key)
    _set_not_none(config, default_section, aws_secret_key, secret_key)

    with open(aws_config_location, 'w') as f:
        config.write(f)


_marker = object()


def get_application_name(default=_marker):
    result = get_config_setting('global', 'application_name')
    if result is not None:
        return result

    # get_config_setting should throw error if directory is not set up
    LOG.debug('Directory found, but no config or app name exists')
    if default is _marker:
        raise NotInitializedError
    return default


def get_default_region():
    # Don't return an error
    ### We can defer to .aws/config region
    return get_config_setting('global', 'default_region')


def create_config_file(app_name, region):
    """
        We want to make sure we do not override the file if it already exists,
         but we do want to fill in all missing pieces
    :param app_name: name of the application
    :return: VOID: no return value
    """
    LOG.debug('Creating config file at ' + os.getcwd())

    if not os.path.exists(beanstalk_directory):
        os.makedirs(beanstalk_directory)

    # add to global without writing over any settings if they exist
    write_config_setting('global', 'application_name', app_name)
    write_config_setting('global', 'default_region', region)


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


def get_zip_location(file_name):
    cwd = os.getcwd()
    try:
        _traverse_to_project_root()
        if not os.path.exists(app_version_folder):
            # create it
            os.makedirs(app_version_folder)

        return os.path.abspath(app_version_folder) + os.path.sep + file_name

    finally:
        os.chdir(cwd)


def get_environment_from_file():
    pass


def get_environments_from_files():
    pass


def save_env_file(env, public=False, paused=False):
    cwd = os.getcwd()
    env_name = env['EnvironmentName']
    if public:
        file_name = env_name + '.ebe.yml'
    elif paused:
        file_name = env_name + '.paused-env.yml'
    else:
        file_name = env_name + '.env.yml'

    file_name = beanstalk_directory + file_name
    try:
        _traverse_to_project_root()

        with open(file_name, 'w') as f:
            f.write(safe_dump(env, default_flow_style=False))

    finally:
        os.chdir(cwd)


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