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
from random import randint
import pytest

import mock
from six import print_

from cement.utils import test
from ebcli.core.ebcore import EB
from ebcli.lib import elasticbeanstalk
from ebcli.objects.exceptions import *


class TestEnd2End(test.CementTestCase):
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
        self.create_index_file()
        self.region = 'us-east-1'
        self.get_app_name()

        self.do_init()
        try:
            self.do_create()
            self.do_events()
            self.do_status()
            self.do_setenv()
            self.do_scale()
            self.do_logs()
            self.do_deploy()
            self.do_list()
            self.do_terminate()
        finally:
            self.do_terminate_all()

    def _run_app(self, list_of_args):

        self.app = EB(argv=list_of_args)
        self.app.setup()
        self.app.run()
        self.app.close()

    def create_index_file(self):
        with open('index.html', 'w') as f:
            f.write('Hello World')

    def get_app_name(self):
        while True:
            self.app_name = 'myEBCLItest' + str(randint(1000, 9999))
            # make sure application doesnt exist yet
            try:
                app = elasticbeanstalk.describe_application(self.app_name)
            except NotFoundError:
                # Found one
                break

    def do_init(self):
        self._run_app(['init', self.app_name,
                       '--region', self.region,
                       '--platform', 'php'])

        # Make sure app exists
        elasticbeanstalk.describe_application(self.app_name)

        print_('Created application')

    def do_create(self):
        self.env_name = 'ebcli-testenv-' + str(randint(100000, 9999999))
        self._run_app(['create', self.env_name])

        # Make sure app was created
        elasticbeanstalk.get_environment(self.app_name, self.env_name)
        print_('created env ', self.env_name)

    def do_events(self):
        print_('starting events')
        self._run_app(['events'])


    def do_status(self):
        print_('starting status')
        self._run_app(['status', '-v'])


    def do_setenv(self):
        print_('starting setenv')
        self._run_app(['setenv', 'foo=bar'])
        #ToDo: check to make sure env was set


    def do_logs(self):
        print_('starting logs')
        self._run_app(['logs'])
        self._run_app(['logs', '--all'])
        #ToDo: check location for logs

    def do_scale(self):
        print_('staring scale')
        self._run_app(['scale', '2'])
        # Check to make sure there are 2 running instances

    def do_deploy(self):
        print_('starting deploy')
        with open('index.html', 'w') as f:
            f.write('Hello World take 2')

        oldenv = elasticbeanstalk.get_environment(self.app_name, self.env_name)
        self._run_app(['deploy'])

        newenv = elasticbeanstalk.get_environment(self.app_name, self.env_name)

        self.assertNotEqual(oldenv.version_label, newenv.version_label)
        #ToDo: Check before and after deploy to make sure web is correct
        ## Maybe check after create to make sure app_version is correct

    def do_list(self):
        print_('starting list')
        self._run_app(['list', '-v'])
        #ToDo: Check and make sure output is ok

    def do_terminate(self):
        print_('starting terminate')
        self._run_app(['terminate', '--force'])
        #ToDo: Check and make sure env is gone

    def do_terminate_all(self):
        print_('starting terminate --all')
        self._run_app(['terminate', '--all', '--force'])
        #ToDo: Check and make sure app is gone

    def setUp(self):
        super(TestEnd2End, self).setUp()
        self.patcher_output = mock.patch('ebcli.core.io.echo')
        self.mock_output = self.patcher_output.start()

        # set up test directory
        self.directory = 'testDir' + os.path.sep
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        os.chdir(self.directory)

    def tearDown(self):
        self.patcher_output.stop()

        os.chdir(os.path.pardir)
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)