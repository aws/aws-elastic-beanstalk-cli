# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import sys

import pytest

from ebcli.core import fileoperations, io
from ebcli.core.ebrun import fix_path


def ensure_eb_application_has_not_been_initialized():
    if '--help' in sys.argv:
        # Allow `pytest --help` to print
        return

    if fileoperations.inside_ebcli_project():
        exception_message = ' '.join(
            [
                'ERROR: This directory or one of its ancestors has been `eb init`-ed. Ensure that the .elasticbeanstalk',
                'directories in this directory or above it have been deleted in order for the test suite to run.'
            ]
        )
        io.echo(exception_message)
        exit(1)


ensure_eb_application_has_not_been_initialized()


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
