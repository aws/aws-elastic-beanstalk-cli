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

from .basecontrollertest import BaseControllerTest

from ebcli.core import fileoperations
from ebcli.core.ebpcore import EBP
from ebcli.objects.exceptions import InvalidOptionsError
from ebcli.operations import commonops, initializeops
from ebcli.core.ebglobals import Constants

class TestDeletePlatform(BaseControllerTest):
    app_name = 'ebcli-intTest-app'

    def setUp(self):
        self.module_name = 'platform'
        self.platform_name = 'test-platform'
        self.platform_version = '1.0.0'
        self.platform_arn = 'arn:aws:elasticbeanstalk:us-east-1:647823116501:platform/{0}/{1}'.format(
            self.platform_name,
            self.platform_version)

        super(TestDeletePlatform, self).setUp()
        initializeops.setup(
            'Custom Platform Builder',
            'us-east-1',
            None,
            workspace_type=Constants.WorkSpaceTypes.PLATFORM,
            platform_name=self.platform_name,
            platform_version=self.platform_version,
            instance_profile='test-instance-profile')

    def run_command(self, *args):
        ebcore.EB.Meta.exit_on_close = False
        self.app = ebcore.EBP(argv=list(args))
        self.app.setup()
        self.app.run()
        self.app.close()

    @mock.patch('ebcli.controllers.platform.delete.delete_platform_version')
    def test_delete_force_flag(self, mock_delete_platform_version):
        """
            Make sure that the force flag works
        """
        # run cmd
        EBP.Meta.exit_on_close = False
        self.app = EBP(argv=['delete', self.platform_arn, '--force'])
        self.app.setup()
        self.app.run()
        self.app.close()

        mock_delete_platform_version.assert_called_with(self.platform_arn, True)
    
    @mock.patch('ebcli.controllers.platform.delete.delete_platform_version')
    def test_delete_no_force_flag(self, mock_delete_platform_version):
        """
            Make sure that the force flag works
        """
        # run cmd
        EBP.Meta.exit_on_close = False
        self.app = EBP(argv=['delete', self.platform_arn])
        self.app.setup()
        self.app.run()
        self.app.close()

        mock_delete_platform_version.assert_called_with(self.platform_arn, False)

