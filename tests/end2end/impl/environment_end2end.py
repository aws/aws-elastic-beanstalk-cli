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

from random import randint
import time
import urllib

from pytest import fail
from six import print_

from ebcli.core.ebcore import EB
from ebcli.lib import elasticbeanstalk, aws
from ebcli.objects.exceptions import *
from ebcli.operations import commonops
from ebcli.resources.statics import namespaces, option_names


class EnvironmentEnd2End():
    def __init__(self, mock_output, mock_pager_output):
        aws._flush()
        self.region = 'us-east-1'
        aws.set_region(self.region)
        self.get_app_name()

        self.mock_output = mock_output
        self.mock_pager_output = mock_pager_output

    def _run_app(self, list_of_args):
        EB.Meta.exit_on_close = False
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
                elasticbeanstalk.describe_application(self.app_name)
            except NotFoundError:
                # Found one
                break

    def do_init(self, platform):
        self._run_app(['init', self.app_name,
                       '--region', self.region,
                       '--platform', platform])

        # Make sure app exists
        elasticbeanstalk.describe_application(self.app_name)
        print_('Created application')

    def do_create(self):
        self.create_index_file()

        self.env_name = 'ebcli-testenv-' + str(randint(100000, 9999999))
        self._run_app(['create', self.env_name, '-i', 't1.micro'])

        # Make sure app was created
        elasticbeanstalk.get_environment(app_name=self.app_name, env_name=self.env_name)
        print_('created env ', self.env_name)

    def do_events(self):
        print_('starting events')
        self._run_app(['events'])
        time.sleep(30)

        # Wait for environment creation to complete
        commonops.wait_for_success_events(request_id=None, timeout_in_minutes=30, app_name=self.app_name, env_name=self.env_name)

    def do_status(self):
        print_('starting status')
        self._run_app(['status', '-v'])

    def do_setenv(self):
        print_('starting setenv')
        self._run_app(['setenv', 'foo=bar'])

        time.sleep(30)
        commonops.wait_for_success_events(request_id=None, timeout_in_minutes=15, app_name=self.app_name, env_name=self.env_name)

    def do_printenv(self):
        print_('calling printenv')
        self._run_app(['printenv'])
        self.mock_output.assert_any_call('    ', 'foo', '=', 'bar')

    def do_logs(self):
        print_('starting logs')
        self._run_app(['logs'])
        time.sleep(30)
        # Actual log contents
        calls = self.mock_pager_output.mock_calls

        self.assert_mock_call_contains_string(calls, "eb-version-deployment.log")

        self._run_app(['logs', '--all'])

    def assert_mock_call_contains_string(self, calls, string):
        for mock_call in calls:
            if string in repr(mock_call):
                return

        fail("{0} not in call parameter list: {1}".format(string, calls))

    def do_scale(self):
        print_('staring scale')
        self._run_app(['scale', '2'])
        time.sleep(30)

        commonops.wait_for_success_events(
            request_id=None,
            timeout_in_minutes=20,
            app_name=self.app_name,
            env_name=self.env_name)

        # Check to make sure there are 2 running instances
        instances = commonops.get_instance_ids(None, self.env_name)
        assert len(instances) == 2

    def do_deploy(self):
        print_('starting deploy')
        app2_response = 'Hello World take 2'

        with open('index.html', 'w') as f:
            f.write(app2_response)

        old_env = elasticbeanstalk.get_environment(app_name=self.app_name, env_name=self.env_name)
        settings = elasticbeanstalk.describe_configuration_settings(
            self.app_name, self.env_name)

        option_settings = settings.get('OptionSettings', [])
        http_port = elasticbeanstalk.get_option_setting(
            option_settings,
            namespaces.LOAD_BALANCER,
            option_names.LOAD_BALANCER_HTTP_PORT)

        if http_port == 'OFF':
            url = "https://%s" % old_env.cname
        else:
            url = "http://%s" % old_env.cname

        # Show that we are running some app that is not the new app
        response = urllib.urlopen(url).read()
        assert response == 'Hello World'

        self._run_app(['deploy'])
        # Give the command time to be processed
        time.sleep(60)

        commonops.wait_for_success_events(
            request_id=None,
            timeout_in_minutes=20,
            app_name=self.app_name,
            env_name=self.env_name)

        new_env = elasticbeanstalk.get_environment(app_name=self.app_name, env_name=self.env_name)
        assert old_env.version_label != new_env.version_label

        # Check that the new app is up and running
        response = urllib.urlopen(url).read()
        assert app2_response in response

    def do_list(self):
        print_('starting list')
        self._run_app(['list', '-v'])

    def do_terminate(self):
        print_('starting terminate')
        self._run_app(['terminate', '--force'])

        commonops.wait_for_success_events(request_id=None, timeout_in_minutes=20, app_name=self.app_name, env_name=self.env_name)

    def do_terminate_all(self):
        print_('starting terminate --all')
        self._run_app(['terminate', '--all', '--force'])
