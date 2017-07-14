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
import yaml
import zipfile

from ebcli.core import fileoperations
from ebcli.objects.exceptions import NotInitializedError, ValidationError
from ebcli.objects.buildconfiguration import BuildConfiguration
from mock import patch


class TestFileOperations(unittest.TestCase):
    if sys.version_info.major > 2:
        config_parser_import = 'configparser.ConfigParser'
    else:
        config_parser_import = 'ConfigParser.ConfigParser'

    expected_file = 'foo.txt'
    expected_file_without_ext = 'foo'

    @classmethod
    def setUpClass(self):
        self.test_root = os.getcwd()

    def setUp(self):
        # set up test directory
        if not os.path.exists('testDir'):
            os.makedirs('testDir')
        os.chdir('testDir')

        # set up mock elastic beanstalk directory
        if not os.path.exists(fileoperations.beanstalk_directory):
            os.makedirs(fileoperations.beanstalk_directory)

        #set up mock home dir
        if not os.path.exists('home'):
            os.makedirs('home')

        # change directory to mock home
        fileoperations.aws_config_folder = 'home' + os.path.sep
        fileoperations.aws_config_location \
            = fileoperations.aws_config_folder + 'config'

    def tearDown(self):
        os.chdir(self.test_root)
        if os.path.exists('testDir'):
            if sys.platform.startswith('win'):
                os.system('rmdir /S /Q testDir')
            else:
                shutil.rmtree('testDir')

    def test_get_aws_home(self):
        # Just make sure no errors are thrown
        fileoperations.get_aws_home()

    def test_get_ssh_folder(self):
        # Just make sure no errors are thrown
        try:
            fileoperations.get_ssh_folder()
        except OSError as ex:
            # If access is denied assume we are running on a limited environment
            if ex.errno == 13:
                pass

    def test_get_application_name(self):
        # wrapper of get_config_setting
        pass

    def test_create_config_file_no_file(self):
        # make sure file doesn't exist
        if os.path.exists(fileoperations.local_config_file):
            os.remove(fileoperations.local_config_file)
        self.assertFalse(os.path.exists(fileoperations.local_config_file))

        app_name = 'ebcli-test'
        region = 'us-east-1'
        solution = 'my-solution-stack'
        fileoperations.create_config_file(app_name, region, solution)

        # Make sure file now exists
        self.assertTrue(os.path.exists(fileoperations.local_config_file))

        #grab value saved
        rslt = fileoperations.get_config_setting('global', 'application_name')
        self.assertEqual(app_name, rslt)

    def test_create_config_file_no_dir(self):
        # make sure directory doesn't exist
        if os.path.exists(fileoperations.beanstalk_directory):
            shutil.rmtree(fileoperations.beanstalk_directory)
        self.assertFalse(os.path.exists(fileoperations.beanstalk_directory))

        app_name = 'ebcli-test'
        region = 'us-east-1'
        solution = 'my-solution-stack'
        fileoperations.create_config_file(app_name, region, solution)

        # Make sure file and dir now exists
        self.assertTrue(os.path.exists(fileoperations.beanstalk_directory))
        self.assertTrue(os.path.exists(fileoperations.local_config_file))

        #grab value saved
        rslt = fileoperations.get_config_setting('global', 'application_name')
        self.assertEqual(app_name, rslt)

    def test_create_config_file_file_exists(self):
        # write to file without overriding anything besides global app name

        fileoperations.write_config_setting('global', 'randomKey', 'val')
        fileoperations.write_config_setting('test', 'application_name', 'app1')

        # call create
        app_name = 'ebcli-test'
        region = 'us-east-1'
        solution = 'my-solution-stack'
        fileoperations.create_config_file(app_name, region, solution)

        key = fileoperations.get_config_setting('global', 'randomKey')
        app = fileoperations.get_config_setting('global', 'application_name')
        test = fileoperations.get_config_setting('test', 'application_name')

        self.assertEqual(key, 'val')
        self.assertEqual(app, app_name)
        self.assertEqual(test, 'app1')

    def test_traverse_to_project_root_at_root(self):
        # make sure we are at root
        if not os.path.exists(fileoperations.beanstalk_directory):
            os.makedirs(fileoperations.beanstalk_directory)

        # save current directory
        cwd = os.getcwd()

        fileoperations._traverse_to_project_root()

        # get new working directory - make sure its the same as the original
        nwd = os.getcwd()
        self.assertEqual(cwd, nwd)

    def test_traverse_to_project_root_deep(self):
        # save current directory
        cwd = os.getcwd()

        # create and swap to deep subdirectory
        self._traverse_to_deeper_subdir()

        fileoperations._traverse_to_project_root()

        # get new working directory - make sure its the same as the original
        nwd = os.getcwd()
        self.assertEqual(cwd, nwd)

    @unittest.skip
    def test_traverse_to_project_root_no_root(self):
        # move up 2 directories first to make sure we are not in a project root
        cwd = os.getcwd()
        try:
            os.chdir(os.path.pardir)
            os.chdir(os.path.pardir)

            try:
                fileoperations._traverse_to_project_root()
                raise Exception('Should have thrown NotInitializedException')
            except fileoperations.NotInitializedError:
                pass  # expected
        finally:
            os.chdir(cwd)

    def test_write_config_setting_no_section(self):
        # create config file
        fileoperations.create_config_file('ebcli-test', 'us-east-1',
                                          'my-solution-stack')

        #make sure section does not exist
        dict = fileoperations._get_yaml_dict(fileoperations.local_config_file)
        self.assertFalse('mytestsection' in dict)

        # now do write
        fileoperations.write_config_setting('mytestsection',
                                            'testkey', 'value')

        # make sure section now exists
        dict = fileoperations._get_yaml_dict(fileoperations.local_config_file)
        self.assertTrue('mytestsection' in dict)

    def test_write_config_setting_no_option(self):
        # create config file
        fileoperations.create_config_file('ebcli-test', 'us-east-1',
                                          'my-solution-stack')

        #make sure section does exists, but option doesn't
        fileoperations.write_config_setting('mytestsection', 'notmykey', 'val')
        dict = fileoperations._get_yaml_dict(fileoperations.local_config_file)

        self.assertTrue('mytestsection' in dict)
        self.assertFalse('testkey' in dict['mytestsection'])

        # now do write
        fileoperations.write_config_setting('mytestsection',
                                            'testkey', 'value')

        # make sure section now exists
        dict = fileoperations._get_yaml_dict(fileoperations.local_config_file)
        self.assertTrue('mytestsection' in dict)
        self.assertTrue('testkey' in dict['mytestsection'])
        self.assertEqual(dict['mytestsection']['testkey'], 'value')

    def test_write_config_setting_override(self):
        # create config file
        fileoperations.create_config_file('ebcli-test', 'us-east-1',
                                          'my-solution-stack')

        #make sure app name exists
        dict = fileoperations._get_yaml_dict(fileoperations.local_config_file)
        self.assertTrue('global' in dict)
        self.assertTrue('application_name' in dict['global'])
        self.assertTrue('application_name' in dict['global'])
        self.assertEqual(dict['global']['application_name'], 'ebcli-test')

        # now override
        fileoperations.write_config_setting('global',
                                            'application_name', 'new_name')

        dict = fileoperations._get_yaml_dict(fileoperations.local_config_file)
        self.assertEqual(dict['global']['application_name'], 'new_name')


    def test_write_config_setting_no_file(self):
        # make sure file doesn't exist
        if os.path.exists(fileoperations.local_config_file):
            os.remove(fileoperations.local_config_file)

        self.assertFalse(os.path.exists(fileoperations.local_config_file))

        # now do write
        fileoperations.write_config_setting('mytestsection',
                                            'testkey', 'value')

        # make sure section and file now exists
        self.assertTrue(os.path.exists(fileoperations.local_config_file))
        dict = fileoperations._get_yaml_dict(fileoperations.local_config_file)
        self.assertTrue('mytestsection' in dict)

    def test_write_config_setting_standard(self):
        fileoperations.write_config_setting('global', 'mysetting', 'value')
        result = fileoperations.get_config_setting('global', 'mysetting')
        self.assertEqual(result, 'value')

    def test_get_config_setting_no_global(self):
        # make sure global file does not exist
        if os.path.exists(fileoperations.global_config_file):
            os.remove(fileoperations.global_config_file)
        self.assertFalse(os.path.exists(fileoperations.global_config_file))

        # Now create local
        fileoperations.create_config_file('ebcli-test', 'us-east-1',
                                          'my-solution-stack')

        #get app name
        result = fileoperations.get_config_setting('global',
                                                   'application_name')

        self.assertEqual(result, 'ebcli-test')

    def test_get_config_setting_no_local(self):
        # create global file
        config = {'global': {'application_name': 'myApp'}}
        with open(fileoperations.global_config_file, 'w') as f:
            f.write(yaml.dump(config, default_flow_style=False))

        self.assertTrue(os.path.exists(fileoperations.global_config_file))

        # make sure local file does not exist
        if os.path.exists(fileoperations.local_config_file):
            os.remove(fileoperations.local_config_file)
        self.assertFalse(os.path.exists(fileoperations.local_config_file))

        #get app name
        result = fileoperations.get_config_setting('global',
                                                   'application_name')

        self.assertEqual(result, 'myApp')

    def test_get_config_setting_no_files(self):
        # make sure local file doesn't exist
        if os.path.exists(fileoperations.local_config_file):
            os.remove(fileoperations.local_config_file)
        self.assertFalse(os.path.exists(fileoperations.local_config_file))

        # make sure global file does not exist
        if os.path.exists(fileoperations.global_config_file):
            os.remove(fileoperations.global_config_file)
        self.assertFalse(os.path.exists(fileoperations.global_config_file))

        # now get setting
        result = fileoperations.get_config_setting('global',
                                                   'application_name')

        self.assertEquals(result, None)

    def test_get_config_setting_merge(self):
        # create global file
        config = {'global':{'application_name':'myApp'}}
        with open(fileoperations.global_config_file, 'w') as f:
            f.write(yaml.dump(config, default_flow_style=False))

        self.assertTrue(os.path.exists(fileoperations.global_config_file))

        # Now create local
        fileoperations.create_config_file('ebcli-test', 'us-east-1',
                                          'my-solution-stack')

        #get app name
        result = fileoperations.get_config_setting('global',
                                                   'application_name')

        # should return result from local NOT global
        self.assertEqual(result, 'ebcli-test')

    def test_get_project_root_at_root(self):
        cwd = os.getcwd()
        self.assertEquals(cwd, fileoperations.get_project_root())
        self.assertEquals(cwd, os.getcwd())

    def test_traverse_to_project_root_deep2(self):
        cwd = os.getcwd()
        self._traverse_to_deeper_subdir()
        self.assertEquals(cwd, fileoperations.get_project_root())

    @unittest.skip
    def test_traverse_to_project_no_root(self):
        os.chdir(os.path.pardir)
        os.chdir(os.path.pardir)

        self.assertRaises(NotInitializedError, fileoperations.get_project_root)

    @patch('ebcli.core.fileoperations.json.loads')
    @patch('ebcli.core.fileoperations.read_from_text_file')
    def test_get_json_dict(self, read_from_data_file, loads):
        read_from_data_file.return_value = '{}'
        loads.return_value = {}
        mock_path = '/a/b/c/file.json'

        self.assertEquals(fileoperations.get_json_dict(mock_path), {})
        read_from_data_file.assert_called_once_with(mock_path)
        loads.assert_called_once_with('{}')

    @patch('ebcli.core.fileoperations.get_project_root')
    def test_project_file_path(self, get_project_root):
        get_project_root.side_effect = ['/']
        expected_file_path = os.path.join('/', 'foo')
        self.assertEquals(fileoperations.project_file_path('foo'),
                          expected_file_path)

    @patch('ebcli.core.fileoperations.file_exists')
    @patch('ebcli.core.fileoperations.project_file_path')
    def test_project_file_exists(self, project_file_path,
                                 file_exists):
        project_file_path.side_effect = ['/foo']
        file_exists.return_value = True

        self.assertTrue(fileoperations.project_file_exists('foo'))
        project_file_path.assert_called_once_with('foo')
        file_exists.assert_called_once_with('/foo')

    def _traverse_to_deeper_subdir(self):
        dir = 'fol1' + os.path.sep + 'fol2' + os.path.sep + 'fol3'
        os.makedirs(dir)
        os.chdir(dir)

    @patch('ebcli.core.fileoperations.codecs')
    @patch('ebcli.core.fileoperations.load')
    def test_get_build_spec_info(self, mock_yaml_load, mock_codecs):
        # Setup mocks
        image = 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.3'
        compute_type = 'BUILD_GENERAL1_SMALL'
        service_role = 'eb-test'
        timeout = 60

        mock_yaml_load.return_value = {fileoperations.buildspec_config_header:
                                       {'ComputeType': compute_type,
                                        'CodeBuildServiceRole': service_role,
                                        'Image': image,
                                        'Timeout': timeout}}

        expected_build_config = BuildConfiguration(image=image, compute_type=compute_type,
                                                   service_role=service_role, timeout=timeout)
        actual_build_config = fileoperations.get_build_configuration()
        self.assertEqual(expected_build_config.__str__(), actual_build_config.__str__(),
                         "Expected '{0}' but got: {1}".format(expected_build_config.__str__(), actual_build_config.__str__()))

    @patch('ebcli.core.fileoperations.codecs')
    @patch('ebcli.core.fileoperations.load')
    def test_get_build_spec_info_with_bad_header(self, mock_yaml_load, mock_codecs):
        # Setup mocks
        image = 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.3'
        compute_type = 'BUILD_GENERAL1_SMALL'
        service_role = 'eb-test'
        timeout = 60

        mock_yaml_load.return_value = {'BadHeader':
                                           {'ComputeType': compute_type,
                                            'CodeBuildServiceRole': service_role,
                                            'Image': image,
                                            'Timeout': timeout}}

        actual_build_config = fileoperations.get_build_configuration()
        self.assertIsNone(actual_build_config)

    @patch('ebcli.core.fileoperations.codecs')
    @patch('ebcli.core.fileoperations.load')
    def test_get_build_spec_info_with_no_values(self, mock_yaml_load, mock_codecs):
        # Setup mocks
        mock_yaml_load.return_value = {fileoperations.buildspec_config_header: None}
        actual_build_config = fileoperations.get_build_configuration()
        self.assertIsNone(actual_build_config.compute_type)
        self.assertIsNone(actual_build_config.image)
        self.assertIsNone(actual_build_config.service_role)
        self.assertIsNone(actual_build_config.timeout)

    def test_build_spec_file_exists_yaml(self):
        # Create buildspec file quickly
        file = 'buildspec.yaml'
        open(file, 'a').close()
        self.assertFalse(fileoperations.build_spec_exists(),
                        "Expected to find build spec file with filename: {0}".format(file))
        os.remove(file)

    def test_build_spec_file_exists_yml(self):
        # Create buildspec file quickly
        file = 'buildspec.yml'
        open(file, 'a').close()
        self.assertTrue(fileoperations.build_spec_exists(),
                        "Expected to find build spec file with filename: {0}".format(file))
        os.remove(file)

    def test_get_filename_without_extension_with_path(self):
        filepath = '/tmp/dir/test/{0}'.format(self.expected_file)

        actual_file = fileoperations.get_filename_without_extension(filepath)
        self.assertEqual(self.expected_file_without_ext, actual_file, "Expected {0} but got: {1}"
                         .format(self.expected_file_without_ext, actual_file))

    def test_get_filename_without_extension_with_file(self):
        actual_file = fileoperations.get_filename_without_extension(self.expected_file)
        self.assertEqual(self.expected_file_without_ext, actual_file, "Expected {0} but got: {1}"
                         .format(self.expected_file_without_ext, actual_file))

    def test_zip_append_archive(self):
        os.chdir(self.test_root)
        os.chdir('testDir')

        open('source_file.txt', 'w+').close()
        open('target_file.txt', 'w+').close()
        os.system('python -m zipfile -c source_file.zip source_file.txt')
        os.system('python -m zipfile -c target_file.zip target_file.txt')

        fileoperations.zip_append_archive('target_file.zip', 'source_file.zip')

        target_file_zip = zipfile.ZipFile('target_file.zip', 'r')
        self.assertEquals(['source_file.txt', 'target_file.txt'], sorted(target_file_zip.namelist()))
