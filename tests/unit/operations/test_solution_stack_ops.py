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
import os
import shutil
import yaml

import mock
import unittest

from ebcli.objects.solutionstack import SolutionStack
from ebcli.operations import solution_stack_ops
from ebcli.operations.platformops import PlatformVersion


class TestSolutionstackOps(unittest.TestCase):

    @mock.patch('ebcli.lib.elasticbeanstalk.get_available_solution_stacks')
    @mock.patch('ebcli.operations.platformops.list_custom_platform_versions')
    def test_find_solution_stack_from_string(
            self,
            custom_platforms_lister_mock,
            solution_stack_lister_mock
    ):
        solution_strings = [
            'docker-1.11.2',
            'docker-1.12.6',
            'docker-1.6.2',
            'docker-1.7.1',
            'docker-1.9.1',
            'docker-17.03.1-ce',
            'glassfish-4.0-java-7-(preconfigured-docker)',
            'glassfish-4.1-java-8-(preconfigured-docker)',
            'go-1.3-(preconfigured-docker)',
            'go-1.4',
            'go-1.4-(preconfigured-docker)',
            'go-1.5',
            'go-1.6',
            'go-1.8',
            'iis-10.0',
            'iis-7.5',
            'iis-8',
            'iis-8.5',
            'java-7',
            'java-8',
            'multi-container-docker-1.11.2-(generic)',
            'multi-container-docker-1.6.2-(generic)',
            'multi-container-docker-1.9.1-(generic)',
            'multi-container-docker-17.03.1-ce-(generic)',
            'node.js',
            'packer-1.0.0',
            'packer-1.0.3',
            'php-5.3',
            'php-5.4',
            'php-5.5',
            'php-5.6',
            'php-7.0',
            'python',
            'python-2.7',
            'python-3.4',
            'python-3.4-(preconfigured-docker)',
            'ruby-1.9.3',
            'ruby-2.0-(passenger-standalone)',
            'ruby-2.0-(puma)',
            'ruby-2.1-(passenger-standalone)',
            'ruby-2.1-(puma)',
            'ruby-2.2-(passenger-standalone)',
            'ruby-2.2-(puma)',
            'ruby-2.3-(passenger-standalone)',
            'ruby-2.3-(puma)',
            'tomcat-6',
            'tomcat-7',
            'tomcat-7-java-6',
            'tomcat-7-java-7',
            'tomcat-8-java-8',

            'Node.js',
            'PHP',
            'Python',
            'Ruby',
            'Tomcat',
            'IIS',
            'Docker',
            'Multi-container Docker',
            'Glassfish',
            'Go',
            'Java',
            'Packer',

            '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0',
            '64bit Windows Server 2016 v1.2.0 running IIS 10.0',
            '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5',
            '64bit Windows Server 2012 R2 v1.2.0 running IIS 8.5',
            '64bit Windows Server 2012 v1.2.0 running IIS 8',
            '64bit Windows Server 2008 R2 v1.2.0 running IIS 7.5',
            '64bit Amazon Linux 2017.03 v2.5.3 running Java 8',
            '64bit Amazon Linux 2017.03 v2.5.3 running Java 7',
            '64bit Amazon Linux 2017.03 v4.2.1 running Node.js',
            '64bit Amazon Linux 2017.03 v4.2.0 running Node.js',
            '64bit Amazon Linux 2017.03 v4.1.1 running Node.js',
            '64bit Amazon Linux 2015.09 v2.0.8 running Node.js',
            '64bit Amazon Linux 2015.03 v1.4.6 running Node.js',
            '64bit Amazon Linux 2014.03 v1.1.0 running Node.js',
            '32bit Amazon Linux 2014.03 v1.1.0 running Node.js',
            '64bit Amazon Linux 2017.03 v2.4.3 running PHP 5.4',
            '64bit Amazon Linux 2017.03 v2.4.3 running PHP 5.5',
            '64bit Amazon Linux 2017.03 v2.4.3 running PHP 5.6',
            '64bit Amazon Linux 2017.03 v2.4.3 running PHP 7.0',
            '64bit Amazon Linux 2017.03 v2.4.2 running PHP 5.4',
            '64bit Amazon Linux 2017.03 v2.4.2 running PHP 5.6',
            '64bit Amazon Linux 2017.03 v2.4.2 running PHP 7.0',
            '64bit Amazon Linux 2017.03 v2.4.1 running PHP 5.6',
            '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.4',
            '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.5',
            '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.6',
            '64bit Amazon Linux 2016.03 v2.1.6 running PHP 7.0',
            '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.6',
            '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.5',
            '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.4',
            '64bit Amazon Linux 2014.03 v1.1.0 running PHP 5.5',
            '64bit Amazon Linux 2014.03 v1.1.0 running PHP 5.4',
            '32bit Amazon Linux 2014.03 v1.1.0 running PHP 5.5',
            '32bit Amazon Linux 2014.03 v1.1.0 running PHP 5.4',
            '64bit Amazon Linux running PHP 5.3',
            '32bit Amazon Linux running PHP 5.3',
            '64bit Amazon Linux 2017.03 v2.5.0 running Python 3.4',
            '64bit Amazon Linux 2017.03 v2.5.0 running Python',
            '64bit Amazon Linux 2017.03 v2.5.0 running Python 2.7',
            '64bit Amazon Linux 2015.03 v1.4.6 running Python 3.4',
            '64bit Amazon Linux 2015.03 v1.4.6 running Python 2.7',
            '64bit Amazon Linux 2015.03 v1.4.6 running Python',
            '64bit Amazon Linux 2014.03 v1.1.0 running Python 2.7',
            '64bit Amazon Linux 2014.03 v1.1.0 running Python',
            '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7',
            '32bit Amazon Linux 2014.03 v1.1.0 running Python',
            '64bit Amazon Linux running Python',
            '32bit Amazon Linux running Python',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.3 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.2 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.3 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.2 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 1.9.3',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.2 (Puma)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.2 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 1.9.3',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3',
            '32bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3',
            '64bit Amazon Linux 2017.03 v2.6.3 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2017.03 v2.6.3 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2017.03 v2.6.3 running Tomcat 7 Java 6',
            '64bit Amazon Linux 2017.03 v2.6.1 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 7 Java 6',
            '64bit Amazon Linux 2015.03 v1.4.4 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 6',
            '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7',
            '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 6',
            '64bit Amazon Linux running Tomcat 7',
            '64bit Amazon Linux running Tomcat 6',
            '32bit Amazon Linux running Tomcat 7',
            '32bit Amazon Linux running Tomcat 6',
            '64bit Windows Server Core 2012 R2 running IIS 8.5',
            '64bit Windows Server 2012 R2 running IIS 8.5',
            '64bit Windows Server 2012 running IIS 8',
            '64bit Windows Server 2008 R2 running IIS 7.5',
            '64bit Amazon Linux 2017.03 v2.7.2 running Docker 17.03.1-ce',
            '64bit Amazon Linux 2017.03 v2.7.1 running Docker 17.03.1-ce',
            '64bit Amazon Linux 2017.03 v2.6.0 running Docker 1.12.6',
            '64bit Amazon Linux 2016.09 v2.3.0 running Docker 1.11.2',
            '64bit Amazon Linux 2016.03 v2.1.6 running Docker 1.11.2',
            '64bit Amazon Linux 2016.03 v2.1.0 running Docker 1.9.1',
            '64bit Amazon Linux 2015.09 v2.0.6 running Docker 1.7.1',
            '64bit Amazon Linux 2015.03 v1.4.6 running Docker 1.6.2',
            '64bit Amazon Linux 2017.03 v2.7.3 running Multi-container Docker 17.03.1-ce (Generic)',
            '64bit Amazon Linux 2016.03 v2.1.6 running Multi-container Docker 1.11.2 (Generic)',
            '64bit Amazon Linux 2016.03 v2.1.0 running Multi-container Docker 1.9.1 (Generic)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Multi-container Docker 1.6.2 (Generic)',
            '64bit Debian jessie v2.7.2 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.2 running GlassFish 4.0 Java 7 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running GlassFish 4.0 Java 7 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.2 running Go 1.4 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.2 running Go 1.3 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running Go 1.4 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running Go 1.3 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.2 running Python 3.4 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running Python 3.4 (Preconfigured - Docker)',
            '64bit Amazon Linux 2017.03 v2.5.1 running Go 1.8',
            '64bit Amazon Linux 2016.09 v2.3.3 running Go 1.6',
            '64bit Amazon Linux 2016.09 v2.3.0 running Go 1.5',
            '64bit Amazon Linux 2016.03 v2.1.0 running Go 1.4',
            '64bit Amazon Linux 2017.03 v2.3.1 running Packer 1.0.3',
            '64bit Amazon Linux 2017.03 v2.2.2 running Packer 1.0.0',

            'Node.js',
            'PHP 5.6',
            'PHP 5.3',
            'Python 3.4',
            'Python',
            'Ruby 2.3 (Puma)',
            'Ruby 2.3 (Passenger Standalone)',
            'Tomcat 8 Java 8',
            'Tomcat 7',
            'IIS 8.5',
            'IIS 8.5',
            'IIS 8',
            'Docker 1.12.6',
            'Multi-container Docker 17.03.1-ce (Generic)',
            'Multi-container Docker 1.11.2 (Generic)',
            'GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            'Go 1.4 (Preconfigured - Docker)',
            'Python 3.4 (Preconfigured - Docker)',
            'Java 8',
            'Java 7',
            'Go 1.8',
            'Go 1.6',
            'Go 1.5',
            'Go 1.4',
            'Packer 1.0.0',
        ]
        solution_stacks = [
            '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0',
            '64bit Windows Server 2016 v1.2.0 running IIS 10.0',
            '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5',
            '64bit Windows Server 2012 R2 v1.2.0 running IIS 8.5',
            '64bit Windows Server 2012 v1.2.0 running IIS 8',
            '64bit Windows Server 2008 R2 v1.2.0 running IIS 7.5',
            '64bit Amazon Linux 2017.03 v2.5.3 running Java 8',
            '64bit Amazon Linux 2017.03 v2.5.3 running Java 7',
            '64bit Amazon Linux 2017.03 v4.2.1 running Node.js',
            '64bit Amazon Linux 2017.03 v4.2.0 running Node.js',
            '64bit Amazon Linux 2017.03 v4.1.1 running Node.js',
            '64bit Amazon Linux 2015.09 v2.0.8 running Node.js',
            '64bit Amazon Linux 2015.03 v1.4.6 running Node.js',
            '64bit Amazon Linux 2014.03 v1.1.0 running Node.js',
            '32bit Amazon Linux 2014.03 v1.1.0 running Node.js',
            '64bit Amazon Linux 2017.03 v2.4.3 running PHP 5.4',
            '64bit Amazon Linux 2017.03 v2.4.3 running PHP 5.5',
            '64bit Amazon Linux 2017.03 v2.4.3 running PHP 5.6',
            '64bit Amazon Linux 2017.03 v2.4.3 running PHP 7.0',
            '64bit Amazon Linux 2017.03 v2.4.2 running PHP 5.4',
            '64bit Amazon Linux 2017.03 v2.4.2 running PHP 5.6',
            '64bit Amazon Linux 2017.03 v2.4.2 running PHP 7.0',
            '64bit Amazon Linux 2017.03 v2.4.1 running PHP 5.6',
            '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.4',
            '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.5',
            '64bit Amazon Linux 2016.03 v2.1.6 running PHP 5.6',
            '64bit Amazon Linux 2016.03 v2.1.6 running PHP 7.0',
            '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.6',
            '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.5',
            '64bit Amazon Linux 2015.03 v1.4.6 running PHP 5.4',
            '64bit Amazon Linux 2014.03 v1.1.0 running PHP 5.5',
            '64bit Amazon Linux 2014.03 v1.1.0 running PHP 5.4',
            '32bit Amazon Linux 2014.03 v1.1.0 running PHP 5.5',
            '32bit Amazon Linux 2014.03 v1.1.0 running PHP 5.4',
            '64bit Amazon Linux running PHP 5.3',
            '32bit Amazon Linux running PHP 5.3',
            '64bit Amazon Linux 2017.03 v2.5.0 running Python 3.4',
            '64bit Amazon Linux 2017.03 v2.5.0 running Python',
            '64bit Amazon Linux 2017.03 v2.5.0 running Python 2.7',
            '64bit Amazon Linux 2015.03 v1.4.6 running Python 3.4',
            '64bit Amazon Linux 2015.03 v1.4.6 running Python 2.7',
            '64bit Amazon Linux 2015.03 v1.4.6 running Python',
            '64bit Amazon Linux 2014.03 v1.1.0 running Python 2.7',
            '64bit Amazon Linux 2014.03 v1.1.0 running Python',
            '32bit Amazon Linux 2014.03 v1.1.0 running Python 2.7',
            '32bit Amazon Linux 2014.03 v1.1.0 running Python',
            '64bit Amazon Linux running Python',
            '32bit Amazon Linux running Python',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.3 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.2 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.3 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.2 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2017.03 v2.4.3 running Ruby 1.9.3',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.2 (Puma)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.2 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Ruby 1.9.3',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Puma)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.1 (Passenger Standalone)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Puma)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 2.0 (Passenger Standalone)',
            '64bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3',
            '32bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3',
            '64bit Amazon Linux 2017.03 v2.6.3 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2017.03 v2.6.3 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2017.03 v2.6.3 running Tomcat 7 Java 6',
            '64bit Amazon Linux 2017.03 v2.6.1 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 8 Java 8',
            '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2015.03 v1.4.5 running Tomcat 7 Java 6',
            '64bit Amazon Linux 2015.03 v1.4.4 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7',
            '64bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 6',
            '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7',
            '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 6',
            '64bit Amazon Linux running Tomcat 7',
            '64bit Amazon Linux running Tomcat 6',
            '32bit Amazon Linux running Tomcat 7',
            '32bit Amazon Linux running Tomcat 6',
            '64bit Windows Server Core 2012 R2 running IIS 8.5',
            '64bit Windows Server 2012 R2 running IIS 8.5',
            '64bit Windows Server 2012 running IIS 8',
            '64bit Windows Server 2008 R2 running IIS 7.5',
            '64bit Amazon Linux 2017.03 v2.7.2 running Docker 17.03.1-ce',
            '64bit Amazon Linux 2017.03 v2.7.1 running Docker 17.03.1-ce',
            '64bit Amazon Linux 2017.03 v2.6.0 running Docker 1.12.6',
            '64bit Amazon Linux 2016.09 v2.3.0 running Docker 1.11.2',
            '64bit Amazon Linux 2016.03 v2.1.6 running Docker 1.11.2',
            '64bit Amazon Linux 2016.03 v2.1.0 running Docker 1.9.1',
            '64bit Amazon Linux 2015.09 v2.0.6 running Docker 1.7.1',
            '64bit Amazon Linux 2015.03 v1.4.6 running Docker 1.6.2',
            '64bit Amazon Linux 2017.03 v2.7.3 running Multi-container Docker 17.03.1-ce (Generic)',
            '64bit Amazon Linux 2016.03 v2.1.6 running Multi-container Docker 1.11.2 (Generic)',
            '64bit Amazon Linux 2016.03 v2.1.0 running Multi-container Docker 1.9.1 (Generic)',
            '64bit Amazon Linux 2015.03 v1.4.6 running Multi-container Docker 1.6.2 (Generic)',
            '64bit Debian jessie v2.7.2 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.2 running GlassFish 4.0 Java 7 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running GlassFish 4.1 Java 8 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running GlassFish 4.0 Java 7 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.2 running Go 1.4 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.2 running Go 1.3 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running Go 1.4 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running Go 1.3 (Preconfigured - Docker)',
            '64bit Debian jessie v2.7.2 running Python 3.4 (Preconfigured - Docker)',
            '64bit Debian jessie v1.4.6 running Python 3.4 (Preconfigured - Docker)',
            '64bit Amazon Linux 2017.03 v2.5.1 running Go 1.8',
            '64bit Amazon Linux 2016.09 v2.3.3 running Go 1.6',
            '64bit Amazon Linux 2016.09 v2.3.0 running Go 1.5',
            '64bit Amazon Linux 2016.03 v2.1.0 running Go 1.4',
            '64bit Amazon Linux 2017.03 v2.3.1 running Packer 1.0.3',
            '64bit Amazon Linux 2017.03 v2.2.2 running Packer 1.0.0',
        ]

        solution_stacks = [SolutionStack(solution_stack) for solution_stack in solution_stacks]
        custom_platforms = [
            'arn:aws:elasticbeanstalk:us-west-2:12345678:platform/custom-platform-1/1.0.0',
        ]
        solution_stack_lister_mock.return_value = solution_stacks
        custom_platforms_lister_mock.return_value = custom_platforms

        for solution_string in solution_strings:
            solution_stack_ops.find_solution_stack_from_string(solution_string)

    @mock.patch('ebcli.lib.elasticbeanstalk.get_available_solution_stacks')
    @mock.patch('ebcli.operations.platformops.list_custom_platform_versions')
    def test_find_solution_stack_from_string__custom_platform(
            self,
            custom_platforms_lister_mock,
            solution_stack_lister_mock
    ):
        solution_stack_lister_mock.return_value = []
        custom_platforms_lister_mock.return_value = [
            'arn:aws:elasticbeanstalk:us-west-2:12345678:platform/custom-platform-1/1.0.0',
        ]

        custom_platform_inputs = [
            'arn:aws:elasticbeanstalk:us-west-2:12345678:platform/custom-platform-1/1.0.0',
            'custom-platform-1'
        ]

        for custom_platform_input in custom_platform_inputs:
            self.assertEqual(
                PlatformVersion('arn:aws:elasticbeanstalk:us-west-2:12345678:platform/custom-platform-1/1.0.0'),
                solution_stack_ops.find_solution_stack_from_string(custom_platform_input)
            )

    @mock.patch('ebcli.lib.elasticbeanstalk.get_available_solution_stacks')
    @mock.patch('ebcli.operations.solution_stack_ops.platform_arn_to_solution_stack')
    def test_find_solution_stack_from_string__eb_managed_platform(
            self,
            platform_arn_to_solution_stack_mock,
            solution_stack_lister_mock
    ):
        solution_stack_lister_mock.return_value = [
            '64bit Amazon Linux 2017.09 v2.7.1 running Tomcat 8 Java 8'
        ]
        platform_arn_to_solution_stack_mock.return_value = SolutionStack(
            '64bit Amazon Linux 2017.09 v2.7.1 running Tomcat 8 Java 8'
        )

        self.assertEqual(
            SolutionStack('64bit Amazon Linux 2017.09 v2.7.1 running Tomcat 8 Java 8'),
            solution_stack_ops.find_solution_stack_from_string(
                'arn:aws:elasticbeanstalk:us-west-2::platform/Tomcat 8 with Java 8 running on 64bit Amazon Linux/2.7.1'
            )
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.get_available_solution_stacks')
    def test_find_solution_stack_from_string__retrieves_latest(self, solution_stacks_retriever_mock):
        solution_stacks = [
            SolutionStack('64bit Amazon Linux 2017.03 v4.2.1 running Node.js'),
            SolutionStack('64bit Amazon Linux 2017.03 v4.2.0 running Node.js')
        ]
        solution_stacks_retriever_mock.return_value = solution_stacks

        self.assertEqual(
            SolutionStack('64bit Amazon Linux 2017.03 v4.2.1 running Node.js'),
            solution_stack_ops.find_solution_stack_from_string(
                '64bit Amazon Linux 2017.03 v4.2.0 running Node.js',
                find_newer=True
            )
        )


    @mock.patch('ebcli.lib.elasticbeanstalk.get_available_solution_stacks')
    def test_find_solution_stack_from_string__retrieves_latest_python_solution_Stack(self, solution_stacks_retriever_mock):
        solution_stacks = [
            SolutionStack('64bit Amazon Linux 2014.09 v1.1.0 running Python 2.7'),
            SolutionStack('64bit Amazon Linux 2014.09 v1.1.0 running Python 3.6')
        ]
        solution_stacks_retriever_mock.return_value = solution_stacks

        self.assertEqual(
            SolutionStack('64bit Amazon Linux 2014.09 v1.1.0 running Python 2.7'),
            solution_stack_ops.find_solution_stack_from_string(
                'Python 2.7',
                find_newer=True
            )
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.get_available_solution_stacks')
    @mock.patch('ebcli.operations.platformops.get_latest_custom_platform')
    def test_find_solution_stack_from_string__return_latest_custom_platform(
            self,
            latest_custom_platform_retriever_mock,
            available_solution_stacks_mock
    ):
        available_solution_stacks_mock.return_value = []
        latest_custom_platform_arn = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.3'
        latest_custom_platform_retriever_mock.return_value = PlatformVersion(latest_custom_platform_arn)

        self.assertEqual(
            PlatformVersion(latest_custom_platform_arn),
            solution_stack_ops.find_solution_stack_from_string(
                latest_custom_platform_arn,
                find_newer=True
            )
        )

    def test_get_default_solution_stack(self):
        ebcli_root = os.getcwd()
        test_dir = 'testDir'
        os.mkdir(test_dir)
        os.mkdir(os.path.join(test_dir, '.elasticbeanstalk'))
        os.chdir(test_dir)

        with open(os.path.join('.elasticbeanstalk', 'config.yml'), 'w') as config_yml:
            config_yml_contents = {
                'branch-defaults': {
                    'default': {
                        'environment': 'default-environment'
                    }
                },
                'global': {
                    'application_name': 'default-application',
                    'default_platform': 'Python 3.6'
                }
            }
            yaml.dump(config_yml_contents, config_yml)

            config_yml.close()

        try:
            self.assertEqual(
                'Python 3.6',
                solution_stack_ops.get_default_solution_stack()
            )

        finally:

            os.chdir(ebcli_root)
            shutil.rmtree(test_dir)

    @mock.patch('ebcli.lib.utils.prompt_for_index_in_list')
    def test_prompt_for_solution_stack_version(self, index_prompter_mock):
        matching_language_versions = [
            {
                'PlatformShorthand': 'Tomcat 8 Java 8',
                'LanguageName': 'Tomcat',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 8 Java 8'
            },
            {
                'PlatformShorthand': 'Tomcat 7 Java 7',
                'LanguageName': 'Tomcat',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 7 Java 7'
            },
            {
                'PlatformShorthand': 'Tomcat 7 Java 6',
                'LanguageName': 'Tomcat',
                'SolutionStack': '64bit Amazon Linux 2017.03 v2.6.1 running Tomcat 7 Java 6'
            }
        ]

        index_prompter_mock.return_value = 2

        self.assertEqual(
            'Tomcat 7 Java 6',
            solution_stack_ops.prompt_for_solution_stack_version(matching_language_versions)
        )

    def test_resolve_language_version__exactly_one_version_found(self):
        matching_language_versions = [
            {
                'PlatformShorthand': 'Node.js',
                'LanguageName': 'Node.js',
                'SolutionStack': '64bit Amazon Linux 2017.09 v4.4.0 running Node.js'
            }
        ]

        SolutionStack.group_solution_stacks_by_platform_shorthand = mock.MagicMock(return_value=matching_language_versions)

        self.assertEqual(
            '64bit Amazon Linux 2017.09 v4.4.0 running Node.js',
            solution_stack_ops.resolve_language_version(
                'Node.js',
                [
                    mock.MagicMock('solution-stack-1'),
                    mock.MagicMock('solution-stack-2')
                ]
            )
        )

    @mock.patch('ebcli.operations.solution_stack_ops.prompt_for_solution_stack_version')
    def test_resolve_language_version__multiple_versions_found(
            self,
            solution_stack_prompter_mock
    ):
        matching_language_versions = [
            {
                'PlatformShorthand': 'Tomcat 8 Java 8',
                'LanguageName': 'Tomcat',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 8 Java 8'
            },
            {
                'PlatformShorthand': 'Tomcat 7 Java 7',
                'LanguageName': 'Tomcat',
                'SolutionStack': '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 7 Java 7'
            },
            {
                'PlatformShorthand': 'Tomcat 7 Java 6',
                'LanguageName': 'Tomcat',
                'SolutionStack': '64bit Amazon Linux 2017.03 v2.6.1 running Tomcat 7 Java 6'
            }
        ]

        solution_stack_prompter_mock.return_value = matching_language_versions[0]['PlatformShorthand']

        SolutionStack.group_solution_stacks_by_platform_shorthand = mock.MagicMock(return_value=matching_language_versions)

        self.assertEqual(
            '64bit Amazon Linux 2017.09 v2.7.0 running Tomcat 8 Java 8',
            solution_stack_ops.resolve_language_version(
                'Tomcat',
                [
                    mock.MagicMock('solution-stack-1'),
                    mock.MagicMock('solution-stack-2')
                ]
            )
        )

    def test_platform_arn_to_solution_stack__custom_platform_arn(self):
        platform_arn = 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-test-test-4/1.0.0'

        self.assertIsNone(solution_stack_ops.platform_arn_to_solution_stack(platform_arn))

    def test_platform_arn_to_solution_stack__preconfigured_solution_stack_arns(self):
        platform_arns = [
            'arn:aws:elasticbeanstalk:us-west-2::platform/Docker running on 64bit Amazon Linux/2.8.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Elastic Beanstalk Packer Builder/2.4.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Go 1 running on 64bit Amazon Linux/2.7.1',
            'arn:aws:elasticbeanstalk:us-west-2::platform/IIS 10.0 running on 64bit Windows Server 2016/1.2.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/IIS 10.0 running on 64bit Windows Server Core 2016/1.2.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/IIS 7.5 running on 64bit Windows Server 2008 R2/1.2.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/IIS 7.5 running on 64bit Windows Server 2008 R2/0.1.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/IIS 8 running on 64bit Windows Server 2012/1.2.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/IIS 8 running on 64bit Windows Server 2012/0.1.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/IIS 8.5 running on 64bit Windows Server 2012 R2/1.2.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/IIS 8.5 running on 64bit Windows Server 2012 R2/0.1.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/IIS 8.5 running on 64bit Windows Server Core 2012 R2/1.2.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/IIS 8.5 running on 64bit Windows Server Core 2012 R2/0.1.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Java 8 running on 64bit Amazon Linux/2.6.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Multi-container Docker running on 64bit Amazon Linux/2.8.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 32bit Amazon Linux/1.2.1',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 32bit Amazon Linux 2014.03/1.1.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Passenger with Ruby 1.9.3 running on 32bit Amazon Linux/1.2.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Passenger with Ruby 1.9.3 running on 32bit Amazon Linux 2014.03/1.1.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Passenger with Ruby 2.4 running on 64bit Amazon Linux/2.6.1',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Passenger with Ruby 2.4 running on 64bit Amazon Linux/2.6.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.5.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Preconfigured Docker - GlassFish 4.0 with Java 7 running on 64bit Debian/2.8.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Preconfigured Docker - Python 3.4 running on 64bit Debian/2.8.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Puma with Ruby 2.4 running on 64bit Amazon Linux/2.6.1',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Python 2.7 running on 64bit Amazon Linux 2014.03/1.1.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Python 3.4 running on 64bit Amazon Linux/2.6.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Tomcat 7 with Java 7 running on 32bit Amazon Linux 2014.03/1.1.0',
            'arn:aws:elasticbeanstalk:us-west-2::platform/Tomcat 8 with Java 8 running on 64bit Amazon Linux/2.7.1',
        ]

        platform_descriptions = [
            {
                'SolutionStackName': '64bit Amazon Linux 2017.09 v2.8.0 running Docker 17.06.2-ce'
            },
            {
                'SolutionStackName': '64bit Amazon Linux 2017.09 v2.4.0 running Packer 1.0.3'
            },
            {
                'SolutionStackName': '64bit Amazon Linux 2017.09 v2.7.1 running Go 1.9'
            },
            {
                'SolutionStackName': '64bit Windows Server 2016 v1.2.0 running IIS 10.0'
            },
            {
                'SolutionStackName': '64bit Windows Server Core 2016 v1.2.0 running IIS 10.0'
            },
            {
                'SolutionStackName': '64bit Windows Server 2008 R2 v1.2.0 running IIS 7.5'
            },
            {
                'SolutionStackName': '64bit Windows Server 2008 R2 running IIS 7.5'
            },
            {
                'SolutionStackName': '64bit Windows Server 2012 v1.2.0 running IIS 8'
            },
            {
                'SolutionStackName': '64bit Windows Server 2012 running IIS 8'
            },
            {
                'SolutionStackName': '64bit Windows Server 2012 R2 v1.2.0 running IIS 8.5'
            },
            {
                'SolutionStackName': '64bit Windows Server 2012 R2 running IIS 8.5'
            },
            {
                'SolutionStackName': '64bit Windows Server Core 2012 R2 v1.2.0 running IIS 8.5'
            },
            {
                'SolutionStackName': '64bit Windows Server Core 2012 R2 running IIS 8.5'
            },
            {
                'SolutionStackName': '64bit Amazon Linux 2017.09 v2.6.0 running Java 8'
            },
            {
                'SolutionStackName': '64bit Amazon Linux 2017.09 v2.8.0 running Multi-container Docker 17.06.2-ce (Generic)'
            },
            {
                'SolutionStackName': '32bit Amazon Linux 2014.09 v1.2.1 running Node.js'
            },
            {
                'SolutionStackName': '32bit Amazon Linux 2014.03 v1.1.0 running Node.js'
            },
            {
                'SolutionStackName': '32bit Amazon Linux 2014.09 v1.2.0 running Ruby 1.9.3'
            },
            {
                'SolutionStackName': '32bit Amazon Linux 2014.03 v1.1.0 running Ruby 1.9.3'
            },
            {
                'SolutionStackName': '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.4 (Passenger Standalone)'
            },
            {
                'SolutionStackName': '64bit Amazon Linux 2017.09 v2.6.0 running Ruby 2.4 (Passenger Standalone)'
            },
            {
                'SolutionStackName': '64bit Amazon Linux 2017.03 v2.5.0 running PHP 7.1'
            },
            {
                'SolutionStackName': '64bit Debian jessie v2.8.0 running GlassFish 4.0 Java 7 (Preconfigured - Docker)'
            },
            {
                'SolutionStackName': '64bit Debian jessie v2.8.0 running Python 3.4 (Preconfigured - Docker)'
            },
            {
                'SolutionStackName': '64bit Amazon Linux 2017.09 v2.6.1 running Ruby 2.4 (Puma)'
            },
            {
                'SolutionStackName': '64bit Amazon Linux 2014.03 v1.1.0 running Python 2.7'
            },
            {
                'SolutionStackName': '64bit Amazon Linux 2017.09 v2.6.0 running Python 3.4'
            },
            {
                'SolutionStackName': '32bit Amazon Linux 2014.03 v1.1.0 running Tomcat 7 Java 7'
            },
            {
                'SolutionStackName': '64bit Amazon Linux 2017.09 v2.7.1 running Tomcat 8 Java 8'
            },
        ]

        for index in range(0, len(platform_arns)):
            with mock.patch('ebcli.lib.elasticbeanstalk.describe_platform_version') as describe_platform_version_mock:
                describe_platform_version_mock.return_value = platform_descriptions[index]

                self.assertEqual(
                    SolutionStack(platform_descriptions[index]['SolutionStackName']),
                    solution_stack_ops.platform_arn_to_solution_stack(platform_arns[index])
                )
