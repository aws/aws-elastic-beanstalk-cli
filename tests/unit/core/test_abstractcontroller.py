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

from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.objects.exceptions import NoEnvironmentForBranchError
from tests.unit.controllers.basecontrollertest import BaseControllerTest

class TestAbstract(BaseControllerTest):
    env_name = 'ebcli-abstractTest-env'
    env_name_alt = 'ebcli-abstractTest-env-alt'

    def setUp(self):
        self.patcher_commonops = mock.patch('ebcli.core.abstractcontroller.commonops')
        self.mock_commonops = self.patcher_commonops.start()
        # setup mock to disable finding env_name from current branch
        self.mock_commonops.get_current_branch_environment.return_value = None

    def tearDown(self):
        self.patcher_commonops.stop()

    def test_get_env_name_from_args(self):
        app = AbstractBaseController()
        # setup args for controller
        pargs = mock.MagicMock(environment_name=self.env_name)
        args = mock.MagicMock(pargs=pargs)
        app.app = args

        # get env_name by using default varname 'environment_name'
        self.assertEquals(app.get_env_name(), self.env_name)

    def test_get_env_name_from_args_by_varname(self):
        app = AbstractBaseController()
        # setup args for controller
        pargs = mock.MagicMock(message=self.env_name_alt)
        args = mock.MagicMock(pargs=pargs)
        app.app = args

        # get env_name by using varname 'name'
        self.assertEquals(app.get_env_name(varname='message'), self.env_name_alt)

    def test_get_env_name_noerror(self):
        app = AbstractBaseController()
        # Now check the case that app.pargs don't have the param environment_name
        # No MagicMock here, because MagicMock returns even if attribute does not exist
        app.app = mock.MagicMock(pargs=object())

        # if noerror=True, should return None
        self.assertEquals(app.get_env_name(noerror=True), None)

    def test_get_env_name_fail(self):
        app = AbstractBaseController()
        # Now check the case that app.pargs don't have the param environment_name
        # No MagicMock here, because MagicMock returns even if attribute does not exist
        app.app = mock.MagicMock(pargs=object())

        # if noerror=False (by default), should raise exception
        with self.assertRaises(NoEnvironmentForBranchError):
            app.get_env_name()

