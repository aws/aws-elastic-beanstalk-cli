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

import ebcli.core.globals as eb


class SolutionStack():
    def __init__(self, ss_string):
        self.name = ss_string
        self.platform = self.get_platform(ss_string)
        self.version = self.get_version(ss_string)
        self.server = self.get_server(ss_string)
        self.string = self.create_string()

    def __repr__(self):
        return self.string

    def create_string(self):
    #  note: platform, version, and server should all exist already
        # handle custom stack case
        if self.version == self.platform:
            return self.pythonify(self.platform)

        # handle all other cases
        string = self.version + ' ' + self.server[0:5]
        if 'v' in self.server:
            string += ' ' + self.server[-6:]
        else:
            string += ' old'
        return self.pythonify(string)

    @staticmethod
    def get_platform(ss_string):
        pattern = re.compile('.+running\s([^\s]*).*')
        matcher = re.match(pattern, ss_string)
        if matcher is None:
            eb.app.log.debug("Can not find a platform in string: " + ss_string)
            return ss_string
        return matcher.group(1)

    @staticmethod
    def get_version(ss_string):
        pattern = re.compile('.+running\s(.*)')
        matcher = re.match(pattern, ss_string)
        if matcher is None:
            eb.app.log.debug("Can not find a version in string: " + ss_string)
            return ss_string
        return matcher.group(1)

    @staticmethod
    def get_server(ss_string):
        pattern = re.compile('(.*)\srunning\s.*')
        matcher = re.match(pattern, ss_string)
        if matcher is None:
            eb.app.log.debug("Can not find a server in string: " + ss_string)
            return ss_string
        return matcher.group(1)

    @staticmethod
    def pythonify(string):
        return string.lower().replace(' ', '-')