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

import unittest
import mock
from datetime import date, timedelta

from ebcli.core.ebcore import EB


class TestRestore(unittest.TestCase):
    def setUp(self):
        self.patcher_restore_ops = mock.patch('ebcli.controllers.restore.restoreops')
        self.patcher_base_controller = mock.patch('ebcli.controllers.restore.AbstractBaseController.get_app_name')
        self.mock_restore_ops = self.patcher_restore_ops.start()
        self.mock_base_controller = self.patcher_base_controller.start()

    def tearDown(self):
        self.patcher_restore_ops.stop()
        self.patcher_base_controller.stop()

    def test_restore_with_id(self):
        env_id = 'e-1234567890'

        EB.Meta.exit_on_close = False
        self.app = EB(argv=['restore', env_id])
        self.app.setup()
        self.app.run()
        self.app.close()

        self.mock_restore_ops.restore.assert_called_with(env_id)

    def test_restore_interactive(self):
        env1 = {'EnvironmnetId': "e-1234567890", 'EnvironmentName': "env1", 'VersionLabel': "v1",
                'ApplicationName': "app1",
                'DateUpdated': (date.today() - timedelta(days=10))}
        env2 = {'EnvironmnetId': "e-0987654321", 'EnvironmentName': "env2", 'VersionLabel': "v2",
                'ApplicationName': "app2",
                'DateUpdated': (date.today())}

        self.mock_restore_ops.get_restorable_envs.return_value = [env1, env2]

        EB.Meta.exit_on_close = False
        self.app = EB(argv=['restore'])
        self.app.setup()
        self.app.run()
        self.app.close()

        self.mock_restore_ops.display_environments.assert_called_with([env1, env2])
