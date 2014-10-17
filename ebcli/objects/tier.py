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

from ..objects.exceptions import NotFoundError


class Tier():
    def __init__(self, name, typ, version):
        self.name = name
        self.type = typ
        self.version = version
        self.string = self.__str__()

    def to_struct(self):
        return {
            'Name': self.name,
            'Type': self.type,
            'Version': self.version
        }

    def __str__(self):
        return (self.name + '-' +
            self.type + '-' +
            self.version)

    def __eq__(self, other):
        if not isinstance(other, Tier):
            return False
        return self.string.lower() == other.string.lower()

    @staticmethod
    def get_all_tiers():
        lst = [
            Tier('WebServer', 'Standard', '1.0'),
            Tier('Worker', 'SQS/HTTP', '1.0'),
            Tier('Worker', 'SQS/HTTP', '1.1'),
        ]
        return lst

    @staticmethod
    def get_latest_tiers():
        lst = [
            Tier('WebServer', 'Standard', '1.0'),
            Tier('Worker', 'SQS/HTTP', '1.1'),
        ]
        return lst

    @staticmethod
    def parse_tier(string):
        if string.lower() == 'web' or string.lower() == 'webserver':
            return Tier('WebServer', 'Standard', '1.0')
        if string.lower() == 'worker':
            return Tier('Worker', 'SQS/HTTP', '1.1')


        name, typ, version = string.split('-')
        result = Tier(name, typ, version)

        for tier in Tier.get_all_tiers():
            if tier == result:
                # we want to return the Proper, uppercase version
                return tier

        # tier not found
        raise NotFoundError('Tier Not found')