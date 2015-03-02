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

from cement.utils import test


class BaseOperationsTest(test.CementTestCase):
    module_name = 'base'

    def setUp(self):
        super(BaseOperationsTest, self).setUp()
        self.reset_backend()
        self.patcher_input = mock.patch('ebcli.core.io.get_input')
        self.patcher_eb = mock.patch('ebcli.operations.' + self.module_name + '.elasticbeanstalk')
        self.patcher_output = mock.patch('ebcli.core.io.echo')
        self.patcher_file = mock.patch('ebcli.operations.' + self.module_name + '.fileoperations')

        self.mock_input = self.patcher_input.start()
        self.mock_elasticbeanstalk = self.patcher_eb.start()
        self.mock_output = self.patcher_output.start()
        # self.mock_fileoperations = self.patcher_file().start()

    def tearDown(self):
        self.patcher_eb.stop()
        self.patcher_input.stop()
        self.patcher_output.stop()
        # self.patcher_file.stop()