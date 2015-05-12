# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License'). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the 'license' file accompanying this file. This file is
# distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from ebcli.containers import commands
from ebcli.objects.exceptions import ValidationError, CommandError
from mock import patch
from unittest import TestCase


MOCK_BUILD_OUTPUT = ('Sending build context to Docker daemon   108 kB\n'
                     'Successfully built 89b8fbeca24e')
EXPECTED_BUILD_IMG_ID = '89b8fbeca24e'
MOCK_DOCKER_PATH = '/home/local/ANT/user/hello'
MOCK_SKELETON_DOCKER_PATH = '/home/local/ANT/user/hello/.Dockerfile'
MOCK_IMG = 'debian'
MOCK_TAG = 'awesome'
MOCK_IMG_TAG = '{}:{}'.format(MOCK_IMG, MOCK_TAG)
MOCK_IMG_LATEST_TAG = MOCK_IMG + ':latest'
MOCK_CONTAINER_PORT = '9000'
MOCK_HOST_PORT = '8080'
MOCK_IMG_ID = 'abcd'
MOCK_ENVVARS_MAP = {'a': '0', 'b': '1'}
MOCK_HOST_LOGS = '/.elasticbeanstalk/logs/local'
MOCK_CONTAINER_LOGS = '/tmp/'
MOCK_CONTAINER_NAME = 'abcdefg'
MOCK_VOLUME_MAP = {MOCK_HOST_LOGS: MOCK_CONTAINER_LOGS}
MOCK_IS_RUNNING = True
MOCK_CONTAINER_INFO = {commands.STATE_KEY: {commands.RUNNING_KEY:
                                            MOCK_IS_RUNNING}}
CONTAINER_PORT_PROTOCOL = '80/tcp'
MOCK_PORTS_OBJ = {CONTAINER_PORT_PROTOCOL:
                  [{commands.HOST_PORT_KEY: MOCK_HOST_PORT}]}

MOCK_CONTAINER_NETWORK = {commands.NETWORK_SETTINGS_KEY: {
    commands.PORTS_KEY: MOCK_PORTS_OBJ
}}
MOCK_COMPOSE_PATH = '.elasticbeanstalk/docker-compose.yml'


class TestCommands(TestCase):
    @patch('ebcli.containers.commands.utils.exec_cmd_live_output')
    @patch('ebcli.containers.commands.fileoperations.readlines_from_text_file')
    def test_pull_img_happy_case_has_tag(self, readlines_file, exec_cmd_live_output):
        _expect_dockerfile_lines(readlines_file, MOCK_IMG_TAG, None)
        commands.pull_img(MOCK_DOCKER_PATH)

        readlines_file.assert_called_once_with(MOCK_DOCKER_PATH)
        expected_args = ['docker', 'pull', MOCK_IMG_TAG]
        exec_cmd_live_output.assert_called_once_with(expected_args)

    @patch('ebcli.containers.commands.utils.exec_cmd_live_output')
    @patch('ebcli.containers.commands.fileoperations.readlines_from_text_file')
    def test_pull_img_happy_case_no_tag(self, readlines_file, exec_cmd_live_output):
        _expect_dockerfile_lines(readlines_file, MOCK_IMG, None)
        commands.pull_img(MOCK_DOCKER_PATH)

        readlines_file.assert_called_once_with(MOCK_DOCKER_PATH)
        expected_args = ['docker', 'pull', MOCK_IMG_LATEST_TAG]
        exec_cmd_live_output.assert_called_once_with(expected_args)

    @patch('ebcli.containers.commands.utils.exec_cmd')
    @patch('ebcli.containers.commands.fileoperations.readlines_from_text_file')
    def test_pull_img_no_img(self, readlines_file, exec_cmd):
        _expect_dockerfile_lines(readlines_file, None, MOCK_CONTAINER_PORT)
        self.assertRaises(ValidationError, commands.pull_img, MOCK_DOCKER_PATH)
        readlines_file.assert_called_once_with(MOCK_DOCKER_PATH)

    @patch('ebcli.containers.commands.utils.exec_cmd_live_output')
    @patch('ebcli.containers.commands.fileoperations.readlines_from_text_file')
    def test_build_img_happy_case(self, readlines_file, exec_cmd_live_output):
        _expect_dockerfile_lines(readlines_file, None, MOCK_CONTAINER_PORT)
        exec_cmd_live_output.return_value = MOCK_BUILD_OUTPUT
        ret = commands.build_img(MOCK_DOCKER_PATH)

        msg = 'Expected returned image to be ' + EXPECTED_BUILD_IMG_ID
        self.assertEquals(EXPECTED_BUILD_IMG_ID, ret, msg)
        expected_args = ['docker', 'build', MOCK_DOCKER_PATH]
        exec_cmd_live_output.assert_called_once_with(expected_args)

    @patch('ebcli.containers.commands.utils.exec_cmd_live_output')
    @patch('ebcli.containers.commands.fileoperations.readlines_from_text_file')
    def test_build_img_happy_case_has_file_path(self, readlines_file,
                                                exec_cmd_live_output):
        _expect_dockerfile_lines(readlines_file, None, MOCK_CONTAINER_PORT)
        exec_cmd_live_output.return_value = MOCK_BUILD_OUTPUT
        ret = commands.build_img(MOCK_DOCKER_PATH, MOCK_SKELETON_DOCKER_PATH)

        msg = 'Expected returned image to be ' + EXPECTED_BUILD_IMG_ID
        self.assertEquals(EXPECTED_BUILD_IMG_ID, ret, msg)
        expected_args = ['docker', 'build', '-f', MOCK_SKELETON_DOCKER_PATH,
                         MOCK_DOCKER_PATH]
        exec_cmd_live_output.assert_called_once_with(expected_args)

    @patch('ebcli.containers.commands.utils.exec_cmd_live_output')
    @patch('ebcli.containers.commands.fileoperations.readlines_from_text_file')
    def test_run_container_happy_case(self, readlines_file, exec_cmd_live_output):
        _expect_dockerfile_lines(readlines_file, None, MOCK_CONTAINER_PORT)
        commands.run_container(MOCK_DOCKER_PATH, MOCK_IMG_ID)

        port_map = '{}:{}'.format(MOCK_CONTAINER_PORT, MOCK_CONTAINER_PORT)
        expected_args = ['docker', 'run', '-i', '-t', '--rm', '-p', port_map,
                         MOCK_IMG_ID]
        exec_cmd_live_output.assert_called_once_with(expected_args)

    @patch('ebcli.containers.commands.utils.exec_cmd_live_output')
    @patch('ebcli.containers.commands.fileoperations.readlines_from_text_file')
    def test_run_container_happy_case_has_envvars(self, readlines_file,
                                                  exec_cmd_live_output):
        _expect_dockerfile_lines(readlines_file, None, MOCK_CONTAINER_PORT)
        commands.run_container(MOCK_DOCKER_PATH, MOCK_IMG_ID,
                               envvars_map=MOCK_ENVVARS_MAP)

        port_map = '{}:{}'.format(MOCK_CONTAINER_PORT, MOCK_CONTAINER_PORT)
        expected_args = ['docker', 'run', '-i', '-t', '--rm', '-p', port_map,
                         '--env', 'a=0', '--env', 'b=1', MOCK_IMG_ID]

        # actual_args is a list of arguments.
        actual_args, _ = exec_cmd_live_output.call_args

        self.assertEqual(1, len(actual_args))
        self.assertListEqual(sorted(expected_args), sorted(actual_args[0]))

    @patch('ebcli.containers.commands.utils.exec_cmd')
    @patch('ebcli.containers.commands.fileoperations.readlines_from_text_file')
    def test_run_container_no_port(self, readlines_file, exec_cmd):
        _expect_dockerfile_lines(readlines_file, None, None)
        self.assertRaises(ValidationError, commands.run_container,
                          MOCK_DOCKER_PATH, MOCK_IMG_ID)

    @patch('ebcli.containers.commands.utils.exec_cmd_live_output')
    @patch('ebcli.containers.commands.fileoperations.readlines_from_text_file')
    def test_run_container_has_volume_map(self, readlines_file,
                                          exec_cmd_live_output):
        _expect_dockerfile_lines(readlines_file, None, MOCK_CONTAINER_PORT)
        commands.run_container(MOCK_DOCKER_PATH, MOCK_IMG_ID,
                               volume_map=MOCK_VOLUME_MAP)

        port_map = '{}:{}'.format(MOCK_CONTAINER_PORT, MOCK_CONTAINER_PORT)
        volume_map = '{}:{}'.format(MOCK_HOST_LOGS, MOCK_CONTAINER_LOGS)
        expected_args = ['docker', 'run', '-i', '-t', '--rm', '-p', port_map,
                         '-v', volume_map, MOCK_IMG_ID]
        exec_cmd_live_output.assert_called_once_with(expected_args)

    @patch('ebcli.containers.commands.utils.exec_cmd_live_output')
    @patch('ebcli.containers.commands.fileoperations.readlines_from_text_file')
    def test_run_container_has_name(self, readlines_file, exec_cmd_live_output):
        _expect_dockerfile_lines(readlines_file, None, MOCK_CONTAINER_PORT)
        commands.run_container(MOCK_DOCKER_PATH, MOCK_IMG_ID,
                               name=MOCK_CONTAINER_NAME)

        port_map = '{}:{}'.format(MOCK_CONTAINER_PORT, MOCK_CONTAINER_PORT)
        expected_args = ['docker', 'run', '-i', '-t', '--rm', '-p', port_map,
                         '--name', MOCK_CONTAINER_NAME, MOCK_IMG_ID]
        exec_cmd_live_output.assert_called_once_with(expected_args)

    @patch('ebcli.containers.commands.utils.exec_cmd_quiet')
    @patch('ebcli.containers.commands.json.loads')
    def test_get_container_lowlvl_info_happy_case(self, loads, exec_cmd_quiet):
        loads.return_value = [{}]
        exec_cmd_quiet.return_value = '[{}]'
        lowlvl_info = commands.get_container_lowlvl_info(MOCK_CONTAINER_NAME)
        self.assertEquals({}, lowlvl_info)

        expected_args = ['docker', 'inspect', MOCK_CONTAINER_NAME]
        exec_cmd_quiet.assert_called_once_with(expected_args)
        loads.assert_called_once_with('[{}]')

    @patch('ebcli.containers.commands.utils.exec_cmd_quiet')
    @patch('ebcli.containers.commands.json.loads')
    def test_get_container_lowlvl_info_command_error(self, loads,
                                                     exec_cmd_quiet):
        exec_cmd_quiet.side_effect = CommandError(message='', output='', code=1)

        self.assertRaises(CommandError, commands.get_container_lowlvl_info,
                          MOCK_CONTAINER_NAME)

    @patch('ebcli.containers.commands.get_container_lowlvl_info')
    def test_is_running_happy_case(self, get_container_lowlvl_info):
        get_container_lowlvl_info.return_value = MOCK_CONTAINER_INFO
        self.assertEquals(MOCK_IS_RUNNING,
                          commands.is_running(MOCK_CONTAINER_NAME))

    @patch('ebcli.containers.commands.get_container_lowlvl_info')
    def test_is_running_command_error(self, get_container_lowlvl_info):
        get_container_lowlvl_info.side_effect = CommandError
        self.assertFalse(commands.is_running(MOCK_CONTAINER_NAME))

    @patch('ebcli.containers.commands.get_container_lowlvl_info')
    def test_get_exposed_hostports_happy_case(self, get_container_lowlvl_info):
        get_container_lowlvl_info.return_value = MOCK_CONTAINER_NETWORK
        self.assertEquals([MOCK_HOST_PORT],
                          commands.get_exposed_hostports(MOCK_CONTAINER_NAME))

    @patch('ebcli.containers.commands.get_container_lowlvl_info')
    def test_get_exposed_hostports_command_error_case(self,
                                                      get_container_lowlvl_info):
        get_container_lowlvl_info.side_effect = CommandError
        self.assertListEqual([], commands.get_exposed_hostports(MOCK_CONTAINER_NAME))

    @patch('ebcli.containers.commands.get_container_lowlvl_info')
    def test_is_container_existent_happy_case(self, get_container_lowlvl_info):
        self.assertTrue(commands.is_container_existent(MOCK_CONTAINER_NAME))

    @patch('ebcli.containers.commands.get_container_lowlvl_info')
    def test_is_container_existent_command_error(self,
                                                 get_container_lowlvl_info):
        get_container_lowlvl_info.side_effect = CommandError
        self.assertFalse(commands.is_container_existent(MOCK_CONTAINER_NAME))

    @patch('ebcli.containers.commands.utils.exec_cmd_quiet')
    def test_rm_container(self, exec_cmd_quiet):
        commands.rm_container(MOCK_IMG_ID)
        expected_args = ['docker', 'rm', MOCK_IMG_ID]
        exec_cmd_quiet.assert_called_once_with(expected_args)

    @patch('ebcli.containers.commands.utils.exec_cmd_quiet')
    def test_rm_container_with_force(self, exec_cmd_quiet):
        commands.rm_container(MOCK_IMG_ID, force=True)
        expected_args = ['docker', 'rm', '-f', MOCK_IMG_ID]
        exec_cmd_quiet.assert_called_once_with(expected_args)

    @patch('ebcli.containers.commands.utils.exec_cmd_quiet')
    def test_version(self, exec_cmd_quiet):
        exec_cmd_quiet.return_value = 'Docker version 1.1.0, build a8a31ef'
        self.assertEquals('1.1.0', commands.version())

    @patch('ebcli.containers.commands.utils.exec_cmd_quiet')
    def test_compose_version(self, exec_cmd_quiet):
        exec_cmd_quiet.return_value = 'docker-compose 1.1.0'
        self.assertEquals('1.1.0', commands.compose_version())

    @patch('ebcli.containers.commands._compose_run')
    def test_up_not_allow_insecure_ssl(self, _compose_run):
        compose_path = '/.elasticbeanstalk/docker-compose.yml'
        expected_args = ['-f', compose_path, 'up']

        commands.up(compose_path, False)
        _compose_run.assert_called_once_with(expected_args)

    @patch('ebcli.containers.commands._compose_run')
    def test_up_do_allow_insecure_ssl(self, _compose_run):
        compose_path = '/.elasticbeanstalk/docker-compose.yml'
        expected_args = ['-f', compose_path, 'up', '--allow-insecure-ssl']

        commands.up(compose_path, True)
        _compose_run.assert_called_once_with(expected_args)


def _expect_dockerfile_lines(readlines_from_text_file, img=None,
                             port_exposed=None):
    lines = []
    if img:
        lines.append('{} {}'.format(commands.FROM_CMD, img))
    if port_exposed:
        lines.append('{} {}'.format(commands.EXPOSE_CMD, port_exposed))

    readlines_from_text_file.return_value = lines
