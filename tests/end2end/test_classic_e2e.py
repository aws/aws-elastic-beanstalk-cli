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


import pytest

from ebcli.core.ebcore import EB
from tests.end2end.end2end import End2EndTest
from tests.end2end.impl.environment_end2end import EnvironmentEnd2End


class TestEnd2EndClassic(End2EndTest):
    app_class = EB

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

        self.test_runner.do_init('php')

        try:
            self.test_runner.do_create()
            self.test_runner.do_events()
            self.test_runner.do_status()
            self.test_runner.do_setenv()
            self.test_runner.do_printenv()
            self.test_runner.do_scale()
            # logs don't work because it saves them to a file and we can't read from that
            # self.test_runner.do_logs()
            self.test_runner.do_deploy()
            self.test_runner.do_list()
            self.test_runner.do_terminate()
        finally:
            self.test_runner.do_terminate_all()
            pass

    def setUp(self):
        super(TestEnd2EndClassic, self).setUp()
        self.test_runner = EnvironmentEnd2End(self.mock_output, self.mock_pager_output)

    def tearDown(self):
        super(TestEnd2EndClassic, self).tearDown()
