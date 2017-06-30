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
from pkg_resources import parse_version

import unittest
from mock import MagicMock, patch

from ebcli.objects.exceptions import DockerVersionError
from ebcli.bundled._compose.docker_py_handler import client

class TestClient(unittest.TestCase):

	@patch('subprocess.Popen')
	def test_api_version__client_version_is_numeric(self, popen_mock):
		child_process_mock = MagicMock()
		stdout_mock = b'1.21'
		popen_mock.return_value = child_process_mock
		child_process_mock.communicate = MagicMock(return_value=[stdout_mock, None])

		self.assertEqual(
			parse_version('1.21'),
			client.api_version()
		)

	@patch('subprocess.Popen')
	def test_engine_version__engine_version_is_alphanumeric(self, popen_mock):
		child_process_mock = MagicMock()
		stdout_mock = b'17.09.1-ce'
		popen_mock.return_value = child_process_mock
		child_process_mock.communicate = MagicMock(return_value=[stdout_mock, None])

		self.assertEqual(
			parse_version('17.9.1'),
			client.client_version()
		)

	@patch('subprocess.Popen')
	def test_engine_version__older_engine_version__retrieve_client_version_using_docker_version_command_output(self, popen_mock):
		child_process_1_mock = MagicMock()
		stdout_1_mock = b''
		child_process_1_mock.communicate = MagicMock(return_value=[stdout_1_mock, None])
		child_process_2_mock = MagicMock()
		stdout_2_mock = b'Client version: 1.7.1\nClient API version: 1.19\nGo version (client): go1.4.2\nGit commit (client): 786b29d-dirty\nOS/Arch (client): linux/amd64\nServer version: 1.13.1\nServer API version: 1.26\nGo version (server): go1.6.2\nGit commit (server): 092cba3\nOS/Arch (server): linux/amd64\n'
		child_process_2_mock.communicate = MagicMock(return_value=[stdout_2_mock, None])

		popen_mock.side_effect = [child_process_1_mock, child_process_2_mock]

		self.assertEqual(
			parse_version('1.7.1'),
			client.client_version()
		)

	@patch('subprocess.Popen')
	def test_engine_version__cannot_find_docker_client_version(self, popen_mock):
		child_process_1_mock = MagicMock()
		stdout_1_mock = b''
		child_process_1_mock.communicate = MagicMock(return_value=[stdout_1_mock, None])
		child_process_2_mock = MagicMock()
		stdout_2_mock = b''
		child_process_2_mock.communicate = MagicMock(return_value=[stdout_2_mock, None])

		popen_mock.side_effect = [child_process_1_mock, child_process_2_mock]

		with self.assertRaises(DockerVersionError) as context_manager:
			client.client_version()

		error_message = """Couldn't connect to Docker daemon - is it running?

If it's at a non-standard location, specify the URL with the DOCKER_HOST environment variable.
"""

		self.assertEqual(error_message, str(context_manager.exception))

	@patch('subprocess.Popen')
	def test_engine_version__engine_version_is_numeric(self, popen_mock):
		child_process_mock = MagicMock()
		stdout_mock = b'1.9.1'
		popen_mock.return_value = child_process_mock
		child_process_mock.communicate = MagicMock(return_value=[stdout_mock, None])

		self.assertEqual(
			parse_version('1.9.1'),
			client.client_version()
		)

	@patch('ebcli.bundled._compose.docker_py_handler.client.client_version')
	def test_raise_if_client_version_is_less_than_1_9_1(self, client_version_mock):
		client_version_mock.return_value = parse_version('1.7.1')
		error_message = """Your local host has Docker client version 1.7.1.
When you run a Multicontainer Docker application locally, the EB CLI requires Docker client version 1.9.1 or later.
Find the latest Docker client version for your operating system here: https://www.docker.com/community-edition
"""
		with self.assertRaises(DockerVersionError) as context_manager:
			client.raise_if_client_version_is_less_than_1_9_1()

		self.assertEqual(error_message, str(context_manager.exception))
