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

from ebcli.core.ebcore import EB


class TestLifecycle(unittest.TestCase):
    app_name = 'foo_app'

    def setUp(self):
        self.patcher_lifecycle_ops = mock.patch('ebcli.controllers.lifecycle.lifecycleops')
        self.patcher_base_get_app = mock.patch('ebcli.controllers.restore.AbstractBaseController.get_app_name')
        self.mock_lifecycle_ops = self.patcher_lifecycle_ops.start()
        self.mock_base_get_app = self.patcher_base_get_app.start()

    def tearDown(self):
        self.patcher_lifecycle_ops.stop()
        self.patcher_base_get_app.stop()

    def test_lifecycle_with_print_flag(self):
        self.mock_base_get_app.return_value = self.app_name

        EB.Meta.exit_on_close = False
        self.app = EB(argv=['appversion', 'lifecycle', '--print'])
        self.app.setup()
        self.app.run()
        self.app.close()

        self.mock_lifecycle_ops.print_lifecycle_policy.assert_called_with(self.app_name)

    def test_lifecycle_no_args_spawn_interactive(self):
        self.mock_base_get_app.return_value = self.app_name

        EB.Meta.exit_on_close = False
        self.app = EB(argv=['appversion', 'lifecycle'])
        self.app.setup()
        self.app.run()
        self.app.close()

        self.mock_lifecycle_ops.print_lifecycle_policy.assert_not_called()
        self.mock_lifecycle_ops.interactive_update_lifcycle_policy.assert_called_with(self.app_name)
