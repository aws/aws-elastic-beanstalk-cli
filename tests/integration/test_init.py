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


class TestInit(BaseIntegrationTest):

    def test_init_standard(self):
        self.app = EB(argv=['update'])
        self.app.setup()
        self.app.run()
        self.app.close()