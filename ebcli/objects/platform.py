import re

import pkg_resources

from ebcli.lib import utils


class PlatformVersion():
    ARN_PATTERN = re.compile('^arn:[^:]+:elasticbeanstalk:[^:]+:([^:]*):platform/([^/]+)/(\d+\.\d+\.\d+)$')

    @staticmethod
    def is_valid_arn(arn):
        if not isinstance(arn, str):
            return False

        return PlatformVersion.ARN_PATTERN.match(arn) is not None

    @staticmethod
    def arn_to_platform(arn):
        # Example ARNS
        # (system)
        # arn:aws:elasticbeanstalk:us-east-1::platform/Name/1.0.0
        # (user)
        # arn:aws:elasticbeanstalk:us-east-1:00000000000:platform/Name/0.0.0
        match = PlatformVersion.ARN_PATTERN.match(arn)

        if not match:
            raise Exception("Unable to parse arn '%s'" % arn)

        account_id, platform_name, platform_version = match.group(1, 2, 3)
        return account_id, platform_name, platform_version

    @staticmethod
    def get_platform_version(arn):
        _, _, platform_version = PlatformVersion.arn_to_platform(arn)
        return platform_version

    @staticmethod
    def get_platform_name(arn):
        _, platform_name, _ = PlatformVersion.arn_to_platform(arn)
        return platform_name

    def __init__(self, arn):
        self.arn = arn
        account_id, platform_name, platform_version = PlatformVersion.arn_to_platform(arn)

        # For the sake of the CLI a version is the same thing as an ARN
        self.version = self.arn

        self.name = platform_name
        self.account_id = account_id
        self.platform_version = platform_version
        self.platform = platform_name

    def __str__(self):
        return self.version

    def __eq__(self, other):
        if not isinstance(other, PlatformVersion):
            return False

        return self.version == other.version

    def __ne__(self, other):
        return not self.__eq__(other)

    def has_healthd_group_version_2_support(self):
        if self.account_id == "AWSElasticBeanstalk":
            return  self.platform_version >= utils.parse_version('2.0.10')

        # Custom platforms always have access to Enhanced Health V2
        return True
