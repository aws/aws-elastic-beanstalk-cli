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

from ebcli.operations import localops
from ebcli.resources.strings import strings, docker_ignore
from ebcli.docker import compat
from mock import patch
from unittest import TestCase

DOCKERIGNORE_PATH = '/.dockerignore'
EXPOSED_HOST_PORT = '1234'
NAME = 'name'
SOLN_STK = 'Docker'


class TestLocalops(TestCase):
    pass

