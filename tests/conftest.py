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
import pytest
from ebcli.core.ebrun import fix_path


def pytest_configure(config):
    fix_path()


def pytest_addoption(parser):
    parser.addoption("--end2end", action="store_true",
                     help="run end2end tests")
    parser.addoption("--odin", nargs=1, action="store")


def pytest_runtest_setup(item):
    if 'end2end' not in item.keywords and item.config.getoption("--end2end"):
        pytest.skip("Only running end to end tests")

    if 'end2end' in item.keywords and not item.config.getoption("--end2end"):
        pytest.skip("Need --end2end option to run")
