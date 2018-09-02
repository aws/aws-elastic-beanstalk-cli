# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
try:
    from pip._internal.operations.check import (
        check_package_set,
        create_package_set_from_installed,
    )
except ImportError:
    raise ImportError('You need pip>=18.0 to check for dependency incompatibilities.')

from ebcli.core import io


def color_red(message):
    io.echo(io.bold(io.color('red', message)))


def color_green(message):
    io.echo(io.bold(io.color('green', message)))


def check_for_missing_requirements_and_dependency_incompatibilities():
    try:
        package_set = create_package_set_from_installed()
        missing, conflicting = check_package_set(package_set)

        io.echo('  - Checking for missing requirements ... ')
        if missing:
            color_red('    Found unmet dependencies')
            color_red(missing)
        else:
            color_green('    OK!')

        io.echo('  - Checking for dependency incompatibilities ... ')
        if conflicting:
            color_red('    Found dependency incompatibilities')
            color_red(conflicting)
        else:
            color_green('    OK!')

        if missing or conflicting:
            exit(1)
    except Exception as e:
        raise RuntimeError(
            '    Something went wrong while attempting to find missing and/or incompatible dependencies. '
            'The following exception was raised: \n    {}'.format(str(e))
        )


io.echo('Checking for dependency mismatches ...')
check_for_missing_requirements_and_dependency_incompatibilities()
