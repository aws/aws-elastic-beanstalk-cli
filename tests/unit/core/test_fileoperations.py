# -*- coding: UTF-8 -*-

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
import stat
import sys
import yaml
import zipfile

import pytest
import unittest
from mock import patch

from ebcli.core import fileoperations
from ebcli.objects.buildconfiguration import BuildConfiguration
from ebcli.objects.exceptions import NotInitializedError


class TestFileOperations(unittest.TestCase):
    def create_config_file(self):
        app_name = 'ebcli-test'
        region = 'us-east-1'
        solution = 'my-solution-stack'
        fileoperations.create_config_file(app_name, region, solution)

    def setUp(self):
        self.test_root = os.getcwd()
        if not os.path.exists('testDir'):
            os.makedirs('testDir')
        os.chdir('testDir')

        if not os.path.exists(fileoperations.beanstalk_directory):
            os.makedirs(fileoperations.beanstalk_directory)

        if not os.path.exists('home'):
            os.makedirs('home')

        fileoperations.aws_config_folder = os.path.join('home', '.aws')
        fileoperations.aws_config_location = os.path.join('home', '.aws', 'config')

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

    def test_project_root__traverse_at_root(self):
        # make sure we are at root
        if not os.path.exists(fileoperations.beanstalk_directory):
            os.makedirs(fileoperations.beanstalk_directory)

        # save current directory
        cwd = os.getcwd()

        fileoperations.ProjectRoot.traverse()

        # get new working directory - make sure its the same as the original
        nwd = os.getcwd()
        self.assertEqual(cwd, nwd)

    def test_project_root__traverse_deep(self):
        # save current directory
        cwd = os.getcwd()

        # create and swap to deep subdirectory
        self._traverse_to_deeper_subdir()

        fileoperations.ProjectRoot.traverse()

        # get new working directory - make sure its the same as the original
        nwd = os.getcwd()
        self.assertEqual(cwd, nwd)

    @unittest.skip
    def test_project_root__traverse_no_root(self):
        # move up 2 directories first to make sure we are not in a project root
        cwd = os.getcwd()
        try:
            os.chdir(os.path.pardir)
            os.chdir(os.path.pardir)

            try:
                fileoperations.ProjectRoot.traverse()
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

        self.assertEqual(result, None)

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
        self.assertEqual(cwd, fileoperations.get_project_root())
        self.assertEqual(cwd, os.getcwd())

    def test_project_root__traverse_deep2(self):
        cwd = os.getcwd()
        self._traverse_to_deeper_subdir()
        self.assertEqual(cwd, fileoperations.get_project_root())

    def test_traverse_to_project_no_root(self):
        os.chdir(os.path.pardir)
        os.chdir(os.path.pardir)

        self.assertRaises(NotInitializedError, fileoperations.get_project_root)

    def test_inside_ebcli_project(self):
        self.assertTrue(fileoperations.inside_ebcli_project())

    def test_inside_ebcli_project__false(self):
        shutil.rmtree(fileoperations.beanstalk_directory)

        self.assertFalse(fileoperations.inside_ebcli_project())

    @patch('ebcli.core.fileoperations.json.loads')
    @patch('ebcli.core.fileoperations.read_from_text_file')
    def test_get_json_dict(self, read_from_data_file, loads):
        read_from_data_file.return_value = '{}'
        loads.return_value = {}
        mock_path = 'a{0}b{0}c{0}file.json'.format(os.path.sep)

        self.assertEqual(fileoperations.get_json_dict(mock_path), {})
        read_from_data_file.assert_called_once_with(mock_path)
        loads.assert_called_once_with('{}')

    @patch('ebcli.core.fileoperations.get_project_root')
    def test_project_file_path(self, get_project_root):
        get_project_root.side_effect = [os.path.sep]
        expected_file_path = '{}foo'.format(os.path.sep)
        self.assertEqual(fileoperations.project_file_path('foo'),
                          expected_file_path)

    @patch('ebcli.core.fileoperations.file_exists')
    @patch('ebcli.core.fileoperations.project_file_path')
    def test_project_file_exists(self, project_file_path,
                                 file_exists):
        project_file_path.side_effect = ['{}foo'.format(os.path.sep)]
        file_exists.return_value = True

        self.assertTrue(fileoperations.project_file_exists('foo'))
        project_file_path.assert_called_once_with('foo')
        file_exists.assert_called_once_with('{}foo'.format(os.path.sep))

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
        filepath = '{1}tmp{1}dir{1}test{1}{0}'.format('foo.txt', os.path.sep)

        actual_file = fileoperations.get_filename_without_extension(filepath)
        self.assertEqual('foo', actual_file, "Expected {0} but got: {1}"
                         .format('foo', actual_file))

    def test_get_filename_without_extension_with_file(self):
        actual_file = fileoperations.get_filename_without_extension('foo.txt')
        self.assertEqual('foo', actual_file, "Expected {0} but got: {1}"
                         .format('foo', actual_file))

    def test_zip_append_archive(self):
        os.chdir(self.test_root)
        os.chdir('testDir')

        open('source_file.txt', 'w+').close()
        open('target_file.txt', 'w+').close()
        os.system('python -m zipfile -c source_file.zip source_file.txt')
        os.system('python -m zipfile -c target_file.zip target_file.txt')

        fileoperations.zip_append_archive('target_file.zip', 'source_file.zip')

        target_file_zip = zipfile.ZipFile('target_file.zip', 'r', allowZip64=True)
        self.assertEqual(['source_file.txt', 'target_file.txt'], sorted(target_file_zip.namelist()))

    @patch('ebcli.core.fileoperations.get_editor')
    @patch('ebcli.core.fileoperations.os.system')
    def test_open_file_for_editing(self, system_mock, get_editor_mock):
        file_to_open = 'config.yml'
        get_editor_mock.return_value = 'vim'
        system_mock.side_effect = None

        fileoperations.open_file_for_editing(file_to_open)

    @patch('ebcli.core.fileoperations.get_editor')
    @patch('os.system')
    @patch('ebcli.core.fileoperations.io.log_error')
    def test_open_file_for_editing__editor_could_not_open_file(
            self,
            log_error_mock,
            system_mock,
            get_editor_mock
    ):
        file_to_open = 'config.yml'
        get_editor_mock.return_value = 'vim'
        system_mock.side_effect = OSError

        fileoperations.open_file_for_editing(file_to_open)

        log_error_mock.assert_called_with(
            'EB CLI cannot open the file using the editor vim.'
        )

    def test_get_platform_from_env_yaml(self):
        with open('env.yaml', 'w') as yaml_file:
            yaml_file.write(
                'SolutionStack: 64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)'
            )

        self.assertEqual(
            '64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)',
            fileoperations.get_platform_from_env_yaml()
        )

    def test_env_yaml_exists(self):
        self.assertFalse(fileoperations.env_yaml_exists())

        os.mkdir('src')
        open(os.path.join('src', 'env.yaml'), 'w').close()
        self.assertFalse(fileoperations.env_yaml_exists())

        open(os.path.join('env.yaml'), 'w').close()
        self.assertTrue(fileoperations.env_yaml_exists())

    def test_get_filename_without_extension(self):
        self.assertEqual('', fileoperations.get_filename_without_extension(''))
        self.assertEqual('file', fileoperations.get_filename_without_extension('file.zip'))
        self.assertEqual('file', fileoperations.get_filename_without_extension('src/file.zip'))
        self.assertEqual('file', fileoperations.get_filename_without_extension('src/file.zip.app'))

    def test_get_eb_file_full_location(self):
        self.assertEqual(
            os.path.join(os.path.abspath('.'), '.elasticbeanstalk'),
            fileoperations.get_eb_file_full_location('')
        )
        self.assertEqual(
            os.path.join(os.path.abspath('.'), '.elasticbeanstalk', 'app'),
            fileoperations.get_eb_file_full_location('app')
        )

    def test_get_ebignore_location(self):
        self.assertEqual(
            os.path.join(os.path.abspath('.'), '.ebignore'),
            fileoperations.get_ebignore_location()
        )

    def test_readlines_from_text_file(self):
        fileoperations.write_to_text_file(
            """aaa
bbb
ccc""",
            location='file'
        )

        self.assertEqual(
            ['aaa\n', 'bbb\n', 'ccc'],
            fileoperations.readlines_from_text_file('file')
        )

        fileoperations.append_to_text_file(
            location='file',
            data="""dddd"""
        )

        self.assertEqual(
            'aaa{linesep}bbb{linesep}cccdddd'.format(linesep=os.linesep).encode('utf-8'),
            fileoperations.read_from_data_file('file')
        )

    def test_write_json_dict(self):
        fileoperations.write_json_dict('{"EnvironmentName": "my-environment"}', 'file')

        self.assertEqual(
            '{"EnvironmentName": "my-environment"}',
            fileoperations.get_json_dict('file')
        )

    def test_get_application_from_file__app_yml_file_does_not_exist(self):
        self.assertIsNone(fileoperations.get_application_from_file('my-application'))

    @patch('ebcli.core.fileoperations.codecs.open')
    def test_get_application_from_file__yaml_parse_errors(self, codecs_mock):
        open('.elasticbeanstalk/my-application.app.yml', 'w').close()

        codecs_mock.side_effect = fileoperations.ScannerError
        with self.assertRaises(fileoperations.InvalidSyntaxError):
            fileoperations.get_application_from_file('my-application')

        codecs_mock.side_effect = fileoperations.ParserError
        with self.assertRaises(fileoperations.InvalidSyntaxError):
            fileoperations.get_application_from_file('my-application')

    def test_get_application_from_file__gets_app_name(self):
        with open('.elasticbeanstalk/my-application.app.yml', 'w') as file:
            file.write('{"EnvironmentName": "my-environment"}')

        self.assertEqual(
            {
                'EnvironmentName': 'my-environment'
            },
            fileoperations.get_application_from_file('my-application')
        )

    def test_get_environment_from_file__env_yml_file_does_not_exist(self):
        self.assertIsNone(fileoperations.get_environment_from_file('my-application'))

    @patch('ebcli.core.fileoperations.codecs.open')
    def test_get_environment_from_file__yaml_parse_errors(self, codecs_mock):
        open('.elasticbeanstalk/my-environment.env.yml', 'w').close()

        codecs_mock.side_effect = fileoperations.ScannerError
        with self.assertRaises(fileoperations.InvalidSyntaxError):
            fileoperations.get_environment_from_file('my-environment')

        codecs_mock.side_effect = fileoperations.ParserError
        with self.assertRaises(fileoperations.InvalidSyntaxError):
            fileoperations.get_environment_from_file('my-environment')

    def test_get_environment_from_file__gets_environment(self):
        with open('.elasticbeanstalk/my-environment.env.yml', 'w') as file:
            file.write('{"EnvironmentName": "my-environment"}')

        self.assertEqual(
            {
                'EnvironmentName': 'my-environment'
            },
            fileoperations.get_environment_from_file('my-environment')
        )

    def test_save_env_file(self):
        env = {
            'EnvironmentName': 'my-environment∂'
        }

        fileoperations.save_env_file(env)

        self.assertEqual(
            'EnvironmentName: "my-environment\\u2202"',
            open(os.path.join('.elasticbeanstalk', 'my-environment∂.env.yml')).read().strip()
        )

    def test_save_app_file(self):
        env = {
            'ApplicationName': 'my-application∂'
        }

        fileoperations.save_app_file(env)

        self.assertEqual(
            'ApplicationName: "my-application\\u2202"',
            open(os.path.join('.elasticbeanstalk', 'my-application∂.app.yml')).read().strip()
        )

    def test_get_editor__set_as_global(self):
        os.environ['EDITOR'] = ''
        fileoperations.write_config_setting('global', 'editor', 'vim')

        self.assertEqual(
            'vim',
            fileoperations.get_editor()
        )

    def test_get_editor__set_as_environment_variable(self):
        os.environ['EDITOR'] = 'vim'
        fileoperations.write_config_setting('global', 'editor', None)

        self.assertEqual(
            'vim',
            fileoperations.get_editor()
        )
        os.environ['EDITOR'] = ''

    @pytest.mark.skipif(not sys.platform.startswith('win'), reason='Behaviour is exclusive to Windows')
    def test_get_editor__cant_determine_editor__picks_default__windows(self):
        os.environ['EDITOR'] = ''
        fileoperations.write_config_setting('global', 'editor', None)

        self.assertEqual('notepad.exe', fileoperations.get_editor())

    @pytest.mark.skipif(sys.platform.startswith('win'), reason='Behaviour is exclusive to Linux')
    def test_get_editor__cant_determine_editor__picks_default__non_windows(self):
        os.environ['EDITOR'] = ''
        fileoperations.write_config_setting('global', 'editor', None)

        self.assertEqual('nano', fileoperations.get_editor())

    def test_delete_env_file(self):
        open(os.path.join('.elasticbeanstalk', 'my-environment.env.yml'), 'w').close()
        open(os.path.join('.elasticbeanstalk', 'my-environment.ebe.yml'), 'w').close()

        fileoperations.delete_env_file('my-environment')

    def test_delete_app_file(self):
        open(os.path.join('.elasticbeanstalk', 'my-application.env.yml'), 'w').close()

        fileoperations.delete_app_file('my-application')

    @unittest.skipIf(not hasattr(os, 'symlink'), reason='"symlink" appears to not have been defined on "os"')
    def test_zip_up_project(self):
        shutil.rmtree('home')
        os.mkdir('src')
        os.mkdir(os.path.join('src', 'lib'))
        open(os.path.join('src', 'lib', 'app.py'), 'w').write('import os')
        open(os.path.join('src', 'lib', 'app.py~'), 'w').write('import os')
        open(os.path.join('src', 'lib', 'ignore-this-file.py'), 'w').write('import os')

        os.symlink(
            os.path.join('src', 'lib', 'app.py'),
            os.path.join('src', 'lib', 'app.py-copy')
        )

        os.mkdir(os.path.join('src', 'lib', 'api'))

        if sys.version_info > (3, 0):
            os.symlink(
                os.path.join('src', 'lib', 'api'),
                os.path.join('src', 'lib', 'api-copy'),
                target_is_directory=True
            )
        else:
            os.symlink(
                os.path.join('src', 'lib', 'api'),
                os.path.join('src', 'lib', 'api-copy')
            )

        open(os.path.join('src', 'lib', 'api', 'api.py'), 'w').write('import unittest')

        fileoperations.zip_up_project(
            'app.zip',
            ignore_list=[os.path.join('src', 'lib', 'ignore-this-file.py')]
        )

        os.mkdir('tmp')
        fileoperations.unzip_folder('app.zip', 'tmp')

        self.assertTrue(os.path.exists(os.path.join('tmp', 'src', 'lib', 'app.py')))
        self.assertTrue(os.path.exists(os.path.join('tmp', 'src', 'lib', 'api')))
        self.assertTrue(os.path.exists(os.path.join('tmp', 'src', 'lib', 'app.py-copy')))
        self.assertTrue(os.path.exists(os.path.join('tmp', 'src', 'lib', 'api-copy')))
        self.assertFalse(os.path.exists(os.path.join('tmp', 'src', 'lib', 'app.py~')))
        self.assertFalse(os.path.exists(os.path.join('tmp', 'src', 'lib', 'ignore-this-file.py')))

    def test_delete_app_versions(self):
        os.mkdir(os.path.join('.elasticbeanstalk', 'app_versions'))

        fileoperations.delete_app_versions()

        self.assertFalse(
            os.path.exists(os.path.join('.elasticbeanstalk', 'app_versions'))
        )

    def test_program_is_installed(self):
        self.assertTrue(fileoperations.program_is_installed('eb'))

    def test_get_logs_location(self):
        self.assertEqual(
            os.path.join(os.path.abspath('.'), '.elasticbeanstalk', 'logs', 'some-folder'),
            fileoperations.get_logs_location('some-folder')
        )

    def test_get_zip_location(self):
        self.assertEqual(
            os.path.join(os.path.abspath('.'), '.elasticbeanstalk', 'app_versions', 'some-file'),
            fileoperations.get_zip_location('some-file')
        )

    def test_get_project_root(self):
        root = os.getcwd()
        os.mkdir('src')
        os.mkdir(os.path.join('src', 'app'))
        os.mkdir(os.path.join('src', 'app', 'dir'))

        os.chdir(os.path.join('src', 'app', 'dir'))

        self.assertEqual(
            root,
            fileoperations.get_project_root()
        )

    def test_save_to_aws_config__config_file_abosent(self):
        fileoperations.save_to_aws_config('my-access-key', 'my-secret-key')

        self.assertEqual(
            """[profile eb-cli]
aws_access_key_id = my-access-key
aws_secret_access_key = my-secret-key""",
            open(os.path.join('home', '.aws', 'config')).read().strip()
        )

    def test_save_to_aws_config__config_file_present__eb_cli_profile_absent(self):
        os.mkdir(os.path.join('home', '.aws'))

        open(os.path.join('home', '.aws', 'config'), 'w').write(
            """[profile aws-cli]
aws_access_key_id = my-access-key
aws_secret_access_key = my-secret-key"""
        )

        fileoperations.save_to_aws_config('my-access-key', 'my-secret-key')

        self.assertEqual(
            """[profile aws-cli]
aws_access_key_id = my-access-key
aws_secret_access_key = my-secret-key

[profile eb-cli]
aws_access_key_id = my-access-key
aws_secret_access_key = my-secret-key""",
            open(os.path.join('home', '.aws', 'config')).read().strip()
        )

    def test_get_war_file_location(self):
        os.mkdir('build')
        os.mkdir(os.path.join('build', 'libs'))
        open(os.path.join('build', 'libs', 'war1.war'), 'w').write('')
        open(os.path.join('build', 'libs', 'war2.war'), 'w').write('')

        self.assertTrue(
            fileoperations.get_war_file_location() in [
                os.path.abspath(os.path.join('build', 'libs', 'war1.war')),
                os.path.abspath(os.path.join('build', 'libs', 'war2.war'))
            ]
        )

    def test_get_war_file_location__war_file_absent(self):
        with self.assertRaises(fileoperations.NotFoundError) as context_manager:
            fileoperations.get_war_file_location()

        self.assertEqual(
            'Can not find .war artifact in {}'.format(os.path.join('build', 'libs') + os.path.sep),
            str(context_manager.exception)
        )

    def test_make_eb_dir__directory_already_exists(self):
        self.create_config_file()
        os.mkdir(os.path.join('.elasticbeanstalk', 'saved_configs'))

        with patch('os.makedirs') as makedirs_mock:
            fileoperations.make_eb_dir('saved_configs')

            makedirs_mock.assert_not_called()

    def test_make_eb_dir(self):
        self.create_config_file()

        with patch('os.makedirs') as makedirs_mock:
            fileoperations.make_eb_dir('saved_configs')

            makedirs_mock.assert_called_once_with(
                os.path.join('.elasticbeanstalk', 'saved_configs')
            )

    def test_clean_up(self):
        self.create_config_file()

        fileoperations.clean_up()

        self.assertFalse(os.path.exists('elasticbeanstalk'))

    @unittest.skipIf(
        condition=sys.platform.startswith('win'),
        reason='file permissions work differently on Windows'
    )
    def test_set_user_only_permissions(self):
        dir_1 = 'dir_1'
        dir_2 = os.path.join('dir_1', 'dir_2')
        dir_3 = os.path.join('dir_1', 'dir_2', 'dir_3')
        file_1 = os.path.join('dir_1', 'dir_2', 'dir_3', 'file_1')
        os.mkdir(dir_1)
        os.mkdir(dir_2)
        os.mkdir(dir_3)
        open(file_1, 'w').close()

        fileoperations.set_user_only_permissions('dir_1')

        if sys.version_info < (3, 0):
            self.assertEqual('040755', oct(os.stat(dir_1)[stat.ST_MODE]))
            self.assertEqual('040700', oct(os.stat(dir_2)[stat.ST_MODE]))
            self.assertEqual('040700', oct(os.stat(dir_3)[stat.ST_MODE]))
            self.assertEqual('0100600', oct(os.stat(file_1)[stat.ST_MODE]))
        else:
            self.assertEqual('0o40755', oct(os.stat(dir_1)[stat.ST_MODE]))
            self.assertEqual('0o40700', oct(os.stat(dir_2)[stat.ST_MODE]))
            self.assertEqual('0o40700', oct(os.stat(dir_3)[stat.ST_MODE]))
            self.assertEqual('0o100600', oct(os.stat(file_1)[stat.ST_MODE]))

    def test_get_platform_version(self):
        self.create_config_file()
        fileoperations.write_config_setting('global', 'platform_version', 'my-platform-version')

        self.assertEqual(
            'my-platform-version',
            fileoperations.get_platform_version()
        )

    def test_get_platform_version__directory_not_initialized(self):
        self.assertIsNone(fileoperations.get_platform_version())

    def test_get_instance_profile(self):
        self.create_config_file()
        fileoperations.write_config_setting('global', 'instance_profile', 'my-instance-profile')

        self.assertEqual(
            'my-instance-profile',
            fileoperations.get_instance_profile()
        )

    def test_get_instance_profile__directory_not_initialized(self):
        self.assertEqual(
            'default',
            fileoperations.get_instance_profile(default='default')
        )

    def test_get_application_name(self):
        self.create_config_file()
        fileoperations.write_config_setting('global', 'application_name', 'my-application-name')

        self.assertEqual(
            'my-application-name',
            fileoperations.get_application_name()
        )

    def test_get_platform_name(self):
        self.create_config_file()
        fileoperations.write_config_setting('global', 'platform_name', 'my-platform-name')

        self.assertEqual(
            'my-platform-name',
            fileoperations.get_platform_name()
        )

    def test_get_workspace_type(self):
        self.create_config_file()
        fileoperations.write_config_setting('global', 'workspace_type', 'application')

        self.assertEqual(
            'application',
            fileoperations.get_workspace_type()
        )

    def test_get_workspace_type__application_not_inited(self):

        with self.assertRaises(fileoperations.NotInitializedError):
            fileoperations.get_workspace_type()

    def test_get_workspace_type__application_not_inited__default_provided(self):

        self.assertEqual(
            'platform',
            fileoperations.get_workspace_type(default='platform')
        )

    def test_project_root__traverse__file_system_root_reached(self):
        if os.path.isdir('.elasticbeanstalk'):
            shutil.rmtree('.elasticbeanstalk')

        cwd = os.getcwd()
        with patch('os.getcwd') as getcwd_mock:
            getcwd_mock.return_value = cwd

            with self.assertRaises(fileoperations.NotInitializedError) as context_manager:
                fileoperations.ProjectRoot.traverse()

            self.assertEqual(
                'EB is not yet initialized',
                str(context_manager.exception)
            )

    def test_update_platform_version(self):
        self.create_config_file()

        fileoperations.update_platform_version('my-platform-version')
        self.assertEqual(
            'my-platform-version',
            fileoperations.get_platform_version()
        )

    def test_write_keyname(self):
        self.create_config_file()

        fileoperations.write_keyname('my-keyname')
        self.assertEqual(
            'my-keyname',
            fileoperations.get_keyname()
        )

    def test_directory_empty(self):
        os.mkdir('temp')

        self.assertTrue(fileoperations.directory_empty('temp'))
