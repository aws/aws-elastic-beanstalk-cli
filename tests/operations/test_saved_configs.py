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
import shutil
import unittest

from ebcli.core import fileoperations
from ebcli.commands import saved_configs


class TestResolveConfigLocations(unittest.TestCase):
    def setUp(self):
        # set up test directory
        if not os.path.exists('testDir'):
            os.makedirs('testDir/.elasticbeanstalk/')
        os.chdir('testDir')

        # set up mock elastic beanstalk directory
        if not os.path.exists(fileoperations.beanstalk_directory):
            os.makedirs(fileoperations.beanstalk_directory)

    def tearDown(self):
        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            shutil.rmtree('testDir')

    def test_resolve_config_location_full_path(self):
        location = os.path.expanduser(os.getcwd() +
                                      os.path.sep + 'myfile.cfg.yml')
        fileoperations.write_to_file(location, '')

        result = saved_configs.resolve_config_location(location)
        self.assertEqual(result, location)

    def test_resolve_config_location_none(self):
        location = 'badlocation'

        result = saved_configs.resolve_config_location(location)
        self.assertEqual(result, None)

    def test_resolve_config_location_relative_path(self):
        os.makedirs('folder')
        location = '.' + os.path.sep + 'folder/myfile.cfg.yml'
        fileoperations.write_to_file(location, '')

        result = saved_configs.resolve_config_location(location)
        self.assertEqual(result, location)

    def test_resolve_config_location_public(self):
        cfg_name = 'myfile'
        location = cfg_name + '.cfg.yml'
        fileoperations.write_to_eb_file(location, '')

        location = os.path.expanduser(os.getcwd() + os.path.sep +
                                      fileoperations.beanstalk_directory +
                                      location)

        result = saved_configs.resolve_config_location(cfg_name)
        self.assertEqual(result, location)

    def test_resolve_config_location_public_with_extension(self):
        cfg_name = 'myfile.cfg.yml'
        location = cfg_name
        fileoperations.write_to_eb_file(location, '')

        location = os.path.expanduser(os.getcwd() + os.path.sep +
                                      fileoperations.beanstalk_directory +
                                      location)

        result = saved_configs.resolve_config_location(cfg_name)
        self.assertEqual(result, location)

    def test_resolve_config_location_private(self):
        cfg_name = 'myfile'
        location = 'saved_configs' + os.path.sep + cfg_name + '.cfg.yml'
        fileoperations.make_eb_dir('saved_configs')
        fileoperations.write_to_eb_file(location, '')

        location = os.path.expanduser(os.getcwd() + os.path.sep +
                                      fileoperations.beanstalk_directory +
                                      location)

        result = saved_configs.resolve_config_location(cfg_name)
        self.assertEqual(result, location)

    def test_resolve_config_location_private_with_extension(self):
        cfg_name = 'myfile.cfg.yml'
        location = 'saved_configs' + os.path.sep + cfg_name
        fileoperations.make_eb_dir('saved_configs')
        fileoperations.write_to_eb_file(location, '')

        location = os.path.expanduser(os.getcwd() + os.path.sep +
                                      fileoperations.beanstalk_directory +
                                      location)

        result = saved_configs.resolve_config_location(cfg_name)
        self.assertEqual(result, location)

    def test_resolve_config_location_correct_resolve(self):
        # make both, make sure private is resolved
        cfg_name = 'myfile'
        location_public = cfg_name + '.cfg.yml'
        location_private = 'saved_configs' + os.path.sep + cfg_name + '.cfg.yml'
        fileoperations.make_eb_dir('saved_configs')
        fileoperations.write_to_eb_file(location_public, '')
        fileoperations.write_to_eb_file(location_private, '')

        location_public = os.getcwd() + os.path.sep + \
                          fileoperations.beanstalk_directory + location_public
        location_private = os.getcwd() + os.path.sep + \
                           fileoperations.beanstalk_directory + location_private


        result = saved_configs.resolve_config_location(cfg_name)
        self.assertEqual(result, location_private)

    def test_resolve_config_location_correct_resolve_with_extension(self):
        # make both, make sure private is resolved
        cfg_name = 'myfile.cfg.yml'
        location_public = cfg_name
        location_private = 'saved_configs' + os.path.sep + cfg_name
        fileoperations.make_eb_dir('saved_configs')
        fileoperations.write_to_eb_file(location_public, '')
        fileoperations.write_to_eb_file(location_private, '')

        location_public = os.getcwd() + os.path.sep + \
            fileoperations.beanstalk_directory + location_public
        location_private = os.getcwd() + os.path.sep + \
            fileoperations.beanstalk_directory + location_private


        result = saved_configs.resolve_config_location(cfg_name)
        self.assertEqual(result, location_private)