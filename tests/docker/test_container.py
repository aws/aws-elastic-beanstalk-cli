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

from ebcli.docker import dockerrun
from ebcli.docker.fshandler import ContainerFSHandler
from ebcli.docker.preconfigured_container import PreconfiguredContainer
from ebcli.objects.exceptions import CommandError
from mock import patch, Mock
from unittest import TestCase


DOCKERFILE_EXISTS = False  # Means we will be creating the Dockerfile
DOCKERRUN_EXISTS = True
DOCKER_PROJ_PATH = '/'
DOCKERRUN_PATH = '/Dockerrun.aws.json'
DOCKERFILE_PATH = '/Dockerfile'
DOCKERCFG_PATH = '/.dockercfg'
NEW_DOCKERFILE_PATH = '/.elasticbeanstalk/Dockerfile.local'
LOGDIR_PATH = '/.elasticbeanstalk/logs/local'
ENVVARS_MAP = {'0': '1'}
IMG_ID = '12345'
EXPOSED_HOST_PORT = '9000'


class TestContainer(TestCase):
    def setUp(self):
        self.fs_handler = _get_mock_fs_handler()
        self.cnt = PreconfiguredContainer(fs_handler=self.fs_handler,
                                          soln_stk=Mock(),
                                          container_cfg={},
                                          envvars_map={})
        self.cnt._get_log_volume_map = Mock(return_value=None)
        self.cnt._containerize = Mock(return_value=False)
        self.cnt._require_pull = Mock(return_value=False)

    @patch('ebcli.docker.container.commands')
    def test_require_append_dockerignore(self, commands):
        self.fs_handler.require_append_dockerignore.return_value = True
        self.cnt.start()
        self.fs_handler.append_dockerignore.assert_called_once_with()

    @patch('ebcli.docker.container.commands')
    def test_require_append_dockerignore_not_required(self, commands):
        self.cnt.start()
        self.assertFalse(self.fs_handler.append_dockerignore.called)

    @patch('ebcli.docker.container.commands')
    def test_start_check_new_dockerfie_creation(self, commands):
        self.fs_handler.require_new_dockerfile.return_value = True
        self.cnt.start()
        self.cnt._containerize.assert_called_once()

    @patch('ebcli.docker.container.commands')
    def test_start_check_new_dockerfie_no_creation(self, commands):
        self.cnt.start()
        self.assertFalse(self.cnt._containerize.called)

    @patch('ebcli.docker.container.commands')
    def test_start_pull_required(self, commands):
        self.cnt._require_pull.return_value = True

        self.cnt.start()
        # We expect image pulled from Dockerfile user provided
        # since we bypassed Dockerfile creation.
        commands.pull_img.assert_called_once_with(NEW_DOCKERFILE_PATH)

    @patch('ebcli.docker.container.commands')
    def test_start_pull_not_required(self, commands):
        self.cnt.start()
        self.assertFalse(commands.pull_img.called)

    @patch('ebcli.docker.container.commands')
    def test_start_container_rm(self, commands):
        self.cnt.start()
        commands.rm_container.assert_called_once_with(self.cnt.get_name(),
                                                      force=True)

    @patch('ebcli.docker.container.commands')
    def test_start_check_all(self, commands):
        self.fs_handler.require_append_dockerignore.return_value = True
        self.fs_handler.require_new_dockerfile.return_value = True
        self.cnt._require_pull.return_value = True

        commands.build_img.return_value = IMG_ID

        self.cnt.start()

        # Should've appended dockerignore, containerize, pull
        # remove existing container, build, and run

        self.fs_handler.append_dockerignore.assert_called_once_with()
        self.cnt._containerize.assert_called_once()

        commands.pull_img.assert_called_once_with(NEW_DOCKERFILE_PATH)
        commands.build_img.expect_called_once_with(DOCKER_PROJ_PATH,
                                                   NEW_DOCKERFILE_PATH)
        commands.rm_container.assert_called_once_with(self.cnt.get_name(),
                                                      force=True)
        commands.run_container.expect_called_once_with(NEW_DOCKERFILE_PATH,
                                                       IMG_ID,
                                                       envvars_map=ENVVARS_MAP)

    def test_get_name(self):
        self.fs_handler.docker_proj_path = ''
        expected_hash = 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
        self.assertEquals(expected_hash, self.cnt.get_name())

    @patch('ebcli.docker.container.commands.is_running')
    def test_is_running_true(self, is_running):
        is_running.return_value = True
        self.assertTrue(self.cnt.is_running())

    @patch('ebcli.docker.container.commands.is_running')
    def test_is_running_false(self, is_running):
        is_running.return_value = False
        self.assertFalse(self.cnt.is_running())


def _get_mock_fs_handler():
    mock = Mock()
    mock.docker_proj_path = DOCKER_PROJ_PATH
    mock.dockerrun_path = DOCKERRUN_PATH
    mock.dockerfile_path = DOCKERFILE_PATH
    mock.dockercfg_path = DOCKERCFG_PATH
    mock.new_dockerfile_path = NEW_DOCKERFILE_PATH
    mock.logdir_path = LOGDIR_PATH
    mock.dockerfile_exists = DOCKERFILE_EXISTS
    mock.dockerrun_exists = DOCKERRUN_EXISTS
    mock.dockerrun = dockerrun

    mock.require_append_dockerignore.return_value = False
    mock.require_new_dockerfile.return_value = False

    return mock
