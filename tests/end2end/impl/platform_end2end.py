# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
from shutil import copy

import pytest
from os import path
from six import print_

from ebcli.core.ebpcore import EBP
from ebcli.lib import elasticbeanstalk, aws
from ebcli.operations import commonops


class End2EndPlatform:
    PLATFORM_YAML = path.join(path.dirname(path.realpath(__file__)), 'platform.yaml')
    PLATFORM_JSON = path.join(path.dirname(path.realpath(__file__)), 'platform.json')

    def __init__(self, mock_output, mock_pager_output):
        self.region = 'us-east-1'
        self.create_platform_config()

        aws._flush()
        aws.set_region(self.region)

        self.get_platform_name()
        self.platform_arn = None

        self.mock_output = mock_output
        self.mock_pager_output = mock_pager_output

    def get_platform_arn(self):
        return self.platform_arn

    def _run_app(self, list_of_args):
        self.app = EBP(argv=list_of_args)
        self.app.setup()
        self.app.run()
        self.app.close()

    def create_platform_config(self):
        copy(End2EndPlatform.PLATFORM_YAML, 'platform.yaml')
        copy(End2EndPlatform.PLATFORM_JSON, 'platform.json')

    def get_platform_name(self):
        while True:
            self.platform_name = 'customPlatform' + str(randint(1000, 9999))
            # make sure application doesnt exist yet
            platforms = elasticbeanstalk.list_platform_versions(platform_name=self.platform_name)

            # Only use this name if there are no platforms of this type
            if len(platforms) == 0:
                break

    def do_init(self):
        self._run_app(['init', self.platform_name,
                       '--region', self.region,
                       '--instance_profile', 'aws-elasticbeanstalk-ec2-role'])

    def do_create(self):
        self._run_app(['create', '1.0.0', '-i', 't1.micro'])

        # Make sure app was created
        platforms = elasticbeanstalk.list_platform_versions(platform_name=self.platform_name, owner='self')

        assert len(platforms) == 1

        self.platform_arn = platforms[0]['PlatformArn']

        assert self.platform_arn is not None


    def do_events(self):
        print_('starting events')
        self._run_app(['events'])

        # Wait for environment creation to complete
        commonops.wait_for_success_events(request_id=None, timeout_in_minutes=20, platform_arn=self.platform_arn)

        # Make sure that the platform is in the 'ready' state
        platforms = elasticbeanstalk.list_platform_versions(platform_name=self.platform_name, owner='self', status='Ready')

        assert len(platforms) == 1

    def do_status(self):
        print_('starting status')
        self._run_app(['status', '-v'])

    def do_logs(self, log_validation):
        print_('starting logs')
        self._run_app(['logs'])
        time.sleep(20)
        # Actual log contents
        calls = self.mock_pager_output.mock_calls

        self.assert_mock_call_contains_string(calls, log_validation)

    def do_logs_all(self):
        self._run_app(['logs', '--all'])

    def assert_mock_call_contains_string(self, calls, string):
        for mock_call in calls:
            if string in repr(mock_call):
                return

        pytest.fail("%s not in call parameter list")

    def do_list(self):
        print_('starting list')
        self._run_app(['list', '-v'])

    def do_delete_platform(self):
        print_('starting delete platform')
        if self.platform_arn:
            self._run_app(['delete', self.platform_arn, '--force'])
