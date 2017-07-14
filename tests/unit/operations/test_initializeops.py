# -*- coding: utf-8 -*-

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
import sys
import shutil
import unittest

import mock
from ebcli.core import fileoperations
from ebcli.operations import initializeops


class TestInitializeOperations(unittest.TestCase):

    def setUp(self):
        # set up test directory
        if not os.path.exists('testDir'):
            os.makedirs('testDir')
        os.chdir('testDir')

        # set up mock elastic beanstalk directory
        if not os.path.exists(fileoperations.beanstalk_directory):
            os.makedirs(fileoperations.beanstalk_directory)

        # set up mock home dir
        if not os.path.exists('home'):
            os.makedirs('home')

        # change directory to mock home
        fileoperations.aws_config_folder = 'home' + os.path.sep
        fileoperations.aws_config_location \
            = fileoperations.aws_config_folder + 'config'

        # Create local
        fileoperations.create_config_file('ebcli-test', 'us-east-1',
                                          'my-solution-stack')

    def tearDown(self):
        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            if sys.platform.startswith('win'):
                os.system('rmdir /S /Q testDir')
            else:
                shutil.rmtree('testDir')


    @mock.patch('ebcli.operations.initializeops.codebuild')
    def test_get_codebuild_image_from_platform_that_exists(self, mock_codebuild):
        # Delcare variables local to this test
        expected_image = {u'name': u'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6',
                              u'description': u'Java 8 Running on Amazon Linux 64bit '}
        curated_images_response = [{u'name': u'aws/codebuild/eb-java-7-amazonlinux-64:2.1.6',
                              u'description': u'Java 7 Running on Amazon Linux 64bit '},
                             expected_image,
                             {u'name': u'aws/codebuild/eb-go-1.5-amazonlinux-64:2.1.6',
                              u'description': u'Go 1.5 Running on Amazon Linux 64bit '}]

        # Mock out methods
        mock_codebuild.list_curated_environment_images.return_value = curated_images_response

        # Make the actual call
        images_for_platform = initializeops.get_codebuild_image_from_platform("Java 8")

        # Assert methods were called with the right params and returned the correct values
        self.assertEqual(expected_image, images_for_platform,
                         "Expected '{0}' but got: {1}".format(expected_image, images_for_platform))

    @mock.patch('ebcli.operations.initializeops.codebuild')
    def test_get_codebuild_image_from_platform_that_does_not_match(self, mock_codebuild):
        # Delcare variables local to this test
        curated_images_response = [{u'name': u'aws/codebuild/eb-java-7-amazonlinux-64:2.1.6',
                                    u'description': u'Java 7 Running on Amazon Linux 64bit '},
                                   {u'name': u'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6',
                                    u'description': u'Java 8 Running on Amazon Linux 64bit '},
                                   {u'name': u'aws/codebuild/eb-go-1.5-amazonlinux-64:2.1.6',
                                    u'description': u'Go 1.5 Running on Amazon Linux 64bit '}]

        # Mock out methods
        mock_codebuild.list_curated_environment_images.return_value = curated_images_response

        # Make the actual call
        images_for_platform = initializeops.get_codebuild_image_from_platform(
            "64bit Amazon Linux 2016.09 v2.2.0 running Java 8")

        # Assert methods were called with the right params and returned the correct values
        self.assertEqual(curated_images_response, images_for_platform,
                         "Expected '{0}' but got: {1}".format(curated_images_response, images_for_platform))
