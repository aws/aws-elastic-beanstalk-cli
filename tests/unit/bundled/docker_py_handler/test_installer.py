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
import os
import subprocess

from pip._vendor.pkg_resources import DistInfoDistribution

import unittest
from mock import patch

from ebcli.bundled._compose.docker_py_handler import installer
from ebcli.objects.exceptions import DockerVersionError


class TestDockerPyHandler(unittest.TestCase):
    @patch('pip.get_installed_distributions')
    def test_install_docker_py__raise_if_docker_py_and_an_incorrect_version_of_docker_exist(
            self,
            distributions_retriever_mock
    ):
        distributions_retriever_mock.return_value = [
            DistInfoDistribution(
                location='/usr/lib/python3.6/site-packages',
                project_name='docker-py',
                version='1.10.6'
            ),
            DistInfoDistribution(
                location='/usr/lib/python3.6/site-packages',
                project_name='docker',
                version='2.5.0'
            )
        ]

        with self.assertRaises(DockerVersionError) as context_manager:
            installer.install_docker_py()

        message = os.linesep.join([
            "Your local host has the 'docker-py' version 1.10.6 and 'docker' version 2.5.0 Python packages installed on it.",
            "When you run a Multicontainer Docker application locally, these two packages are in conflict. The EB CLI also requires a different version of ‘docker’.",
            "",
            "To fix this error:",
            "Be sure that no applications on your local host requires ‘docker-py’, and that no applications need this specific version of 'docker', and then run these commands:",
            "   pip uninstall docker-py",
            "   pip install 'docker>=2.6.0,<2.7'"
        ])

        self.assertEqual(message, str(context_manager.exception))

    @patch('pip.get_installed_distributions')
    def test_install_docker_py__raise_if_docker_py_does_not_exist_and_an_incorrect_version_of_docker_exists(
            self,
            distributions_retriever_mock
    ):
        distributions_retriever_mock.return_value = [
            DistInfoDistribution(
                location='/usr/lib/python3.6/site-packages',
                project_name='docker',
                version='2.5.0'
            )
        ]

        with self.assertRaises(DockerVersionError) as context_manager:
            installer.install_docker_py()

        message = os.linesep.join([
            "Your local host has the 'docker' version 2.5.0 Python package installed on it.",
            "When you run a Multicontainer Docker application locally, the EB CLI requires a different version of ‘docker’.",
            "",
            "To fix this error:",
            "Be sure that no applications on your local host require this specific version of 'docker', and then run this command:",
            "   pip install 'docker>=2.6.0,<2.7'"
        ])

        self.assertEqual(message, str(context_manager.exception))

    @patch('pip.get_installed_distributions')
    def test_install_docker_py__raise_if_docker_py_and_docker_exist(
            self,
            distributions_retriever_mock
    ):
        distributions_retriever_mock.return_value = [
            DistInfoDistribution(
                location='/usr/lib/python3.6/site-packages',
                project_name='docker-py',
                version='1.10.6'
            ),
            DistInfoDistribution(
                location='/usr/lib/python3.6/site-packages',
                project_name='docker',
                version='2.6.0'
            )
        ]

        with self.assertRaises(DockerVersionError) as context_manager:
            installer.install_docker_py()

        message = os.linesep.join([
            "Your local host has the 'docker-py' version 1.10.6 and 'docker' version 2.6.0 Python packages installed on it.",
            "When you run a Multicontainer Docker application locally using the EB CLI, these two packages are in conflict.",
            "",
            "To fix this error:",
            "Be sure that no applications on your local host require ‘docker-py’, and then run this command:",
            "   pip uninstall docker-py"
        ])

        self.assertEqual(message, str(context_manager.exception))

    @patch('pip.get_installed_distributions')
    def test_install_docker_py__raise_if_docker_py_exists_but_not_docker(
            self,
            distributions_retriever_mock
    ):
        distributions_retriever_mock.return_value = [
            DistInfoDistribution(
                location='/usr/lib/python3.6/site-packages',
                project_name='docker-py',
                version='1.10.6'
            ),
        ]

        with self.assertRaises(DockerVersionError) as context_manager:
            installer.install_docker_py()

        message = os.linesep.join([
            "Your local host has the 'docker-py' version 1.10.6 Python package installed on it.",
            "When you run a Multicontainer Docker application locally, the EB CLI requires the ‘docker’ Python package.",
            "",
            "To fix this error:",
            "Be sure that no applications on your local host require ‘docker-py’, and then run this command:",
            "   pip uninstall docker-py",
            "",
            "The EB CLI will install 'docker' the next time you run it."
        ])

        self.assertEqual(message, str(context_manager.exception))

    @patch('pip.get_installed_distributions')
    def test_install_docker_py__docker_2_6_x_present__docker_py_absent(
            self,
            distributions_retriever_mock
    ):
        distributions_retriever_mock.return_value = [
            DistInfoDistribution(
                location='/usr/lib/python3.6/site-packages',
                project_name='docker',
                version='2.6.0'
            ),
        ]

        installer.install_docker_py()

    @patch('pip.get_installed_distributions')
    @patch('subprocess.Popen')
    def test_install_docker_py__docker_2_6_x_and_docker_py_absent__installs_docker_2_6_x(
            self,
            popen_mock,
            distributions_retriever_mock
    ):
        distributions_retriever_mock.return_value = []

        installer.install_docker_py()

        popen_mock.assert_called_once_with(['pip', 'install', "docker>=2.6.0,<2.7"], stdout=subprocess.PIPE)
