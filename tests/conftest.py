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
import pytest_socket

from ebcli.core import fileoperations, io
from ebcli.core.ebrun import fix_path


pytest_socket.disable_socket()


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
