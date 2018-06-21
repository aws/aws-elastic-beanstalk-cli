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
import unittest

from ebcli.objects.solutionstack import SolutionStack


class TestSolutionStack(unittest.TestCase):
    maxDiff = None

    def test_platform_shorthand(self):
        solution_stack_platform_shorthand_mappings = {
            '64bit Amazon Linux 2017.09 v4.4.0 running Node.js': 'Node.js',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4': 'PHP 5.4',
            '64bit Amazon Linux running PHP 5.3': 'PHP 5.3',
            '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7': 'Python 2.7',
            '64bit Amazon Linux running Python': 'Python',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Puma)': 'Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Passenger Standalone)': 'Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3': 'Ruby 1.9.3',
            '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 8 Java 8': 'Tomcat 8 Java 8',
            '64bit Amazon Linux running Tomcat 7': 'Tomcat 7',
            '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0': 'IIS 10.0',
            '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5': 'IIS 8.5',
            '64bit Windows Server 2012 v1.2.0 running IIS 8': 'IIS 8',
            '64bit Windows Server 2008 R2 v1.2.0 running IIS 7.5': 'IIS 7.5',
            '64bit Windows Server Core 2012 R2 running IIS 8.5': 'IIS 8.5',
            '64bit Windows Server 2012 running IIS 8': 'IIS 8',
            '64bit Windows Server 2008 R2 running IIS 7.5': 'IIS 7.5',
            '64bit Amazon Linux 2017.09 v2.8.0 running Docker 17.06.2-ce': 'Docker 17.06.2-ce',
            '64bit Amazon Linux 2017.03 v2.6.0 running Docker 1.12.6': 'Docker 1.12.6',
            '64bit Amazon Linux 2017.03 v2.7.5 running Multi-container Docker 17.03.2-ce (Generic)': 'Multi-container Docker 17.03.2-ce (Generic)',
            '64bit Amazon Linux 2016.03 v2.1.6 running Multi-container Docker 1.11.2 (Generic)': 'Multi-container Docker 1.11.2 (Generic)',
            '64bit Debian jessie v2.8.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)': 'GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v2.8.0 running Go 1.4 (Preconfigured - Docker)': 'Go 1.4 (Preconfigured - Docker)',
            '64bit Debian jessie v2.8.0 running Python 3.4 (Preconfigured - Docker)': 'Python 3.4 (Preconfigured - Docker)',
            '64bit Amazon Linux 2017.09 v2.6.0 running Java 8': 'Java 8',
            '64bit Amazon Linux 2017.09 v2.7.1 running Go 1.9': 'Go 1.9',
            '64bit Amazon Linux 2017.09 v2.4.0 running Packer 1.0.3': 'Packer 1.0.3'
        }

        for solution_stack_name, expected_platform_shorthand in solution_stack_platform_shorthand_mappings.items():
            self.assertEqual(expected_platform_shorthand, SolutionStack(solution_stack_name).platform_shorthand)

    def test_language_name(self):
        solution_stack_language_name_mappings = {
            '64bit Amazon Linux 2017.09 v4.4.0 running Node.js': 'Node.js',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4': 'PHP',
            '64bit Amazon Linux running PHP 5.3': 'PHP',
            '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7': 'Python',
            '64bit Amazon Linux running Python': 'Python',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Puma)': 'Ruby',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Passenger Standalone)': 'Ruby',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3': 'Ruby',
            '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 8 Java 8': 'Tomcat',
            '64bit Amazon Linux running Tomcat 7': 'Tomcat',
            '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0': 'IIS',
            '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5': 'IIS',
            '64bit Windows Server 2012 v1.2.0 running IIS 8': 'IIS',
            '64bit Windows Server 2008 R2 v1.2.0 running IIS 7.5': 'IIS',
            '64bit Windows Server Core 2012 R2 running IIS 8.5': 'IIS',
            '64bit Windows Server 2012 running IIS 8': 'IIS',
            '64bit Windows Server 2008 R2 running IIS 7.5': 'IIS',
            '64bit Amazon Linux 2017.09 v2.8.0 running Docker 17.06.2-ce': 'Docker',
            '64bit Amazon Linux 2017.03 v2.6.0 running Docker 1.12.6': 'Docker',
            '64bit Amazon Linux 2017.03 v2.7.5 running Multi-container Docker 17.03.2-ce (Generic)': 'Multi-container Docker',
            '64bit Amazon Linux 2016.03 v2.1.6 running Multi-container Docker 1.11.2 (Generic)': 'Multi-container Docker',
            '64bit Debian jessie v2.8.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)': 'GlassFish',
            '64bit Debian jessie v2.8.0 running Go 1.4 (Preconfigured - Docker)': 'Go',
            '64bit Debian jessie v2.8.0 running Python 3.4 (Preconfigured - Docker)': 'Python',
            '64bit Amazon Linux 2017.09 v2.6.0 running Java 8': 'Java',
            '64bit Amazon Linux 2017.09 v2.7.1 running Go 1.9': 'Go',
            '64bit Amazon Linux 2017.09 v2.4.0 running Packer 1.0.3': 'Packer'
        }

        for solution_stack_name, expected_language_name in solution_stack_language_name_mappings.items():
            self.assertEqual(expected_language_name, SolutionStack(solution_stack_name).language_name)

    def test_language_version(self):
        solution_stack_language_version_mappings = {
            '64bit Amazon Linux 2017.09 v4.4.0 running Node.js': '0.0.1',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4': '5.4',
            '64bit Amazon Linux running PHP 5.3': '5.3',
            '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7': '2.7',
            '64bit Amazon Linux running Python': '0.0.1',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Puma)': '2.0',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Passenger Standalone)': '2.0',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3': '1.9.3',
            '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 8 Java 8': '8',
            '64bit Amazon Linux running Tomcat 7': '7',
            '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0': '10.0',
            '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5': '8.5',
            '64bit Windows Server 2012 v1.2.0 running IIS 8': '8',
            '64bit Windows Server 2008 R2 v1.2.0 running IIS 7.5': '7.5',
            '64bit Windows Server Core 2012 R2 running IIS 8.5': '8.5',
            '64bit Windows Server 2012 running IIS 8': '8',
            '64bit Windows Server 2008 R2 running IIS 7.5': '7.5',
            '64bit Amazon Linux 2017.09 v2.8.0 running Docker 17.06.2-ce': '17.6.2',
            '64bit Amazon Linux 2017.03 v2.6.0 running Docker 1.12.6': '1.12.6',
            '64bit Amazon Linux 2017.03 v2.7.5 running Multi-container Docker 17.03.2-ce (Generic)': '17.3.2',
            '64bit Amazon Linux 2016.03 v2.1.6 running Multi-container Docker 1.11.2 (Generic)': '1.11.2',
            '64bit Debian jessie v2.8.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)': '4.1',
            '64bit Debian jessie v2.8.0 running Go 1.4 (Preconfigured - Docker)': '1.4',
            '64bit Debian jessie v2.8.0 running Python 3.4 (Preconfigured - Docker)': '3.4',
            '64bit Amazon Linux 2017.09 v2.6.0 running Java 8': '8',
            '64bit Amazon Linux 2017.09 v2.7.1 running Go 1.9': '1.9',
            '64bit Amazon Linux 2017.09 v2.4.0 running Packer 1.0.3': '1.0.3'
        }

        for solution_stack_name, expected_language_version in solution_stack_language_version_mappings.items():
            self.assertEqual(
                expected_language_version,
                SolutionStack(solution_stack_name).language_version.public
            )

    def test_has_healthd_support(self):
        solution_stack_healthd_support_mappings = {
            '64bit Amazon Linux 2017.09 v4.4.0 running Node.js': True,
            '64bit Amazon Linux running PHP 5.3': False,
            '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7': False,
            '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0': False,
            '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5': False,
            '64bit Windows Server Core 2012 R2 running IIS 8.5': False,
            '64bit Amazon Linux 2015.09 v2.0.6 running Docker 1.7.1': True
        }

        for solution_stack_name, expected_healthd_support_result in solution_stack_healthd_support_mappings.items():
            self.assertEqual(
                expected_healthd_support_result,
                SolutionStack(solution_stack_name).has_healthd_support
            )

    def test_has_healthd_V2_support(self):
        solution_stack_healthd_support_mappings = {
            '64bit Amazon Linux 2017.09 v4.4.0 running Node.js': True,
            '64bit Amazon Linux running PHP 5.3': False,
            '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7': False,
            '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0': False,
            '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5': False,
            '64bit Windows Server Core 2012 R2 running IIS 8.5': False,
            '64bit Amazon Linux 2015.09 v2.0.6 running Docker 1.7.1': False
        }

        for solution_stack_name, expected_healthd_support_result in solution_stack_healthd_support_mappings.items():
            self.assertEqual(
                expected_healthd_support_result,
                SolutionStack(solution_stack_name).has_healthd_group_version_2_support
            )

    def test_os_bitness(self):
        solution_stack_os_bitness_mappings = {
            '64bit Amazon Linux 2017.09 v4.4.0 running Node.js': 64,
            '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7': 32
        }

        for solution_stack_name, expected_os_bitness in solution_stack_os_bitness_mappings.items():
            self.assertEqual(
                expected_os_bitness,
                SolutionStack(solution_stack_name).os_bitness
            )

    def test_operating_system_version(self):
        solution_stack_os_version_mappings = {
            '64bit Amazon Linux 2017.09 v4.4.0 running Node.js': '2017.9',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4': '2017.9',
            '64bit Amazon Linux running PHP 5.3': '0.1',
            '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7': '2014.3',
            '64bit Amazon Linux running Python': '0.1',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Puma)': '2014.3',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Passenger Standalone)': '2014.3',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3': '2014.3',
            '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 8 Java 8': '2017.9',
            '64bit Amazon Linux running Tomcat 7': '0.1',
            '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0': '0.1',
            '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5': '0.1',
            '64bit Windows Server 2012 v1.2.0 running IIS 8': '0.1',
            '64bit Windows Server 2008 R2 v1.2.0 running IIS 7.5': '0.1',
            '64bit Windows Server Core 2012 R2 running IIS 8.5': '0.1',
            '64bit Windows Server 2012 running IIS 8': '0.1',
            '64bit Windows Server 2008 R2 running IIS 7.5': '0.1',
            '64bit Amazon Linux 2017.09 v2.8.0 running Docker 17.06.2-ce': '2017.9',
            '64bit Amazon Linux 2017.03 v2.6.0 running Docker 1.12.6': '2017.3',
            '64bit Amazon Linux 2017.03 v2.7.5 running Multi-container Docker 17.03.2-ce (Generic)': '2017.3',
            '64bit Amazon Linux 2016.03 v2.1.6 running Multi-container Docker 1.11.2 (Generic)': '2016.3',
            '64bit Debian jessie v2.8.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)': '0.1',
            '64bit Debian jessie v2.8.0 running Go 1.4 (Preconfigured - Docker)': '0.1',
            '64bit Debian jessie v2.8.0 running Python 3.4 (Preconfigured - Docker)': '0.1',
            '64bit Amazon Linux 2017.09 v2.6.0 running Java 8': '2017.9',
            '64bit Amazon Linux 2017.09 v2.7.1 running Go 1.9': '2017.9',
            '64bit Amazon Linux 2017.09 v2.4.0 running Packer 1.0.3': '2017.9'
        }

        for solution_stack_name, expected_os_version in solution_stack_os_version_mappings.items():
            self.assertEqual(
                expected_os_version,
                str(SolutionStack(solution_stack_name).operating_system_version)
            )

    def test_platform_version(self):
        solution_stack_platform_version_mappings = {
            '64bit Amazon Linux 2017.09 v4.4.0 running Node.js': '4.4.0',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4': '2.6.0',
            '64bit Amazon Linux running PHP 5.3': '0.0.1',
            '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7': '1.1.0',
            '64bit Amazon Linux running Python': '0.0.1',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Puma)': '1.1.0',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Passenger Standalone)': '1.1.0',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3': '1.1.0',
            '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 8 Java 8': '2.7.0',
            '64bit Amazon Linux running Tomcat 7': '0.0.1',
            '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0': '1.2.0',
            '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5': '1.2.0',
            '64bit Windows Server 2012 v1.2.0 running IIS 8': '1.2.0',
            '64bit Windows Server 2008 R2 v1.2.0 running IIS 7.5': '1.2.0',
            '64bit Windows Server Core 2012 R2 running IIS 8.5': '0.0.1',
            '64bit Windows Server 2012 running IIS 8': '0.0.1',
            '64bit Windows Server 2008 R2 running IIS 7.5': '0.0.1',
            '64bit Amazon Linux 2017.09 v2.8.0 running Docker 17.06.2-ce': '2.8.0',
            '64bit Amazon Linux 2017.03 v2.6.0 running Docker 1.12.6': '2.6.0',
            '64bit Amazon Linux 2017.03 v2.7.5 running Multi-container Docker 17.03.2-ce (Generic)': '2.7.5',
            '64bit Amazon Linux 2016.03 v2.1.6 running Multi-container Docker 1.11.2 (Generic)': '2.1.6',
            '64bit Debian jessie v2.8.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)': '2.8.0',
            '64bit Debian jessie v2.8.0 running Go 1.4 (Preconfigured - Docker)': '2.8.0',
            '64bit Debian jessie v2.8.0 running Python 3.4 (Preconfigured - Docker)': '2.8.0',
            '64bit Amazon Linux 2017.09 v2.6.0 running Java 8': '2.6.0',
            '64bit Amazon Linux 2017.09 v2.7.1 running Go 1.9': '2.7.1',
            '64bit Amazon Linux 2017.09 v2.4.0 running Packer 1.0.3': '2.4.0'
        }

        for solution_stack_name, expected_platform_version in solution_stack_platform_version_mappings.items():
            self.assertEqual(
                expected_platform_version,
                SolutionStack(solution_stack_name).platform_version.public
            )

    def test_json_to_solution_stack_array(self):
        solution_stack_platform_shorthand_mappings = {
            '64bit Amazon Linux 2017.09 v4.4.0 running Node.js': 'Node.js',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4': 'PHP 5.4',
            '64bit Amazon Linux running PHP 5.3': 'PHP 5.3',
            '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7': 'Python 2.7',
            '64bit Amazon Linux running Python': 'Python',
        }

        self.assertEqual(
            list(solution_stack_platform_shorthand_mappings.values()),
            [s.platform_shorthand for s in SolutionStack.json_to_solution_stack_array(solution_stack_platform_shorthand_mappings)]
        )

    def test_group_solution_stacks_by_platform_shorthand(self):
        solution_stacks = [
            '64bit Amazon Linux 2017.09 v4.4.0 running Node.js',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 7.1',
            '64bit Amazon Linux 2017.03 v2.5.0 running PHP 7.1',
            '64bit Amazon Linux 2017.03 v2.4.4 running PHP 5.4',
            '64bit Amazon Linux running PHP 5.3',
            '32bit Amazon Linux running PHP 5.3',
            '64bit Amazon Linux 2017.09 v2.6.0 running Python 3.6',
            '64bit Amazon Linux 2017.09 v2.6.0 running Python 3.4',
            '64bit Amazon Linux 2017.03 v2.5.2 running Python 3.4',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.4 (Puma)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.4 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 1.9.3',
            '32bit Amazon Linux 2014.09 v1.2.0 running Ruby 1.9.3',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2017.03 v2.6.5 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7',
            '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0',
            '64bit Windows Server 2016 v1.2.0 running IIS 10.0',
            '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5',
            '64bit Windows Server 2012 R2 v1.2.0 running IIS 8.5',
            '64bit Windows Server 2012 v1.2.0 running IIS 8',
            '64bit Windows Server 2008 R2 v1.2.0 running IIS 7.5',
            '64bit Windows Server Core 2012 R2 running IIS 8.5',
            '64bit Windows Server 2012 R2 running IIS 8.5',
            '64bit Windows Server 2012 running IIS 8',
            '64bit Windows Server 2008 R2 running IIS 7.5',
            '64bit Amazon Linux 2017.03 v2.7.4 running Docker 17.03.2-ce',
            '64bit Amazon Linux 2017.03 v2.7.3 running Docker 17.03.1-ce',
            '64bit Debian jessie v2.8.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Amazon Linux 2017.09 v2.6.0 running Java 8',
            '64bit Amazon Linux 2017.03 v2.5.4 running Java 8',
            '64bit Amazon Linux 2017.09 v2.7.1 running Go 1.9',
            '64bit Amazon Linux 2017.03 v2.7.0 running Go 1.9',
            '64bit Amazon Linux 2017.09 v2.4.0 running Packer 1.0.3',
            '64bit Amazon Linux 2017.03 v2.3.1 running Packer 1.0.3'
        ]

        expected_platform_shorthand_solution_stack_name_mappings = [
            {
                'PlatformShorthand': 'Node.js',
                'SolutionStack': '64bit Amazon Linux 2017.09 v4.4.0 running Node.js'
            },
            {
                'PlatformShorthand': 'PHP 5.4',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4'
            },
            {
                'PlatformShorthand': 'PHP 7.1',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.6.0 running PHP 7.1'
            },
            {
                'PlatformShorthand': 'PHP 5.3',
                'SolutionStack': '64bit Amazon Linux running PHP 5.3'
            },
            {
                'PlatformShorthand': 'Python 3.6',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.6.0 running Python 3.6'
            },
            {
                'PlatformShorthand': 'Python 3.4',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.6.0 running Python 3.4'
            },
            {
                'PlatformShorthand': 'Ruby 2.4 (Puma)',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.4 (Puma)'
            },
            {
                'PlatformShorthand': 'Ruby 2.4 (Passenger Standalone)',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.4 (Passenger Standalone)'
            },
            {
                'PlatformShorthand': 'Ruby 1.9.3',
                'SolutionStack': '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 1.9.3'
            },
            {
                'PlatformShorthand': 'Ruby 2.1 (Puma)',
                'SolutionStack': '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Puma)'
            },
            {
                'PlatformShorthand': 'Tomcat 8 Java 8',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 8 Java 8'
            },
            {
                'PlatformShorthand': 'Tomcat 7 Java 7',
                'SolutionStack': '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7'
            },
            {
                'PlatformShorthand': 'IIS 10.0',
                'SolutionStack': '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0'
            },
            {
                'PlatformShorthand': 'IIS 8.5',
                'SolutionStack': '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5'
            },
            {
                'PlatformShorthand': 'IIS 8',
                'SolutionStack': '64bit Windows Server 2012 v1.2.0 running IIS 8'
            },
            {
                'PlatformShorthand': 'IIS 7.5',
                'SolutionStack': '64bit Windows Server 2008 R2 v1.2.0 running IIS 7.5'
            },
            {
                'PlatformShorthand': 'Docker 17.03.2-ce',
                'SolutionStack': '64bit Amazon Linux 2017.03 v2.7.4 running Docker 17.03.2-ce'
            },
            {
                'PlatformShorthand': 'Docker 17.03.1-ce',
                'SolutionStack': '64bit Amazon Linux 2017.03 v2.7.3 running Docker 17.03.1-ce'
            },
            {
                'PlatformShorthand': 'GlassFish 4.1 Java 8 (Preconfigured - Docker)',
                'SolutionStack': '64bit Debian jessie v2.8.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)'
            },
            {
                'PlatformShorthand': 'Java 8',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.6.0 running Java 8'
            },
            {
                'PlatformShorthand': 'Go 1.9',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.7.1 running Go 1.9'
            },
            {
                'PlatformShorthand': 'Packer 1.0.3',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.4.0 running Packer 1.0.3'
            }
        ]

        solution_stacks = [SolutionStack(s) for s in solution_stacks]
        grouped_solution_stacks = SolutionStack.group_solution_stacks_by_platform_shorthand(solution_stacks)

        self.assertEqual(
            [mapping['PlatformShorthand'] for mapping in expected_platform_shorthand_solution_stack_name_mappings],
            [solution_stack['PlatformShorthand'] for solution_stack in grouped_solution_stacks]
        )

        self.assertEqual(
            [mapping['SolutionStack'] for mapping in expected_platform_shorthand_solution_stack_name_mappings],
            [solution_stack['SolutionStack'] for solution_stack in grouped_solution_stacks]
        )

    def test_group_solution_stacks_by_language_name(self):
        solution_stacks = [
            '64bit Amazon Linux 2017.09 v4.4.0 running Node.js',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 7.1',
            '64bit Amazon Linux 2017.03 v2.5.0 running PHP 7.1',
            '64bit Amazon Linux 2017.03 v2.4.4 running PHP 5.4',
            '64bit Amazon Linux running PHP 5.3',
            '32bit Amazon Linux running PHP 5.3',
            '64bit Amazon Linux 2017.09 v2.6.0 running Python 3.6',
            '64bit Amazon Linux 2017.09 v2.6.0 running Python 3.4',
            '64bit Amazon Linux 2017.03 v2.5.2 running Python 3.4',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.4 (Puma)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.4 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 1.9.3',
            '32bit Amazon Linux 2014.09 v1.2.0 running Ruby 1.9.3',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2017.03 v2.6.5 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7',
            '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0',
            '64bit Windows Server 2016 v1.2.0 running IIS 10.0',
            '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5',
            '64bit Windows Server 2012 R2 v1.2.0 running IIS 8.5',
            '64bit Windows Server 2012 v1.2.0 running IIS 8',
            '64bit Windows Server 2008 R2 v1.2.0 running IIS 7.5',
            '64bit Windows Server Core 2012 R2 running IIS 8.5',
            '64bit Windows Server 2012 R2 running IIS 8.5',
            '64bit Windows Server 2012 running IIS 8',
            '64bit Windows Server 2008 R2 running IIS 7.5',
            '64bit Amazon Linux 2017.03 v2.7.4 running Docker 17.03.2-ce',
            '64bit Amazon Linux 2017.03 v2.7.3 running Docker 17.03.1-ce',
            '64bit Debian jessie v2.8.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Amazon Linux 2017.09 v2.6.0 running Java 8',
            '64bit Amazon Linux 2017.03 v2.5.4 running Java 8',
            '64bit Amazon Linux 2017.09 v2.7.1 running Go 1.9',
            '64bit Amazon Linux 2017.03 v2.7.0 running Go 1.9',
            '64bit Amazon Linux 2017.09 v2.4.0 running Packer 1.0.3',
            '64bit Amazon Linux 2017.03 v2.3.1 running Packer 1.0.3'
        ]

        expected_language_name_solution_stack_name_mappings = [
            {
                'LanguageName': 'Node.js',
                'SolutionStack': '64bit Amazon Linux 2017.09 v4.4.0 running Node.js'
            },
            {
                'LanguageName': 'PHP',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4'
            },
            {
                'LanguageName': 'Python',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.6.0 running Python 3.6'
            },
            {
                'LanguageName': 'Ruby',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.4 (Puma)'
            },
            {
                'LanguageName': 'Tomcat',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 8 Java 8'
            },
            {
                'LanguageName': 'IIS',
                'SolutionStack': '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0'
            },
            {
                'LanguageName': 'Docker',
                'SolutionStack': '64bit Amazon Linux 2017.03 v2.7.4 running Docker 17.03.2-ce'
            },
            {
                'LanguageName': 'GlassFish',
                'SolutionStack': '64bit Debian jessie v2.8.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            },
            {
                'LanguageName': 'Java',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.6.0 running Java 8'
            },
            {
                'LanguageName': 'Go',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.7.1 running Go 1.9'
            },
            {
                'LanguageName': 'Packer',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.4.0 running Packer 1.0.3'
            }
        ]

        solution_stacks = [SolutionStack(solution_stack) for solution_stack in solution_stacks]
        grouped_solution_stacks = SolutionStack.group_solution_stacks_by_language_name(solution_stacks)
        self.assertEqual(
            [mapping['LanguageName'] for mapping in expected_language_name_solution_stack_name_mappings],
            [solution_stack['LanguageName'] for solution_stack in grouped_solution_stacks]
        )
        self.assertEqual(
            [mapping['SolutionStack'] for mapping in expected_language_name_solution_stack_name_mappings],
            [solution_stack['SolutionStack'] for solution_stack in grouped_solution_stacks]
        )

    def test_solution_string_sorting(self):
        solution_stacks = [
            '64bit Amazon Linux 2017.09 v4.4.0 running Node.js',
            '64bit Amazon Linux 2017.03 v4.3.0 running Node.js',
            '64bit Amazon Linux 2017.03 v4.2.2 running Node.js',
            '64bit Amazon Linux 2017.03 v4.2.1 running Node.js',
            '64bit Amazon Linux 2017.03 v4.2.0 running Node.js',
            '64bit Amazon Linux 2017.03 v4.1.1 running Node.js',
            '64bit Amazon Linux 2017.03 v4.1.0 running Node.js',
            '64bit Amazon Linux 2015.03 v1.4.6 running Node.js',
            '64bit Amazon Linux 2015.03 v1.3.0 running Node.js',
            '64bit Amazon Linux 2014.09 v1.2.1 running Node.js',
            '32bit Amazon Linux 2014.09 v1.2.1 running Node.js',
            '64bit Amazon Linux 2014.03 v1.1.0 running Node.js',
            '32bit Amazon Linux 2014.03 v1.1.0 running Node.js',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.5',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.6',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 7.0',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 7.1',
            '64bit Amazon Linux 2017.03 v2.5.0 running PHP 5.4',
            '64bit Amazon Linux 2017.03 v2.5.0 running PHP 5.6',
            '64bit Amazon Linux 2017.03 v2.5.0 running PHP 7.1',
            '64bit Amazon Linux 2017.03 v2.4.4 running PHP 5.4',
            '64bit Amazon Linux 2017.03 v2.4.4 running PHP 5.6',
            '64bit Amazon Linux 2017.03 v2.4.4 running PHP 7.0',
            '64bit Amazon Linux 2017.03 v2.4.3 running PHP 5.6',
            '64bit Amazon Linux 2017.03 v2.4.2 running PHP 5.4',
            '64bit Amazon Linux 2017.03 v2.4.2 running PHP 5.6',
            '64bit Amazon Linux 2017.03 v2.4.1 running PHP 5.4',
            '64bit Amazon Linux 2017.03 v2.4.1 running PHP 5.5',
            '64bit Amazon Linux 2017.03 v2.4.1 running PHP 5.6',
            '64bit Amazon Linux 2017.03 v2.4.1 running PHP 7.0',
            '64bit Amazon Linux 2017.03 v2.4.0 running PHP 5.6',
            '64bit Amazon Linux 2016.09 v2.3.3 running PHP 7.0',
            '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.4',
            '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.5',
            '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.6',
            '64bit Amazon Linux 2016.03 v2.1.6 running PHP 7.0',
            '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.6',
            '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.5',
            '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.4',
            '64bit Amazon Linux 2015.03 v1.3.0 running PHP 5.5',
            '64bit Amazon Linux 2015.03 v1.3.0 running PHP 5.4',
            '64bit Amazon Linux 2014.09 v1.2.0 running PHP 5.5',
            '64bit Amazon Linux 2014.09 v1.2.0 running PHP 5.4',
            '32bit Amazon Linux 2014.09 v1.2.0 running PHP 5.5',
            '32bit Amazon Linux 2014.09 v1.2.0 running PHP 5.4',
            '64bit Amazon Linux 2014.03 v1.1.0 running PHP 5.5',
            '64bit Amazon Linux 2014.03 v1.1.0 running PHP 5.4',
            '32bit Amazon Linux 2014.03 v1.1.0 running PHP 5.5',
            '32bit Amazon Linux 2014.03 v1.1.0 running PHP 5.4',
            '64bit Amazon Linux running PHP 5.3',
            '32bit Amazon Linux running PHP 5.3',
            '64bit Amazon Linux 2017.09 v2.6.0 running Python 3.6',
            '64bit Amazon Linux 2017.09 v2.6.0 running Python 3.4',
            '64bit Amazon Linux 2017.09 v2.6.0 running Python',
            '64bit Amazon Linux 2017.09 v2.6.0 running Python 2.7',
            '64bit Amazon Linux 2017.03 v2.5.2 running Python 3.4',
            '64bit Amazon Linux 2017.03 v2.4.2 running Python 3.4',
            '64bit Amazon Linux 2017.03 v2.4.2 running Python',
            '64bit Amazon Linux 2017.03 v2.4.1 running Python 3.4',
            '64bit Amazon Linux 2017.03 v2.4.1 running Python',
            '64bit Amazon Linux 2017.03 v2.4.1 running Python 2.7',
            '64bit Amazon Linux 2017.03 v2.4.0 running Python',
            '64bit Amazon Linux 2016.09 v2.3.3 running Python',
            '64bit Amazon Linux 2015.03 v1.4.6 running Python 3.4',
            '64bit Amazon Linux 2015.03 v1.4.6 running Python 2.7',
            '64bit Amazon Linux 2015.03 v1.4.6 running Python',
            '64bit Amazon Linux 2015.03 v1.3.0 running Python 3.4',
            '64bit Amazon Linux 2015.03 v1.3.0 running Python 2.7',
            '64bit Amazon Linux 2015.03 v1.3.0 running Python',
            '64bit Amazon Linux 2014.09 v1.2.0 running Python 2.7',
            '64bit Amazon Linux 2014.09 v1.2.0 running Python',
            '32bit Amazon Linux 2014.09 v1.2.0 running Python 2.7',
            '32bit Amazon Linux 2014.09 v1.2.0 running Python',
            '64bit Amazon Linux 2014.03 v1.1.0 running Python 2.7',
            '64bit Amazon Linux 2014.03 v1.1.0 running Python',
            '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7',
            '32bit Amazon Linux 2014.03 v1.1.0 running Python',
            '64bit Amazon Linux running Python',
            '32bit Amazon Linux running Python',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.4 (Puma)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.3 (Puma)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.2 (Puma)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.4 (Passenger Standalone)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.3 (Passenger Standalone)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.2 (Passenger Standalone)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 1.9.3',
            '64bit Amazon Linux 2017.09 v2.6.0 running Ruby 2.4 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.3 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.3 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.2 running Ruby 2.3 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.2 running Ruby 2.3 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 2.3 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 2.2 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 2.3 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 2.2 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 1.9.3',
            '64bit Amazon Linux 2017.03 v2.4.0 running Ruby 2.3 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.0 running Ruby 2.3 (Passenger Standalone)',
            '64bit Amazon Linux 2016.09 v2.3.3 running Ruby 2.3 (Puma)',
            '64bit Amazon Linux 2016.09 v2.3.3 running Ruby 2.3 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.2 (Puma)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.2 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 1.9.3',
            '64bit Amazon Linux 2015.03 v1.3.0 running Ruby 2.2 (Puma)',
            '64bit Amazon Linux 2015.03 v1.3.0 running Ruby 2.2 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.3.0 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2015.03 v1.3.0 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.3.0 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2015.03 v1.3.0 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.3.0 running Ruby 1.9.3',
            '64bit Amazon Linux 2014.09 v1.2.1 running Ruby 2.2 (Puma)',
            '64bit Amazon Linux 2014.09 v1.2.1 running Ruby 2.2 (Passenger Standalone)',
            '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 1.9.3',
            '32bit Amazon Linux 2014.09 v1.2.0 running Ruby 1.9.3',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3',
            '32bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3',
            '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 7 Java 6',
            '64bit Amazon Linux 2017.03 v2.6.5 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2017.03 v2.6.4 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2017.03 v2.6.3 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2017.03 v2.6.1 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2017.03 v2.6.1 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2017.03 v2.6.1 running Tomcat 7 Java 6',
            '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 7 Java 6',
            '64bit Amazon Linux 2015.03 v1.3.0 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2015.03 v1.3.0 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2015.03 v1.3.0 running Tomcat 7 Java 6',
            '64bit Amazon Linux 2014.09 v1.2.0 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 6',
            '32bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 7',
            '32bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 6',
            '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 6',
            '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7',
            '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 6',
            '64bit Amazon Linux running Tomcat 7',
            '64bit Amazon Linux running Tomcat 6',
            '32bit Amazon Linux running Tomcat 7',
            '32bit Amazon Linux running Tomcat 6',
            '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0',
            '64bit Windows Server 2016 v1.2.0 running IIS 10.0',
            '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5',
            '64bit Windows Server 2012 R2 v1.2.0 running IIS 8.5',
            '64bit Windows Server 2012 v1.2.0 running IIS 8',
            '64bit Windows Server 2008 R2 v1.2.0 running IIS 7.5',
            '64bit Windows Server Core 2012 R2 running IIS 8.5',
            '64bit Windows Server 2012 R2 running IIS 8.5',
            '64bit Windows Server 2012 running IIS 8',
            '64bit Windows Server 2008 R2 running IIS 7.5',
            '64bit Amazon Linux 2017.09 v2.8.0 running Docker 17.06.2-ce',
            '64bit Amazon Linux 2017.03 v2.7.4 running Docker 17.03.2-ce',
            '64bit Amazon Linux 2017.03 v2.7.3 running Docker 17.03.1-ce',
            '64bit Amazon Linux 2017.03 v2.7.0 running Docker 17.03.1-ce',
            '64bit Amazon Linux 2017.03 v2.6.0 running Docker 1.12.6',
            '64bit Amazon Linux 2016.09 v2.3.0 running Docker 1.11.2',
            '64bit Amazon Linux 2016.03 v2.1.6 running Docker 1.11.2',
            '64bit Amazon Linux 2016.03 v2.1.0 running Docker 1.9.1',
            '64bit Amazon Linux 2015.09 v2.0.6 running Docker 1.7.1',
            '64bit Amazon Linux 2015.03 v1.4.6 running Docker 1.6.2',
            '64bit Amazon Linux 2014.09 v1.2.1 running Docker 1.5.0',
            '64bit Amazon Linux 2017.03 v2.7.5 running Multi-container Docker 17.03.2-ce (Generic)',
            '64bit Amazon Linux 2017.03 v2.7.1 running Multi-container Docker 17.03.1-ce (Generic)',
            '64bit Amazon Linux 2017.03 v2.7.0 running Multi-container Docker 17.03.1-ce (Generic)',
            '64bit Amazon Linux 2016.03 v2.1.6 running Multi-container Docker 1.11.2 (Generic)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Multi-container Docker 1.6.2 (Generic)',
            '64bit Debian jessie v2.8.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v2.8.0 running GlassFish 4.0 Java 7 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.0 running GlassFish 4.0 Java 7 (Preconfigured - Docker)',
            '64bit Debian jessie v2.6.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running GlassFish 4.0 Java 7 (Preconfigured - Docker)',
            '64bit Debian jessie v1.2.1 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v1.2.1 running GlassFish 4.0 Java 7 (Preconfigured - Docker)',
            '64bit Debian jessie v2.8.0 running Go 1.4 (Preconfigured - Docker)',
            '64bit Debian jessie v2.8.0 running Go 1.3 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.0 running Go 1.4 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.0 running Go 1.3 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running Go 1.4 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running Go 1.3 (Preconfigured - Docker)',
            '64bit Debian jessie v1.2.1 running Go 1.4 (Preconfigured - Docker)',
            '64bit Debian jessie v1.2.1 running Go 1.3 (Preconfigured - Docker)',
            '64bit Debian jessie v2.8.0 running Python 3.4 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.0 running Python 3.4 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running Python 3.4 (Preconfigured - Docker)',
            '64bit Debian jessie v1.2.1 running Python 3.4 (Preconfigured - Docker)',
            '64bit Amazon Linux 2017.09 v2.6.0 running Java 8',
            '64bit Amazon Linux 2017.09 v2.6.0 running Java 7',
            '64bit Amazon Linux 2017.03 v2.5.4 running Java 8',
            '64bit Amazon Linux 2017.03 v2.5.3 running Java 8',
            '64bit Amazon Linux 2017.03 v2.5.2 running Java 8',
            '64bit Amazon Linux 2017.03 v2.5.1 running Java 8',
            '64bit Amazon Linux 2017.03 v2.5.1 running Java 7',
            '64bit Amazon Linux 2017.09 v2.7.1 running Go 1.9',
            '64bit Amazon Linux 2017.03 v2.7.0 running Go 1.9',
            '64bit Amazon Linux 2017.03 v2.6.1 running Go 1.8',
            '64bit Amazon Linux 2017.03 v2.6.0 running Go 1.8',
            '64bit Amazon Linux 2017.03 v2.4.2 running Go 1.7',
            '64bit Amazon Linux 2016.09 v2.3.3 running Go 1.6',
            '64bit Amazon Linux 2016.09 v2.3.0 running Go 1.5',
            '64bit Amazon Linux 2016.03 v2.1.0 running Go 1.4',
            '64bit Amazon Linux 2017.09 v2.4.0 running Packer 1.0.3',
            '64bit Amazon Linux 2017.03 v2.3.1 running Packer 1.0.3',
            '64bit Amazon Linux 2017.03 v2.2.2 running Packer 1.0.0'
        ]

        expected_sorted_list = [
            '64bit Amazon Linux 2017.09 v4.4.0 running Node.js',
            '64bit Amazon Linux 2017.03 v4.3.0 running Node.js',
            '64bit Amazon Linux 2017.03 v4.2.2 running Node.js',
            '64bit Amazon Linux 2017.03 v4.2.1 running Node.js',
            '64bit Amazon Linux 2017.03 v4.2.0 running Node.js',
            '64bit Amazon Linux 2017.03 v4.1.1 running Node.js',
            '64bit Amazon Linux 2017.03 v4.1.0 running Node.js',
            '64bit Amazon Linux 2015.03 v1.4.6 running Node.js',
            '64bit Amazon Linux 2015.03 v1.3.0 running Node.js',
            '64bit Amazon Linux 2014.09 v1.2.1 running Node.js',
            '32bit Amazon Linux 2014.09 v1.2.1 running Node.js',
            '64bit Amazon Linux 2014.03 v1.1.0 running Node.js',
            '32bit Amazon Linux 2014.03 v1.1.0 running Node.js',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 7.1',
            '64bit Amazon Linux 2017.03 v2.5.0 running PHP 7.1',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 7.0',
            '64bit Amazon Linux 2017.03 v2.4.4 running PHP 7.0',
            '64bit Amazon Linux 2017.03 v2.4.1 running PHP 7.0',
            '64bit Amazon Linux 2016.09 v2.3.3 running PHP 7.0',
            '64bit Amazon Linux 2016.03 v2.1.6 running PHP 7.0',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.6',
            '64bit Amazon Linux 2017.03 v2.5.0 running PHP 5.6',
            '64bit Amazon Linux 2017.03 v2.4.4 running PHP 5.6',
            '64bit Amazon Linux 2017.03 v2.4.3 running PHP 5.6',
            '64bit Amazon Linux 2017.03 v2.4.2 running PHP 5.6',
            '64bit Amazon Linux 2017.03 v2.4.1 running PHP 5.6',
            '64bit Amazon Linux 2017.03 v2.4.0 running PHP 5.6',
            '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.6',
            '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.6',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.5',
            '64bit Amazon Linux 2017.03 v2.4.1 running PHP 5.5',
            '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.5',
            '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.5',
            '64bit Amazon Linux 2015.03 v1.3.0 running PHP 5.5',
            '64bit Amazon Linux 2014.09 v1.2.0 running PHP 5.5',
            '32bit Amazon Linux 2014.09 v1.2.0 running PHP 5.5',
            '64bit Amazon Linux 2014.03 v1.1.0 running PHP 5.5',
            '32bit Amazon Linux 2014.03 v1.1.0 running PHP 5.5',
            '64bit Amazon Linux 2017.09 v2.6.0 running PHP 5.4',
            '64bit Amazon Linux 2017.03 v2.5.0 running PHP 5.4',
            '64bit Amazon Linux 2017.03 v2.4.4 running PHP 5.4',
            '64bit Amazon Linux 2017.03 v2.4.2 running PHP 5.4',
            '64bit Amazon Linux 2017.03 v2.4.1 running PHP 5.4',
            '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.4',
            '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.4',
            '64bit Amazon Linux 2015.03 v1.3.0 running PHP 5.4',
            '64bit Amazon Linux 2014.09 v1.2.0 running PHP 5.4',
            '32bit Amazon Linux 2014.09 v1.2.0 running PHP 5.4',
            '64bit Amazon Linux 2014.03 v1.1.0 running PHP 5.4',
            '32bit Amazon Linux 2014.03 v1.1.0 running PHP 5.4',
            '64bit Amazon Linux running PHP 5.3',
            '32bit Amazon Linux running PHP 5.3',
            '64bit Amazon Linux 2017.09 v2.6.0 running Python 3.6',
            '64bit Amazon Linux 2017.09 v2.6.0 running Python 3.4',
            '64bit Amazon Linux 2017.03 v2.5.2 running Python 3.4',
            '64bit Amazon Linux 2017.03 v2.4.2 running Python 3.4',
            '64bit Amazon Linux 2017.03 v2.4.1 running Python 3.4',
            '64bit Amazon Linux 2015.03 v1.4.6 running Python 3.4',
            '64bit Amazon Linux 2015.03 v1.3.0 running Python 3.4',
            '64bit Debian jessie v2.8.0 running Python 3.4 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.0 running Python 3.4 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running Python 3.4 (Preconfigured - Docker)',
            '64bit Debian jessie v1.2.1 running Python 3.4 (Preconfigured - Docker)',
            '64bit Amazon Linux 2017.09 v2.6.0 running Python 2.7',
            '64bit Amazon Linux 2017.03 v2.4.1 running Python 2.7',
            '64bit Amazon Linux 2015.03 v1.4.6 running Python 2.7',
            '64bit Amazon Linux 2015.03 v1.3.0 running Python 2.7',
            '64bit Amazon Linux 2014.09 v1.2.0 running Python 2.7',
            '32bit Amazon Linux 2014.09 v1.2.0 running Python 2.7',
            '64bit Amazon Linux 2014.03 v1.1.0 running Python 2.7',
            '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7',
            '64bit Amazon Linux 2017.09 v2.6.0 running Python',
            '64bit Amazon Linux 2017.03 v2.4.2 running Python',
            '64bit Amazon Linux 2017.03 v2.4.1 running Python',
            '64bit Amazon Linux 2017.03 v2.4.0 running Python',
            '64bit Amazon Linux 2016.09 v2.3.3 running Python',
            '64bit Amazon Linux 2015.03 v1.4.6 running Python',
            '64bit Amazon Linux 2015.03 v1.3.0 running Python',
            '64bit Amazon Linux 2014.09 v1.2.0 running Python',
            '32bit Amazon Linux 2014.09 v1.2.0 running Python',
            '64bit Amazon Linux 2014.03 v1.1.0 running Python',
            '32bit Amazon Linux 2014.03 v1.1.0 running Python',
            '64bit Amazon Linux running Python',
            '32bit Amazon Linux running Python',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.4 (Puma)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.4 (Passenger Standalone)',
            '64bit Amazon Linux 2017.09 v2.6.0 running Ruby 2.4 (Passenger Standalone)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.3 (Puma)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.3 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.3 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.3 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.2 running Ruby 2.3 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.2 running Ruby 2.3 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 2.3 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 2.3 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.0 running Ruby 2.3 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.0 running Ruby 2.3 (Passenger Standalone)',
            '64bit Amazon Linux 2016.09 v2.3.3 running Ruby 2.3 (Puma)',
            '64bit Amazon Linux 2016.09 v2.3.3 running Ruby 2.3 (Passenger Standalone)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.2 (Puma)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.2 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 2.2 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 2.2 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.2 (Puma)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.2 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.3.0 running Ruby 2.2 (Puma)',
            '64bit Amazon Linux 2015.03 v1.3.0 running Ruby 2.2 (Passenger Standalone)',
            '64bit Amazon Linux 2014.09 v1.2.1 running Ruby 2.2 (Puma)',
            '64bit Amazon Linux 2014.09 v1.2.1 running Ruby 2.2 (Passenger Standalone)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.3.0 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2015.03 v1.3.0 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.3.0 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2015.03 v1.3.0 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 1.9.3',
            '64bit Amazon Linux 2017.03 v2.4.1 running Ruby 1.9.3',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 1.9.3',
            '64bit Amazon Linux 2015.03 v1.3.0 running Ruby 1.9.3',
            '64bit Amazon Linux 2014.09 v1.2.0 running Ruby 1.9.3',
            '32bit Amazon Linux 2014.09 v1.2.0 running Ruby 1.9.3',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3',
            '32bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3',
            '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2017.03 v2.6.5 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2017.03 v2.6.4 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2017.03 v2.6.3 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2017.03 v2.6.1 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2015.03 v1.3.0 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2014.09 v1.2.0 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2017.03 v2.6.1 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2015.03 v1.3.0 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 7',
            '32bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7',
            '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 7 Java 6',
            '64bit Amazon Linux 2017.03 v2.6.1 running Tomcat 7 Java 6',
            '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 7 Java 6',
            '64bit Amazon Linux 2015.03 v1.3.0 running Tomcat 7 Java 6',
            '64bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 6',
            '32bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 6',
            '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 6',
            '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 6',
            '64bit Amazon Linux running Tomcat 7',
            '32bit Amazon Linux running Tomcat 7',
            '64bit Amazon Linux running Tomcat 6',
            '32bit Amazon Linux running Tomcat 6',
            '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0',
            '64bit Windows Server 2016 v1.2.0 running IIS 10.0',
            '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5',
            '64bit Windows Server 2012 R2 v1.2.0 running IIS 8.5',
            '64bit Windows Server Core 2012 R2 running IIS 8.5',
            '64bit Windows Server 2012 R2 running IIS 8.5',
            '64bit Windows Server 2012 v1.2.0 running IIS 8',
            '64bit Windows Server 2012 running IIS 8',
            '64bit Windows Server 2008 R2 v1.2.0 running IIS 7.5',
            '64bit Windows Server 2008 R2 running IIS 7.5',
            '64bit Amazon Linux 2017.09 v2.8.0 running Docker 17.06.2-ce',
            '64bit Amazon Linux 2017.03 v2.7.4 running Docker 17.03.2-ce',
            '64bit Amazon Linux 2017.03 v2.7.3 running Docker 17.03.1-ce',
            '64bit Amazon Linux 2017.03 v2.7.0 running Docker 17.03.1-ce',
            '64bit Amazon Linux 2017.03 v2.6.0 running Docker 1.12.6',
            '64bit Amazon Linux 2016.09 v2.3.0 running Docker 1.11.2',
            '64bit Amazon Linux 2016.03 v2.1.6 running Docker 1.11.2',
            '64bit Amazon Linux 2016.03 v2.1.0 running Docker 1.9.1',
            '64bit Amazon Linux 2015.09 v2.0.6 running Docker 1.7.1',
            '64bit Amazon Linux 2015.03 v1.4.6 running Docker 1.6.2',
            '64bit Amazon Linux 2014.09 v1.2.1 running Docker 1.5.0',
            '64bit Amazon Linux 2017.03 v2.7.5 running Multi-container Docker 17.03.2-ce (Generic)',
            '64bit Amazon Linux 2017.03 v2.7.1 running Multi-container Docker 17.03.1-ce (Generic)',
            '64bit Amazon Linux 2017.03 v2.7.0 running Multi-container Docker 17.03.1-ce (Generic)',
            '64bit Amazon Linux 2016.03 v2.1.6 running Multi-container Docker 1.11.2 (Generic)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Multi-container Docker 1.6.2 (Generic)',
            '64bit Debian jessie v2.8.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v2.6.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v1.2.1 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v2.8.0 running GlassFish 4.0 Java 7 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.0 running GlassFish 4.0 Java 7 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running GlassFish 4.0 Java 7 (Preconfigured - Docker)',
            '64bit Debian jessie v1.2.1 running GlassFish 4.0 Java 7 (Preconfigured - Docker)',
            '64bit Amazon Linux 2017.09 v2.7.1 running Go 1.9',
            '64bit Amazon Linux 2017.03 v2.7.0 running Go 1.9',
            '64bit Amazon Linux 2017.03 v2.6.1 running Go 1.8',
            '64bit Amazon Linux 2017.03 v2.6.0 running Go 1.8',
            '64bit Amazon Linux 2017.03 v2.4.2 running Go 1.7',
            '64bit Amazon Linux 2016.09 v2.3.3 running Go 1.6',
            '64bit Amazon Linux 2016.09 v2.3.0 running Go 1.5',
            '64bit Amazon Linux 2016.03 v2.1.0 running Go 1.4',
            '64bit Debian jessie v2.8.0 running Go 1.4 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.0 running Go 1.4 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running Go 1.4 (Preconfigured - Docker)',
            '64bit Debian jessie v1.2.1 running Go 1.4 (Preconfigured - Docker)',
            '64bit Debian jessie v2.8.0 running Go 1.3 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.0 running Go 1.3 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running Go 1.3 (Preconfigured - Docker)',
            '64bit Debian jessie v1.2.1 running Go 1.3 (Preconfigured - Docker)',
            '64bit Amazon Linux 2017.09 v2.6.0 running Java 8',
            '64bit Amazon Linux 2017.03 v2.5.4 running Java 8',
            '64bit Amazon Linux 2017.03 v2.5.3 running Java 8',
            '64bit Amazon Linux 2017.03 v2.5.2 running Java 8',
            '64bit Amazon Linux 2017.03 v2.5.1 running Java 8',
            '64bit Amazon Linux 2017.09 v2.6.0 running Java 7',
            '64bit Amazon Linux 2017.03 v2.5.1 running Java 7',
            '64bit Amazon Linux 2017.09 v2.4.0 running Packer 1.0.3',
            '64bit Amazon Linux 2017.03 v2.3.1 running Packer 1.0.3',
            '64bit Amazon Linux 2017.03 v2.2.2 running Packer 1.0.0'
        ]

        self.assertEqual(
            expected_sorted_list,
            [s.name for s in sorted(SolutionStack.json_to_solution_stack_array(solution_stacks))]
        )
