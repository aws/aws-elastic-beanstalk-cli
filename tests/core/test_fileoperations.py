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
import yaml

from six.moves import configparser
from six.moves.configparser import NoOptionError

from core import fileoperations


class TestFileOperations(unittest.TestCase):
    def setUp(self):
        # set up test directory
        if not os.path.exists('testDir'):
            os.makedirs('testDir')
        os.chdir('testDir')

        # set up mock elastic beanstalk directory
        if not os.path.exists(fileoperations.beanstalk_directory):
            os.makedirs(fileoperations.beanstalk_directory)

        fileoperations.default_section = 'ebcli_test_default'

        #set up mock home dir
        if not os.path.exists('home'):
            os.makedirs('home')

        # change directory to mock home
        fileoperations.aws_config_folder = 'home' + os.path.sep
        fileoperations.aws_config_location \
            = fileoperations.aws_config_folder + 'config'

    def tearDown(self):
        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            shutil.rmtree('testDir')

    def test_read_aws_config_credentials_standard(self):
        # setup
        config = configparser.ConfigParser()

        default = fileoperations.default_section
        access1 = '123456'
        access2 = '567890'
        secret1 = 'abcdefg'
        secret2 = 'hijklmn'
        region1 = 'us-west-2'
        region2 = 'us-east-1'

        config.add_section(default)
        config.add_section('section1')
        config.set(default, 'aws_access_key_id', access1)
        config.set(default, 'aws_secret_access_key', secret1)
        config.set(default, 'region', region1)

        config.set('section1', 'aws_access_key_id', access2)
        config.set('section1', 'aws_secret_access_key', secret2)
        config.set('section1', 'region', region2)

        with open(fileoperations.aws_config_location, 'wb') as f:
            config.write(f)


        # do Test
        access, secret, region = fileoperations.read_aws_config_credentials()
        self.assertEqual(access, access1)
        self.assertEqual(secret, secret1)
        self.assertEqual(region, region1)



    def test_read_aws_config_credentials_no_region(self):
        # setup
        config = configparser.ConfigParser()

        default = fileoperations.default_section
        access1 = '123456'
        access2 = '567890'
        secret1 = 'abcdefg'
        secret2 = 'hijklmn'
        region2 = 'us-east-1'

        config.add_section(default)
        config.add_section('section1')
        config.set(default, 'aws_access_key_id', access1)
        config.set(default, 'aws_secret_access_key', secret1)

        config.set('section1', 'aws_access_key_id', access2)
        config.set('section1', 'aws_secret_access_key', secret2)
        config.set('section1', 'region', region2)

        with open(fileoperations.aws_config_location, 'wb') as f:
            config.write(f)


        # do Test
        access, secret, region = fileoperations.read_aws_config_credentials()
        self.assertEqual(access, access1)
        self.assertEqual(secret, secret1)
        self.assertEqual(region, None)

    def test_read_aws_config_credentials_region_only(self):
        # setup
        config = configparser.ConfigParser()

        default = fileoperations.default_section
        access2 = '567890'
        secret2 = 'hijklmn'
        region1 = 'us-west-2'
        region2 = 'us-east-1'

        config.add_section(default)
        config.add_section('section1')
        config.set(default, 'region', region1)

        config.set('section1', 'aws_access_key_id', access2)
        config.set('section1', 'aws_secret_access_key', secret2)
        config.set('section1', 'region', region2)

        with open(fileoperations.aws_config_location, 'wb') as f:
            config.write(f)


        # do Test
        access, secret, region = fileoperations.read_aws_config_credentials()
        self.assertEqual(access, None)
        self.assertEqual(secret, None)
        self.assertEqual(region, region1)

    def test_read_aws_config_credentials_no_file(self):
        # setup
        # make sure file doesn't exist
        if os.path.exists(fileoperations.aws_config_location):
            os.remove(fileoperations.aws_config_location)

        # do test
        access, secret, region = fileoperations.read_aws_config_credentials()
        self.assertEqual(access, None)
        self.assertEqual(secret, None)
        self.assertEqual(region, None)

    def test_read_aws_config_credentials_no_dir(self):
        # setup
        # make sure dir doesn't exist
        if os.path.exists(fileoperations.aws_config_folder):
            shutil.rmtree(fileoperations.aws_config_folder)

        # do test
        access, secret, region = fileoperations.read_aws_config_credentials()
        self.assertEqual(access, None)
        self.assertEqual(secret, None)
        self.assertEqual(region, None)

    def test_read_aws_config_credentials_empty_file(self):
        # setup
        with open(fileoperations.aws_config_location, 'wb') as f:
            f.write('')

        # do test
        access, secret, region = fileoperations.read_aws_config_credentials()
        self.assertEqual(access, None)
        self.assertEqual(secret, None)
        self.assertEqual(region, None)

    def test_save_to_aws_config_override(self):
        # first, write in some values
        fileoperations.save_to_aws_config('1234', 'abc', 'test_region')

        #now override
        access = '09876'
        secret = 'abDfg'
        region = 'us-east-1'
        fileoperations.save_to_aws_config(access, secret, region)

        # Grab values and make sure they were saved
        access_result, secret_result, region_result \
            = fileoperations.read_aws_config_credentials()

        # Test
        self.assertEqual(access, access_result)
        self.assertEqual(secret, secret_result)
        self.assertEqual(region, region_result)

    def test_save_to_aws_config_no_dir(self):
        # make sure directory doesn't exist
        if os.path.exists(fileoperations.aws_config_folder):
            shutil.rmtree(fileoperations.aws_config_folder)

        # write values
        access = '09876'
        secret = 'abDfg'
        region = 'us-east-1'
        fileoperations.save_to_aws_config(access, secret, region)

        # Grab values and make sure they were saved
        access_result, secret_result, region_result \
            = fileoperations.read_aws_config_credentials()

        # Test
        self.assertEqual(access, access_result)
        self.assertEqual(secret, secret_result)
        self.assertEqual(region, region_result)

    def test_save_to_aws_config_no_file(self):
        # make sure file doesn't exist
        if os.path.exists(fileoperations.aws_config_location):
            os.remove(fileoperations.aws_config_location)

        # write values
        access = '09876'
        secret = 'abDfg'
        region = 'us-east-1'
        fileoperations.save_to_aws_config(access, secret, region)

        # Grab values and make sure they were saved
        access_result, secret_result, region_result \
            = fileoperations.read_aws_config_credentials()

        # Test
        self.assertEqual(access, access_result)
        self.assertEqual(secret, secret_result)
        self.assertEqual(region, region_result)


    def test_save_to_aws_config_standard(self):
        # write values
        access = '09876'
        secret = 'abDfg'
        region = 'us-east-1'
        fileoperations.save_to_aws_config(access, secret, region)

        # Grab values and make sure they were saved
        access_result, secret_result, region_result \
            = fileoperations.read_aws_config_credentials()

        # Test
        self.assertEqual(access, access_result)
        self.assertEqual(secret, secret_result)
        self.assertEqual(region, region_result)


    def test_save_to_aws_config_no_region(self):
        # write values
        access = '09876'
        secret = 'abDfg'
        fileoperations.save_to_aws_config(access, secret, None)

        # Grab values and make sure they were saved
        access_result, secret_result, region_result \
            = fileoperations.read_aws_config_credentials()

        # Test
        self.assertEqual(access, access_result)
        self.assertEqual(secret, secret_result)
        self.assertEqual(None, region_result)

        # make sure nothing was saved to the file
        config = configparser.ConfigParser()
        config.read(fileoperations.aws_config_location)

        try:
            config.get(fileoperations.default_section,
                       fileoperations.aws_region)
            raise Exception('Should have thrown a no section error')
        except NoOptionError:
            pass  # Error expected


    def test_save_to_aws_config_region_only(self):
        # write values
        region = 'us-east-1'
        fileoperations.save_to_aws_config(None, None, region)

        # Grab values and make sure they were saved
        access_result, secret_result, region_result \
            = fileoperations.read_aws_config_credentials()

        # Test
        self.assertEqual(None, access_result)
        self.assertEqual(None, secret_result)
        self.assertEqual(region, region_result)

        # make sure nothing was saved to the file
        config = configparser.ConfigParser()
        config.read(fileoperations.aws_config_location)

        try:
            config.get(fileoperations.default_section,
                       fileoperations.aws_access_key)
            raise Exception('Should have thrown a no section error')
        except NoOptionError:
            pass  # Error expected

        try:
            config.get(fileoperations.default_section,
                       fileoperations.aws_secret_key)
            raise Exception('Should have thrown a no section error')
        except NoOptionError:
            pass  # Error expected


    def test_save_and_read_to_real_credentials_file(self):
        # change directory back to normal
        fileoperations.aws_config_folder = fileoperations.get_aws_home()
        fileoperations.aws_config_location \
            = fileoperations.aws_config_folder + 'config'

        access = '12345678'
        secret = 'aBcdEfgh'
        region = 'us-west-2'

        # save
        fileoperations.save_to_aws_config(access, secret, region)
        # read
        access_result, secret_result, region_result \
            = fileoperations.read_aws_config_credentials()

        # Test
        self.assertEqual(access, access_result)
        self.assertEqual(secret, secret_result)
        self.assertEqual(region, region_result)

    def test_get_application_name(self):
        # wrapper of get_config_setting
        pass


    def test_create_config_file_no_file(self):
        # make sure file doesn't exist
        if os.path.exists(fileoperations.local_config_file):
            os.remove(fileoperations.local_config_file)
        self.assertFalse(os.path.exists(fileoperations.local_config_file))

        app_name = 'ebcli-test'
        fileoperations.create_config_file(app_name)

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
        fileoperations.create_config_file(app_name)

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
        fileoperations.create_config_file(app_name)

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
        dir = 'fol1' + os.path.sep + 'fol2' + os.path.sep + 'fol3'
        os.makedirs(dir)
        os.chdir(dir)

        fileoperations._traverse_to_project_root()

        # get new working directory - make sure its the same as the original
        nwd = os.getcwd()
        self.assertEqual(cwd, nwd)

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
        fileoperations.create_config_file('ebcli-test')

        #make sure section does not exist
        dict = fileoperations._get_yaml_dict(fileoperations.local_config_file)
        self.assertFalse(dict.has_key('mytestsection'))

        # now do write
        fileoperations.write_config_setting('mytestsection', 'testkey', 'value')

        # make sure section now exists
        dict = fileoperations._get_yaml_dict(fileoperations.local_config_file)
        self.assertTrue(dict.has_key('mytestsection'))

    def test_write_config_setting_no_option(self):
        # create config file
        fileoperations.create_config_file('ebcli-test')

        #make sure section does exists, but option doesn't
        fileoperations.write_config_setting('mytestsection', 'notmykey', 'val')
        dict = fileoperations._get_yaml_dict(fileoperations.local_config_file)

        self.assertTrue(dict.has_key('mytestsection'))
        self.assertFalse(dict['mytestsection'].has_key('testkey'))

        # now do write
        fileoperations.write_config_setting('mytestsection', 'testkey', 'value')

        # make sure section now exists
        dict = fileoperations._get_yaml_dict(fileoperations.local_config_file)
        self.assertTrue(dict.has_key('mytestsection'))
        self.assertTrue(dict['mytestsection'].has_key('testkey'))
        self.assertEqual(dict['mytestsection']['testkey'], 'value')

    def test_write_config_setting_override(self):
        # create config file
        fileoperations.create_config_file('ebcli-test')

        #make sure app name exists
        dict = fileoperations._get_yaml_dict(fileoperations.local_config_file)
        self.assertTrue(dict.has_key('global'))
        self.assertTrue(dict['global'].has_key('application_name'))
        self.assertTrue(dict['global'].has_key('application_name'))
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
        fileoperations.write_config_setting('mytestsection', 'testkey', 'value')

        # make sure section and file now exists
        self.assertTrue(os.path.exists(fileoperations.local_config_file))
        dict = fileoperations._get_yaml_dict(fileoperations.local_config_file)
        self.assertTrue(dict.has_key('mytestsection'))

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
        fileoperations.create_config_file('ebcli-test')

        #get app name
        result = fileoperations.get_config_setting('global',
                                                   'application_name')

        self.assertEqual(result, 'ebcli-test')

    def test_get_config_setting_no_local(self):
        # create global file
        config = {'global':{'application_name':'myApp'}}
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
        fileoperations.create_config_file('ebcli-test')

        #get app name
        result = fileoperations.get_config_setting('global',
                                                   'application_name')

        # should return result from local NOT global
        self.assertEqual(result, 'ebcli-test')