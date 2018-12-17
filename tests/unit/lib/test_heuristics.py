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
import json
import os
import shutil

import unittest
import mock

from ebcli.lib import heuristics


class TestHeuristics(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'testDir'
        self.ebcli_root = os.getcwd()

        os.mkdir(self.test_dir)
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.ebcli_root)
        shutil.rmtree(self.test_dir)

    def create_file(self, file):
        open(file, 'w').close()

    def detect_language(self, language):
        self.assertEqual(language, heuristics.find_language_type())

    def test_find_language_type__multi_container_docker_detected(self):
        with open('Dockerrun.aws.json', 'w') as dockerrun_file:
            dockerrun_contents = {
                "AWSEBDockerrunVersion": 2
            }

            json.dump(dockerrun_contents, dockerrun_file)

            dockerrun_file.close()

        self.detect_language('Multi-container Docker')

    def test_find_language_type__docker_detected_through_Dockerrun(self):
        with open('Dockerrun.aws.json', 'w') as dockerrun_file:
            dockerrun_contents = {
                "AWSEBDockerrunVersion": 1
            }

            json.dump(dockerrun_contents, dockerrun_file)

            dockerrun_file.close()

        self.detect_language('Docker')

    def test_find_language_type__docker_detected_through_Dockerfile(self):
        self.create_file('Dockerfile')
        self.detect_language('Docker')

    def test_find_language_type__python_detected_through_dot_py_file(self):
        self.create_file('application.py')
        self.detect_language('Python')

    def test_find_language_type__python_detected_through_requirements_txt(self):
        self.create_file('requirements.txt')
        self.detect_language('Python')

    def test_find_language_type__ruby_detected_through_dot_rb_file(self):
        self.create_file('application.rb')
        self.detect_language('Ruby')

    def test_find_language_type__python_detected_through_Gemfile(self):
        self.create_file('Gemfile')
        self.detect_language('Ruby')

    def test_find_language_type__php_detected_through_dot_php(self):
        self.create_file('index.php')
        self.detect_language('PHP')

    def test_find_language_type__nodejs_detected_through_package_json(self):
        self.create_file('package.json')
        self.detect_language('Node.js')

    def test_find_language_type__iis_detected_through_systemInfo_xml(self):
        self.create_file('systemInfo.xml')
        self.detect_language('IIS')

    def test_find_language_type__tomcat_detected_through_dot_war_in_build_dir(self):
        os.mkdir('build')
        os.mkdir(os.path.join('build', 'libs'))
        self.create_file(os.path.join('build', 'libs', 'project.war'))
        self.detect_language('Tomcat')

    def test_find_language_type__tomcat_detected_through_dot_jsp_file(self):
        self.create_file('application.jsp')
        self.detect_language('Tomcat')

    def test_find_language_type__tomcat_detected_through_WEB_INF_file(self):
        self.create_file('WEB-INF')
        self.detect_language('Tomcat')

    def test_has_platform_definition_file(self):
        self.create_file('platform.yaml')
        self.assertTrue(heuristics.has_platform_definition_file())
