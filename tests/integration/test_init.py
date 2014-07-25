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

import mock
import os
import shutil

from cement.utils import test
from ebcli.core.ebcore import EB
from ebcli.core import fileoperations
from integration.baseinttest import BaseIntegrationTest
from ebcli.resources.strings import strings
from ebcli.lib import elasticbeanstalk


class TestInit(BaseIntegrationTest):

    def test_init_standard(self):
        """
                testing for:
                1. Prompt for app name
                2. Ask to set up credentials: Accept
                3. Ask to set up default region: Accept
                4. Create app
            """
        app_name = 'ebcli-intTest-app'

        # Set up mock responses
        self.mock_aws.make_api_call.side_effect = [
            {'Applications': [{'ApplicationName': 'myApp'}]},  # describe call
            None  # create call, we don't need a return value
        ]

        self.mock_input.side_effect = [
            app_name,  # Application name
            'y',   # setup creds
            '12345',  # access key
            'ABCDEF',  # Secret Key
            'y',    # setup region
            '3',  # region
        ]

        try:
            # run cmd
            self.app = EB(argv=['init'])
            self.app.setup()
            self.app.run()
            self.app.close()

            # make sure everything happened
            self.mock_aws.make_api_call.assert_any_call(
                'elasticbeanstalk',
                'describe-applications',
                application_names=[app_name]
            )
            self.mock_aws.make_api_call.assert_called_with(
                'elasticbeanstalk',
                'create-application',
                application_name=app_name,
                description=strings['app.description'],
            )
            self.assertEqual(self.mock_input.call_count, 6)

        # clean up
        finally:
            # elasticbeanstalk.delete_application(app_name)
            pass


    def test_init_no_creds(self):
        """
                testing for:
                1. Give app name as cli option
                2. Ask to set up Credentials: Reject
                3. Ask to set up Region: Accept
                4. Fail to create app (no credentials)
        """

    def test_init_no_region(self):
        """
                testing for:
                1.  Give app name as cli option
                2. Credentials should be present,
                        Do not ask to set up credentials
                3. Ask to set up region: Reject
                4. Create app in default region
        """

    def test_init_override(self):
        """
                testing to make sure all options successfully override defaults
                 1. App name overrides config file app name
            """

    def test_init_no_git(self):
        """
                testing to make sure a warning is given if git is not installed
                1. Prompt for app name
                2. Create App
                3. Warn that git is not installed
        """

    def test_init_repeat(self):
        """
                testing to make sure init doesnt override anything if
                called a second time
                All options previously entered should be persisted
        """

    def test_init_app_exists(self):
        """
                Testing to make sure init doesnt fail or override any existing apps
                it should pull down environments from given app
        """