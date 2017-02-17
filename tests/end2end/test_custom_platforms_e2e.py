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

import pytest
import shutil

from ebcli.core.ebpcore import EBP
from tests.end2end.end2end import End2EndTest
from tests.end2end.impl.platform_end2end import End2EndPlatform
from tests.end2end.impl.environment_end2end import EnvironmentEnd2End


class TestEnd2EndCustomPlatforms(End2EndTest):
    app_class = EBP

    """
    Test order
    init - make sure application gets created and file is good
    create - make sure environment is created

    do tests on basic environment operations
    events
    status
    status verbose
    setenv
    status verbose - make sure env was set
    logs
    scale
    status verbose - make sure more instances were launched


    make a change
    deploy

    Cant really test for open, console, or config because a CI wont be able to
    open browsers/text editor

    list
    terminate
    delete

    """

    @pytest.mark.end2end
    def test_end2end(self):
        """ Run all tests in this one method in order to preserve order """
        self.platform_test_runner.do_init()

        platform_test_app_dir = self.directory
        env_test_directory = 'testDirEnv'
        current_dir = platform_test_app_dir

        try:
            self.platform_test_runner.do_create()
            self.platform_test_runner.do_events()
            self.platform_test_runner.do_status()
            self.platform_test_runner.do_logs('build.rb')
            self.platform_test_runner.do_list()

            try:
                # Prepare for running the environment tests
                os.chdir(os.path.pardir)
                if not os.path.exists(env_test_directory):
                    os.makedirs(env_test_directory)
                os.chdir(env_test_directory)
                current_dir = env_test_directory

                self.env_test_runner.do_init(self.platform_test_runner.get_platform_arn())
                self.env_test_runner.do_create()

                self.env_test_runner.do_events()
                self.env_test_runner.do_status()
                self.env_test_runner.do_setenv()
                self.env_test_runner.do_printenv()
                self.env_test_runner.do_scale()
                self.env_test_runner.do_list()
                self.env_test_runner.do_terminate()
            finally:
                self.env_test_runner.do_terminate_all()
        finally:
            if current_dir == env_test_directory:
                os.chdir(os.path.pardir)
                if os.path.exists(env_test_directory):
                    shutil.rmtree(env_test_directory)

                os.chdir(platform_test_app_dir)

            self.platform_test_runner.do_delete_platform()

    def setUp(self):
        super(TestEnd2EndCustomPlatforms, self).setUp()
        self.env_test_runner = EnvironmentEnd2End(self.mock_output, self.mock_pager_output)
        self.platform_test_runner = End2EndPlatform(self.mock_output, self.mock_pager_output)

    def tearDown(self):
        super(TestEnd2EndCustomPlatforms, self).tearDown()
