# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

from ebcli.objects.exceptions import EBCLIException


class PlatformVersion(object):
    class UnableToParseArnException(EBCLIException):
        pass

    ARN_PATTERN = re.compile(
        r'^arn:[^:]+:elasticbeanstalk:[^:]+:([^:]*):platform/([^/]+)/(\d+\.\d+\.\d+)$'
    )

    @classmethod
    def is_custom_platform_arn(cls, arn):
        if PlatformVersion.is_valid_arn(arn):
            return PlatformVersion(arn).account_id

    @classmethod
    def is_eb_managed_platform_arn(cls, arn):
        if PlatformVersion.is_valid_arn(arn):
            return not PlatformVersion(arn).account_id

    @classmethod
    def is_valid_arn(cls, arn):
        if not isinstance(arn, str) and not isinstance(arn, bytes):
            return False

        return PlatformVersion.ARN_PATTERN.search(arn)

    @classmethod
    def arn_to_platform(cls, arn):
        match = PlatformVersion.ARN_PATTERN.search(arn)

        if not match:
            raise PlatformVersion.UnableToParseArnException("Unable to parse arn '{}'".format(arn))

        account_id, platform_name, platform_version = match.group(1, 2, 3)

        return account_id, platform_name, platform_version

    @classmethod
    def get_platform_version(cls, arn):
        _, _, platform_version = PlatformVersion.arn_to_platform(arn)

        return platform_version

    @classmethod
    def get_platform_name(cls, arn):
        _, platform_name, _ = PlatformVersion.arn_to_platform(arn)

        return platform_name

    @classmethod
    def match_with_complete_arn(
            cls,
            platforms,
            input_platform_name
    ):
        for platform in platforms:
            if platform == input_platform_name:
                return PlatformVersion(platform)

    @classmethod
    def match_with_platform_name(
            cls,
            custom_platforms,
            input_platform_name
    ):
        for custom_platform in custom_platforms:
            if PlatformVersion.get_platform_name(custom_platform) == input_platform_name:
                return PlatformVersion(custom_platform)

    def __init__(self, arn):
        self.arn = arn
        account_id, platform_name, platform_version = PlatformVersion.arn_to_platform(arn)

        # For the sake of the CLI a version is the same thing as an ARN
        self.version = self.arn

        self.name = arn
        self.account_id = account_id
        self.platform_version = platform_version
        self.platform_shorthand = platform_name

    def __str__(self):
        return self.version

    def __eq__(self, other):
        if not isinstance(other, PlatformVersion):
            return False

        return self.version == other.version

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def has_healthd_group_version_2_support(self):
        if PlatformVersion.is_custom_platform_arn(self.name):
            return False

        return pkg_resources.parse_version(self.platform_version) \
            >= pkg_resources.parse_version('2.0.10')

    @property
    def has_healthd_support(self):
        return pkg_resources.parse_version(self.platform_version) \
               >= pkg_resources.parse_version('2.0.0')
