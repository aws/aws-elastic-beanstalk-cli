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

import re

import pkg_resources

from cement.utils.misc import minimal_logger

from ..lib import utils

LOG = minimal_logger(__name__)


class SolutionStack():
    def __init__(self, ss_string):
        self.name = ss_string
        self.platform = self.get_platform(ss_string)
        self.version = self.get_version(ss_string)
        self.server = self.get_server(ss_string)
        self.stack_version = self.get_stack_version(ss_string)
        self.string = self.name

    def __str__(self):
        return self.string

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return self.__dict__ != other.__dict__

    def has_healthd_support(self):
        return utils.parse_version(self.stack_version) \
               >= utils.parse_version('2.0')

    def has_healthd_group_version_2_support(self):
        stack_version = utils.parse_version(self.stack_version)
        if stack_version is not None:
            return stack_version >= utils.parse_version('2.0.10')
        return True

    @staticmethod
    def get_platform(ss_string):
        pattern = re.compile('.+running\s([^0-9]+).*')
        matcher = re.match(pattern, ss_string)
        if matcher is None:
            LOG.debug("Can not find a platform in string: " + ss_string)
            return ss_string
        return matcher.group(1).strip()

    @staticmethod
    def get_version(ss_string):
        pattern = re.compile('.+running\s(.*)')
        matcher = re.match(pattern, ss_string)
        if matcher is None:
            LOG.debug("Can not find a version in string: " + ss_string)
            return ss_string
        return matcher.group(1)

    @staticmethod
    def get_server(ss_string):
        pattern = re.compile('(.*)\srunning\s.*')
        matcher = re.match(pattern, ss_string)
        if matcher is None:
            LOG.debug("Can not find a server in string: " + ss_string)
            return ss_string
        return matcher.group(1)

    @staticmethod
    def get_stack_version(ss_string):
        pattern = re.compile('.+v([0-9.]+)\srunning\s.*')
        matcher = re.match(pattern, ss_string)
        if matcher is None:
            LOG.debug("Can not find a patch version in string: " + ss_string)
            return ss_string
        return matcher.group(1)

    def pythonify(self):
        return self.version.lower().replace(' ', '-').replace('---', '-')
