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
    raise RuntimeError('You need pip==21.1 to check for dependency incompatibilities.')

from ebcli.core import io

_indent = '  '


def color_red(message):
    io.echo(io.bold(io.color('red', message)))


def color_green(message):
    io.echo(io.bold(io.color('green', message)))


def collect_package_requirements_by_requirement_name(req_name, package_set):
    required_by = dict()
    for pkg_name, package in package_set.items():
        for req in package.dependencies:
            if req.name.lower() == req_name.lower():
                required_by[pkg_name] = req.specifier

    return required_by


def collect_package_set():
    package_set = create_package_set_from_installed()[0]

    return package_set


def check_for_missing_requirements_and_dependency_incompatibilities():
    try:
        package_set = collect_package_set()
        missing, conflicting = check_package_set(package_set)

        io.echo('- Checking for missing requirements ... ')
        if missing:
            color_red('{}Found unmet dependencies'.format(_indent * 1))
            missing_description = describe_missing_results(missing, package_set)
            color_red(missing_description)
        else:
            color_green('{}OK!'.format(_indent * 2))

        io.echo('- Checking for dependency incompatibilities ... ')
        if conflicting:
            color_red('{}Found dependency incompatibilities'.format(_indent * 1))
            conflicting_description = describe_conflicting_results(conflicting, package_set)
            color_red(conflicting_description)
        else:
            color_green('{}OK!'.format(_indent * 1))

        if missing or conflicting:
            exit(1)
    except Exception as e:
        raise RuntimeError(
            '    Something went wrong while attempting to find missing and/or incompatible dependencies. '
            'The following exception was raised: \n    {}'.format(str(e))
        )


def describe_conflicting_results(conflicting, package_set):
    conflicting_reqs = dict()
    description = '{}Confliciting dependencies:\n'.format(_indent * 2)

    for pkg_name in conflicting:
        for result in conflicting[pkg_name]:

            req_name = result[0]
            req_version = result[1]
            req = result[2]

            if not req_name in conflicting_reqs:
                conflicting_reqs[req_name] = {
                    'required_by': collect_package_requirements_by_requirement_name(req_name, package_set),
                    'package_details': package_set[req_name]
                }

    for req_name, req in conflicting_reqs.items():
        req_version = req['package_details'].version
        description += '{}{}:\n'.format(_indent * 3, req_name)
        description += '{}Installed version: {}\n'.format(_indent * 4, req_version)
        description += '{}Required by:\n'.format(_indent * 4)
        for pkg_name, specifier in req['required_by'].items():
            is_conflict = not specifier.contains(req_version, prereleases=True)
            description += '{}{} {} ({}: {}) {}\n'.format(
                _indent * 5,
                pkg_name,
                package_set[pkg_name].version,
                req_name,
                specifier,
                '[CONFLICT]' if is_conflict else ''
            )

    return description


def describe_missing_results(missing, package_set):
    missing_reqs = dict()
    description = '{}Missing dependencies:\n'.format(_indent * 2)

    for pkg_name in missing:
        for result in missing[pkg_name]:

            req_name = result[0]

            if not req_name in missing_reqs:
                missing_reqs[req_name] = collect_package_requirements_by_requirement_name(req_name, package_set)

    for req_name, required_by in missing_reqs.items():
        description += '{}{}:\n'.format(_indent * 3, req_name)
        description += '{}Required by:\n'.format(_indent * 4)
        for pkg_name, specifier in required_by.items():
            description += '{}{} {} ({}: {})\n'.format(
                _indent * 5,
                pkg_name,
                package_set[pkg_name].version,
                req_name,
                specifier,
            )

    return description

io.echo('Checking for dependency mismatches ...')
check_for_missing_requirements_and_dependency_incompatibilities()
