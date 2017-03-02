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
from ebcli.objects.exceptions import NotInitializedError, AlreadyExistsError
from ebcli.objects.buildconfiguration import BuildConfiguration
from mock import patch, Mock


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

    @patch('os.path.isdir', return_value=True)
    @patch('ebcli.lib.aws.get_profile', return_value="default")
    def test_get_credentials_with_no_config(self, aws, isdir):
        # Setup Mocks
        with patch(self.config_parser_import) as MockConfigParserClass:
            instance = MockConfigParserClass.return_value
            instance.sections.return_value = []

            # Execute the method
            credentials = fileoperations.read_credentials_from_aws_dir()
            self.assertEqual((None, None), credentials, "Expected credentials to be (None, None) but were: {0}".format(credentials))

    @patch('ebcli.core.fileoperations._get_option')
    @patch('os.path.isdir', return_value=True)
    @patch('ebcli.lib.aws.get_profile', return_value="default")
    def test_get_credentials_with_no_config_but_creds_file(self, aws, isdir, get_option):
        # Setup Mocks
        with patch(self.config_parser_import) as MockConfigParserClass:
            instance = MockConfigParserClass.return_value
            instance.sections.return_value = ["default"]

            credentials_expected = ('access_key', 'secret_key')
            get_option.side_effect = credentials_expected

            # Execute the method
            credentials = fileoperations.read_credentials_from_aws_dir()
            self.assertEqual(credentials, credentials_expected,
                             "Expected credentials to be {0} but were: {1}".format(credentials_expected, credentials))


    @patch('ebcli.core.fileoperations._get_option')
    @patch('os.path.isdir', return_value=True)
    def test_get_credentials_with_config(self, isdir, get_option):
        # Setup Mocks
        ebcli_section = 'profile eb-cli'
        with patch(self.config_parser_import) as MockConfigParserClass:
            instance = MockConfigParserClass.return_value
            instance.sections.return_value = [ebcli_section]

            credentials_expected = ('access_key', 'secret_key')
            get_option.side_effect = credentials_expected

            # Execute the method
            credentials = fileoperations.read_credentials_from_aws_dir()
            self.assertEqual(credentials, credentials_expected,
                             "Expected credentials to be {0} but were: {1}".format(credentials_expected, credentials))

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

    @patch('ebcli.core.fileoperations.zip_lambda_dirs')
    @patch('ebcli.core.fileoperations.zip_up_folder')
    def test_zip_project_with_lambda(self, mock_zip_up_folder, mock_zip_lambda_dirs):
        # Setup mocks
        location = 'such/location'
        lambda_dir = ['_awseblambd/func1']
        mock_zip_lambda_dirs.return_value = lambda_dir

        fileoperations.zip_up_project(location)

        mock_zip_up_folder.assert_called()
        args, kwargs = mock_zip_up_folder.call_args
        self.assertEqual(args[0], './')
        self.assertEqual(args[1], location)
        self.assertItemsEqual(lambda_dir + ['.gitignore', '.elasticbeanstalk'], kwargs['ignore_list'])

    @patch('ebcli.core.fileoperations.zip_lambda_dirs')
    @patch('ebcli.core.fileoperations.zip_up_folder')
    def test_zip_project_without_lambda(self, mock_zip_up_folder, mock_zip_lambda_dirs):
        # Setup mocks
        location = 'such/location'
        lambda_dir = []
        mock_zip_lambda_dirs.return_value = lambda_dir

        fileoperations.zip_up_project(location)

        mock_zip_up_folder.assert_called()
        args, kwargs = mock_zip_up_folder.call_args
        self.assertEqual(args[0], './')
        self.assertEqual(args[1], location)
        self.assertItemsEqual(['.gitignore', '.elasticbeanstalk'], kwargs['ignore_list'])

    def test_list_child_dir(self):
        # make sure local test dir does not exist
        if os.path.exists(fileoperations.lambda_base_directory):
            os.remove(fileoperations.lambda_base_directory)

        pwd = os.getcwd()
        try:
            os.mkdir(fileoperations.lambda_base_directory)
            os.chdir(fileoperations.lambda_base_directory)
            cwd = os.getcwd()

            # when directory is empty, should get empty list of chil_dir
            self.assertItemsEqual(fileoperations.list_child_dir(cwd), [])

            # Create several directories and a file
            child_file = 'test.elc'
            child_dirs = ['white space', 'very-lambda', 'yeah~']
            open(child_file, 'w').close()
            for child in child_dirs:
                os.mkdir(child)

            # only directories should be returned
            expected = [os.path.join(cwd, child) for child in child_dirs]
            self.assertItemsEqual(fileoperations.list_child_dir(cwd), expected)
        finally:
            if os.path.exists(fileoperations.lambda_base_directory):
                os.remove(fileoperations.lambda_base_directory)
            os.chdir(pwd)

    @patch('ebcli.lib.iam_role.get_default_lambda_role')
    def test_zip_lambda_dirs_success(self, mock_get_default_lambda_role):
        # make sure local test dir does not exist
        if os.path.exists(fileoperations.lambda_base_directory):
            os.remove(fileoperations.lambda_base_directory)

        pwd = os.getcwd()
        try:
            os.mkdir(fileoperations.lambda_base_directory)
            os.chdir(fileoperations.lambda_base_directory)

            # Create several directories and a file
            child_file = 'test.elc'
            child_dirs = ['white space', 'very-lambda', 'yeah~']
            open(child_file, 'w').close()
            for child in child_dirs:
                os.mkdir(child)

            expected = [os.path.join(fileoperations.lambda_base_directory, child) for child in child_dirs]
            self.assertItemsEqual(fileoperations.zip_lambda_dirs(), expected)
            mock_get_default_lambda_role.assert_called()
        finally:
            if os.path.exists(fileoperations.lambda_base_directory):
                os.remove(fileoperations.lambda_base_directory)
            os.chdir(pwd)

    @patch('ebcli.lib.iam_role.get_default_lambda_role')
    def test_zip_lambda_dirs_zip_already_exists(self, mock_get_default_lambda_role):
        # make sure local test dir does not exist
        if os.path.exists(fileoperations.lambda_base_directory):
            os.remove(fileoperations.lambda_base_directory)

        pwd = os.getcwd()
        try:
            os.mkdir(fileoperations.lambda_base_directory)
            os.chdir(fileoperations.lambda_base_directory)

            # Create several directories and a file
            child_file = 'very-lambda.zip'
            child_dirs = ['white space', 'very-lambda', 'yeah~']
            open(child_file, 'w').close()
            for child in child_dirs:
                os.mkdir(child)

            # Should fail if zip and directory both exists as lambda functions
            self.assertRaises(AlreadyExistsError, fileoperations.zip_lambda_dirs)
            mock_get_default_lambda_role.assert_called()
        finally:
            if os.path.exists(fileoperations.lambda_base_directory):
                os.remove(fileoperations.lambda_base_directory)
            os.chdir(pwd)

    @patch('ebcli.lib.iam_role.get_default_lambda_role')
    def test_zip_lambda_dirs_with_lambda_subdir_flag(self, mock_get_default_lambda_role):
        # make sure local test dir does not exist
        if os.path.exists(fileoperations.lambda_base_directory):
            os.remove(fileoperations.lambda_base_directory)

        pwd = os.getcwd()
        try:
            os.mkdir(fileoperations.lambda_base_directory)
            os.chdir(fileoperations.lambda_base_directory)

            # Create several directories and a file
            lambda_subdir = 'very-lambda'
            os.mkdir(lambda_subdir)
            grandchild_dir = os.path.join(lambda_subdir, 'fun1')
            child_dirs = ['white space', 'yeah~', grandchild_dir]
            for child in child_dirs:
                os.mkdir(child)

            # lambda_subdir should not be in the zip_lambda_dir; instead, its child should be zipped
            expected = [os.path.join(fileoperations.lambda_base_directory, child) for child in child_dirs]
            self.assertItemsEqual(fileoperations.zip_lambda_dirs(lambda_subdir=[lambda_subdir]), expected)
            mock_get_default_lambda_role.assert_called()
        finally:
            if os.path.exists(fileoperations.lambda_base_directory):
                os.remove(fileoperations.lambda_base_directory)
            os.chdir(pwd)

    @patch('ebcli.lib.iam_role.get_default_lambda_role')
    def test_zip_lambda_dirs_not_exists(self, mock_get_default_lambda_role):
        # make sure local test dir does not exist
        if os.path.exists(fileoperations.lambda_base_directory):
            os.remove(fileoperations.lambda_base_directory)

        pwd = os.getcwd()
        try:
            # Should just be empty
            self.assertItemsEqual(fileoperations.zip_lambda_dirs(), [])
            mock_get_default_lambda_role.assert_not_called()
        finally:
            os.chdir(pwd)

    @patch('ebcli.core.fileoperations.zipfile')
    def test_dir_exist_in_zip_exists_with_slash(self, mock_zipfile_lib):
        # setup mock zipfile
        mock_zip = Mock()
        mock_zipfile_lib.ZipFile.return_value = mock_zip
        mock_zip.namelist.return_value = ['wow/', 'such-dir/']

        self.assertTrue(fileoperations.dir_exist_in_zip('', 'such-dir/'))


    @patch('ebcli.core.fileoperations.zipfile')
    def test_dir_exist_in_zip_exists_without_slash(self, mock_zipfile_lib):
        # setup mock zipfile
        mock_zip = Mock()
        mock_zipfile_lib.ZipFile.return_value = mock_zip
        mock_zip.namelist.return_value = ['wow/', 'such-dir/']

        self.assertTrue(fileoperations.dir_exist_in_zip('', 'such-dir'))


    @patch('ebcli.core.fileoperations.zipfile')
    def test_dir_exist_in_zip_does_not_exist(self, mock_zipfile_lib):
        # setup mock zipfile
        mock_zip = Mock()
        mock_zipfile_lib.ZipFile.return_value = mock_zip
        mock_zip.namelist.return_value = ['wow/', 'such-dir/']

        self.assertFalse(fileoperations.dir_exist_in_zip('', 'such-directory'))
