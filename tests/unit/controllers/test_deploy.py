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

from ebcli.controllers.deploy import DeployController
from .basecontrollertest import BaseControllerTest
from ebcli.core.ebcore import EB
from ebcli.operations import commonops

from cement.utils import test

from ebcli.core import fileoperations
from ebcli.objects.solutionstack import SolutionStack
from ebcli.objects.tier import Tier
from ebcli.operations import commonops

class TestDeploy(BaseControllerTest):
    solution = SolutionStack('64bit Amazon Linux 2015.03 v2.0.6 running PHP 5.5')
    app_name = 'ebcli-intTest-app'
    env_name = 'my-env'
    tier = Tier.get_all_tiers()[0]
    app_class = DeployController

    def setUp(self):
        self.module_name = 'deploy'
        super(TestDeploy, self).setUp()
        fileoperations.create_config_file(self.app_name, 'us-west-2',
                                          self.solution.string)

    def test_deploy_multi_app_selection(self):
        app = DeployController()
        app.app = self.get_multi_app_args()
        app.multiple_app_deploy = mock.MagicMock()

        # Deploy app
        app.do_command()

        # Make sure that it was run as a multi-app deployment
        app.multiple_app_deploy.assert_called_once_with()

    def test_deploy_multi_app_compose_deploy(self):
        app = DeployController()
        app.app = self.get_multi_app_args()
        app.compose_deploy = mock.MagicMock()

        # Deploy app
        app.do_command()

        # Make sure that it was run as a multi-app deployment
        app.compose_deploy.assert_called_once_with()

    def test_deploy_with_preprocessing(self):
        # run cmd
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['deploy', '--process', self.env_name])
        self.app.setup()
        self.app.run()
        self.app.close()

        # Make sure that it was run as a multi-app deployment
        args, kwargs = self.mock_operations.deploy.call_args
        self.mock_operations.deploy.assert_called_with(self.app_name, self.env_name, None, None, None, group_name=None,
                                                       process_app_versions=True, source=None, staged=False,
                                                       timeout=None)

    def get_multi_app_args(self):
        pargs = mock.MagicMock(
            environment_name = self.env_name,
            message = 'My message',
            staged = False,
            timeout = 10,
            modules = ['foo', 'bar'],
            version = None)

        return mock.MagicMock(pargs = pargs)
