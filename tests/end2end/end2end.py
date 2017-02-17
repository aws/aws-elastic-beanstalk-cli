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


import os
import shutil

import mock

from cement.utils import test

from ebcli.core.ebpcore import EBP


class End2EndTest(test.CementTestCase):
    app_class = EBP

    def setUp(self):
        super(End2EndTest, self).setUp()

        # set up test directory
        self.directory = 'testDir' + os.path.sep
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        os.chdir(self.directory)

        self.patcher_output = mock.patch('ebcli.core.io.echo')
        self.patcher_pager_output = mock.patch('ebcli.core.io.echo_with_pager')

        self.mock_output = self.patcher_output.start()
        self.mock_pager_output = self.patcher_pager_output.start()

    def tearDown(self):
        os.chdir(os.path.pardir)
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)

        self.patcher_output.stop()
        self.patcher_pager_output.stop()
