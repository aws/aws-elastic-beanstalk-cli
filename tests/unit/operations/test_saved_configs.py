# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import sys

import mock
import unittest

from ebcli.core import fileoperations
from ebcli.operations import saved_configs


class TestResolveConfigLocations(unittest.TestCase):
    module_name = 'test2'
    app_name = 'app_name'
    platform = 'python'
    cfg_name = 'myfile.cfg.yml'

    def setUp(self):
        if not os.path.exists('testDir'):
            os.makedirs('testDir/.elasticbeanstalk/')
        os.chdir('testDir')

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

    @mock.patch('ebcli.operations.saved_configs.download_config_from_s3')
    @mock.patch('ebcli.operations.saved_configs.elasticbeanstalk.create_configuration_template')
    def test_create_config(
            self,
            create_configuration_template_mock,
            download_config_from_s3_mock
    ):
        saved_configs.create_config(
            'my-application',
            'environment-1',
            'config-template'
        )
        download_config_from_s3_mock.assert_called_once_with('my-application', 'config-template')
        create_configuration_template_mock.assert_called_once_with(
            'my-application',
            'environment-1',
            'config-template',
            'Configuration created from the EB CLI using "eb config save".'
        )

    @mock.patch('ebcli.operations.saved_configs.commonops.update_environment')
    @mock.patch('ebcli.operations.saved_configs.fileoperations.env_yaml_exists')
    def test_update_environment_with_config_file(
            self,
            env_yaml_exists_mock,
            update_environment_mock
    ):
        env_yaml_exists_mock.return_value = True
        saved_configs.update_environment_with_config_file(
            'environment-1',
            'cfg-name',
            False
        )
        update_environment_mock.assert_called_once_with(
            'environment-1',
            None,
            False,
            template='cfg-name',
            timeout=None
        )

    @mock.patch('ebcli.operations.saved_configs.commonops.update_environment')
    @mock.patch('ebcli.operations.saved_configs.fileoperations.env_yaml_exists')
    def test_update_environment_with_config_file(
            self,
            env_yaml_exists_mock,
            update_environment_mock
    ):
        env_yaml_exists_mock.return_value = True
        saved_configs.update_environment_with_config_data(
            'environment-1',
            'cfg-name',
            False
        )
        update_environment_mock.assert_called_once_with(
            'environment-1',
            None,
            False,
            template_body='cfg-name',
            timeout=None
        )

    @mock.patch('ebcli.operations.saved_configs.elasticbeanstalk.get_storage_location')
    @mock.patch('ebcli.operations.saved_configs.s3.get_object')
    @mock.patch('ebcli.operations.saved_configs.write_to_local_config')
    @mock.patch('ebcli.operations.saved_configs.fileoperations.set_user_only_permissions')
    @mock.patch('ebcli.operations.saved_configs._get_s3_keyname_for_template')
    def test_download_config_from_s3(
            self,
            get_s3_keyname_for_template_mock,
            set_user_only_permissions_mock,
            write_to_local_config_mock,
            get_object_mock,
            get_storage_location_mock
    ):
        get_s3_keyname_for_template_mock.return_value = 'template'
        write_to_local_config_mock.return_value = 'file_path'
        get_storage_location_mock.return_value = 'bucket'
        get_object_mock.return_value = 'body'

        saved_configs.download_config_from_s3('my-application', 'cfg-name')

        get_storage_location_mock.assert_called_once_with()
        get_object_mock.assert_called_once_with('bucket', 'template')
        write_to_local_config_mock.assert_called_once_with('cfg-name', 'body')
        set_user_only_permissions_mock.assert_called_once_with('file_path')

    @mock.patch('ebcli.operations.saved_configs.elasticbeanstalk.delete_configuration_template')
    @mock.patch('ebcli.operations.saved_configs.fileoperations.delete_file')
    @mock.patch('ebcli.operations.saved_configs.resolve_config_location')
    def test_delete_config(
            self,
            resolve_config_location_mock,
            delete_file_mock,
            delete_configuration_template_mock
    ):
        resolve_config_location_mock.return_value = 'location'

        saved_configs.delete_config('my-application', 'cfg-name')

        delete_configuration_template_mock.assert_called_once_with('my-application', 'cfg-name')
        delete_file_mock.assert_called_once_with('location')

    @mock.patch('ebcli.operations.saved_configs.upload_config_file')
    @mock.patch('ebcli.operations.saved_configs.resolve_config_location')
    @mock.patch('ebcli.operations.saved_configs.fileoperations.get_filename_without_extension')
    def test_resolve_config_name(
            self,
            get_filename_without_extension_mock,
            resolve_config_location_mock,
            upload_config_file_mock
    ):
        resolve_config_location_mock.return_value = 'config_location'
        get_filename_without_extension_mock.return_value = 'file_name'

        saved_configs.resolve_config_name('my-application', 'cfg-name')

        upload_config_file_mock.assert_called_once_with('my-application', 'file_name', 'config_location')

    @mock.patch('ebcli.operations.saved_configs.fileoperations.make_eb_dir')
    @mock.patch('ebcli.operations.saved_configs.fileoperations.write_to_eb_data_file')
    @mock.patch('ebcli.operations.saved_configs.fileoperations.get_eb_file_full_location')
    def test_write_to_local_config(
            self,
            get_eb_file_full_location_mock,
            write_to_eb_data_file_mock,
            make_eb_dir_mock
    ):
        saved_configs.write_to_local_config('cfg-name', 'data')

        make_eb_dir_mock.assert_called_once_with('saved_configs{}'.format(os.path.sep))
        write_to_eb_data_file_mock.assert_called_once_with('saved_configs{}cfg-name.cfg.yml'.format(os.path.sep), 'data')
        get_eb_file_full_location_mock.assert_called_once_with('saved_configs{}cfg-name.cfg.yml'.format(os.path.sep))
