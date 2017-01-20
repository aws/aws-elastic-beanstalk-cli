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

from mock import patch

from ebcli.core.ebcore import EB
from .baseinttest import BaseIntegrationTest
from ebcli.resources.strings import strings
from ebcli.core import fileoperations
from ebcli.objects.sourcecontrol import NoSC
from ebcli.objects.solutionstack import SolutionStack

from ebcli.objects.exceptions import CredentialsError


class TestInit(BaseIntegrationTest):

    def test_init_standard(self):
        pass