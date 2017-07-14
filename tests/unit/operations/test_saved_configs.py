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
import sys
import mock

from ebcli.core import fileoperations
from ebcli.operations import saved_configs


class TestResolveConfigLocations(unittest.TestCase):
    module_name = 'test2'
    app_name = 'app_name'
    platform = 'python'
    cfg_name = 'myfile.cfg.yml'


    def setUp(self):
        # set up test directory
        if not os.path.exists('testDir'):
            os.makedirs('testDir/.elasticbeanstalk/')
        os.chdir('testDir')

        # set up mock elastic beanstalk directory
        if not os.path.exists(fileoperations.beanstalk_directory):
            os.makedirs(fileoperations.beanstalk_directory)

        if sys.version_info[0] >= 3:
            self.data = bytes('', 'UTF-8')
        else:
            self.data = ''


    def tearDown(self):
        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            if sys.platform.startswith('win'):
                os.system('rmdir /S /Q testDir')
            else:
                shutil.rmtree('testDir')

    def test_resolve_config_location_full_path(self):
        location = os.path.expanduser(os.getcwd() +
                                      os.path.sep + 'myfile.cfg.yml')
        fileoperations.write_to_data_file(location, self.data)

        result = saved_configs.resolve_config_location(location)
        self.assertEqual(result, location)

    def test_resolve_config_location_none(self):
        location = 'badlocation'

        result = saved_configs.resolve_config_location(location)
        self.assertEqual(result, None)

    def test_resolve_config_location_relative_path(self):
        os.makedirs('folder')
        location = '.' + os.path.sep + 'folder/myfile.cfg.yml'
        fileoperations.write_to_data_file(location, self.data)

        result = saved_configs.resolve_config_location(location)
        self.assertEqual(result, os.path.abspath(location))

    def test_resolve_config_location_public(self):
        cfg_name = 'myfile'
        location = cfg_name + '.cfg.yml'
        fileoperations.write_to_eb_data_file(location, self.data)

        location = os.path.expanduser(os.getcwd() + os.path.sep +
                                      fileoperations.beanstalk_directory +
                                      location)

        result = saved_configs.resolve_config_location(cfg_name)
        self.assertEqual(result, location)

    def test_resolve_config_location_public_with_extension(self):
        cfg_name = 'myfile.cfg.yml'
        location = cfg_name
        fileoperations.write_to_eb_data_file(location, self.data)

        location = os.path.expanduser(os.getcwd() + os.path.sep +
                                      fileoperations.beanstalk_directory +
                                      location)

        result = saved_configs.resolve_config_location(cfg_name)
        self.assertEqual(result, location)

    def test_resolve_config_location_private(self):
        cfg_name = 'myfile'
        location = 'saved_configs' + os.path.sep + cfg_name + '.cfg.yml'
        fileoperations.make_eb_dir('saved_configs')
        fileoperations.write_to_eb_data_file(location, self.data)

        location = os.path.expanduser(os.getcwd() + os.path.sep +
                                      fileoperations.beanstalk_directory +
                                      location)

        result = saved_configs.resolve_config_location(cfg_name)
        self.assertEqual(result, location)

    def test_resolve_config_location_private_with_extension(self):
        cfg_name = 'myfile.cfg.yml'
        location = 'saved_configs' + os.path.sep + cfg_name
        fileoperations.make_eb_dir('saved_configs')
        fileoperations.write_to_eb_data_file(location, self.data)

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
        fileoperations.write_to_eb_data_file(location_public, self.data)
        fileoperations.write_to_eb_data_file(location_private, self.data)

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
        fileoperations.write_to_eb_data_file(location_public, self.data)
        fileoperations.write_to_eb_data_file(location_private, self.data)

        location_public = os.getcwd() + os.path.sep + \
            fileoperations.beanstalk_directory + location_public
        location_private = os.getcwd() + os.path.sep + \
            fileoperations.beanstalk_directory + location_private


        result = saved_configs.resolve_config_location(cfg_name)
        self.assertEqual(result, location_private)

    def test_resolve_config_location_relative_without_slash(self):
        cfg_name = 'myfile.cfg.yml'
        location = fileoperations.get_project_file_full_location(cfg_name)
        fileoperations.write_to_data_file(location, self.data)

        result = saved_configs.resolve_config_location(cfg_name)
        self.assertEqual(result, location)

    @mock.patch('ebcli.operations.saved_configs.upload_config_file')
    def test_update_config_resolve_normal(self, mock_upload):
        cfg_name = 'myfile.cfg.yml'
        location = 'saved_configs' + os.path.sep + cfg_name
        fileoperations.make_eb_dir('saved_configs')
        fileoperations.write_to_eb_data_file(location, self.data)

        location = os.getcwd() + os.path.sep + \
                   fileoperations.beanstalk_directory + location

        saved_configs.update_config('app', 'myfile')

        mock_upload.assert_called_with('app', 'myfile', location)

    @mock.patch('ebcli.operations.saved_configs.upload_config_file')
    def test_update_config_resolve_path(self, mock_upload):
        cfg_name = self.cfg_name
        location = fileoperations.get_project_file_full_location(cfg_name)
        fileoperations.write_to_data_file(location, self.data)

        saved_configs.update_config('app', './{0}'.format(self.cfg_name))

        mock_upload.assert_called_with('app', 'myfile', location)

    @mock.patch('ebcli.operations.saved_configs.fileoperations.get_filename_without_extension')
    @mock.patch('ebcli.operations.saved_configs.elasticbeanstalk.validate_template')
    def test_validate_config(self, mock_validate, mock_filename):
        mock_filename.return_value = self.cfg_name
        mock_validate.return_value = {'Messages': [{'Severity': 'error', 'Message': 'foo-error'},
                                                    {'Severity': 'warning', 'Message': 'foo-warn'}]}
        saved_configs.validate_config_file(self.app_name, self.cfg_name, self.platform)

        mock_filename.assert_called_with(self.cfg_name)
        mock_validate.assert_called_with(self.app_name, self.cfg_name)


