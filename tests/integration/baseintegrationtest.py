# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import logging
import os
import shutil
import sys

from tests.utilities.testutils import unittest, eb

from ebcli.core import fileoperations
from tests.utilities.beanstalkutils import BeanstalkUtilities

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger('ebcli.tests.integration.base')


class BaseIntegrationTest(unittest.TestCase):
    python_version = '-'.join(str(s) for s in sys.version_info[:3])
    app_name = 'test-app-{0}'.format(python_version)
    env_name = 'cli-test-env-{0}'.format(python_version)
    platform = 'python'
    region = 'us-west-2'
    test_dir = 'testDir'

    def setUp(self):
        # Per test setup
        pass

    def tearDown(self):
        # Per test tear down
        pass

    @classmethod
    def setUpClass(self):
        self.beanstalk_utils = BeanstalkUtilities(self.region, app_name=self.app_name, env_name=self.env_name)
        _setup_testing_workspace(self.test_dir)

        # Run eb init
        p = eb('init --region {0} --platform {1} {2}'.format(self.region, self.platform, self.app_name))
        if p.rc != 0:
            LOG.error("Failed to run 'eb init':\n{0}".format(p.stderr))
        LOG.info("init stdout: {0}".format(p.stdout))

        # Create the environment
        p = eb('create --instance_type c4.large --instance_profile aws-elasticbeanstalk-ec2-role --timeout 20'
               ' --service-role aws-elasticbeanstalk-service-role --elb-type classic {0}'.format(self.env_name))
        if p.rc != 0:
            LOG.error("Failed to run 'eb create':\n{0}".format(p.stderr))

        LOG.info("create stdout: {0}".format(p.stdout))

    @classmethod
    def tearDownClass(self):
        os.chdir(os.path.pardir)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)


def _setup_testing_workspace(dir_name):
    # Copy sample app to directory
    print(os.getcwd())
    full_sample_app_path = os.path.abspath('sampleApps{0}python-sample'.format(os.path.sep))
    src_files = os.listdir(full_sample_app_path)
    for file_name in src_files:
        full_file_name = os.path.join(full_sample_app_path, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, dir_name)

    # set up test directory
    if not os.path.exists(dir_name) or (os.path.exists(dir_name) and os.path.isfile(dir_name)):
        os.remove(dir_name)
        os.makedirs(dir_name)
    os.chdir(dir_name)

    # set up mock home dir
    if not os.path.exists('home'):
        os.makedirs('home')

    # change directory to mock home
    if not os.path.exists(fileoperations.aws_credentials_location):
        fileoperations.aws_config_folder = 'home' + os.path.sep
        fileoperations.aws_credentials_location \
            = fileoperations.aws_config_folder + 'credentials'
    LOG.info("Using credentials from: ".format(fileoperations.aws_credentials_location))
