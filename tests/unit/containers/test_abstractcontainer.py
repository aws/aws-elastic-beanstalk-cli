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

from unittest import TestCase

from mock import patch, Mock

from ebcli.containers.envvarcollector import EnvvarCollector
from ebcli.containers.preconfigured_container import PreconfiguredContainer
from tests.unit.containers import dummy

OPT_ENV = EnvvarCollector({'a': '1', 'b': '555'})
SETENV_ENV = EnvvarCollector({'a': '350'})
EXPECTED_ENVVARS_MAP = {'a': '1', 'b': '555'}
IMG_ID = '12345'


class TestAbstractContainer(TestCase):
    def setUp(self):
        self.fs_handler = dummy.get_container_fs_handler()
        self.pathconfig = self.fs_handler.pathconfig
        self.cnt = PreconfiguredContainer(fs_handler=self.fs_handler,
                                          soln_stk=Mock(),
                                          container_cfg={},
                                          opt_env=OPT_ENV)
        self.cnt._get_log_volume_map = Mock(return_value=None)
        self.cnt._containerize = Mock(return_value=False)
        self.cnt._require_pull = Mock(return_value=False)

    @patch('ebcli.containers.abstractcontainer.commands')
    def test_start_check_new_dockerfie_creation_when_required(self, commands):
        self.fs_handler.require_new_dockerfile.return_value = True
        self.cnt.start()
        self.cnt._containerize.assert_called_once_with()

    @patch('ebcli.containers.abstractcontainer.commands')
    def test_start_check_new_dockerfie_no_creation(self, commands):
        self.fs_handler.require_new_dockerfile.return_value = False
        self.cnt.start()
        self.assertFalse(self.cnt._containerize.called)

    @patch('ebcli.containers.abstractcontainer.commands')
    def test_start_pull_required(self, commands):
        self.cnt._require_pull.return_value = True
        self.pathconfig.dockerfile_exists = lambda: False

        self.cnt.start()
        # We expect image pulled from Dockerfile user provided
        # since we bypassed Dockerfile creation.
        commands.pull_img.assert_called_once_with(dummy.NEW_DOCKERFILE_PATH)

    @patch('ebcli.containers.abstractcontainer.commands')
    def test_start_pull_not_required(self, commands):
        self.cnt.start()
        self.assertFalse(commands.pull_img.called)

    @patch('ebcli.containers.abstractcontainer.commands')
    def test_start_container_rm(self, commands):
        self.cnt.start()
        commands.rm_container.assert_called_once_with(self.cnt.get_name(),
                                                      force=True)

    @patch('ebcli.containers.abstractcontainer.commands')
    def test_start_check_all(self, commands):
        self.pathconfig.dockerfile_exists = lambda: False
        self.fs_handler.require_append_dockerignore.return_value = True
        self.fs_handler.require_new_dockerfile.return_value = True
        self.cnt._require_pull.return_value = True

        commands.build_img.return_value = IMG_ID

        self.cnt.start()

        # Should've appended dockerignore, containerize, pull
        # remove existing container, build, and run

        self.fs_handler.append_dockerignore.assert_called_once_with()
        self.cnt._containerize.assert_called_once_with()

        commands.pull_img.assert_called_once_with(dummy.NEW_DOCKERFILE_PATH)
        commands.build_img.expect_called_once_with(dummy.DOCKER_PROJ_PATH,
                                                   dummy.NEW_DOCKERFILE_PATH)
        commands.rm_container.assert_called_once_with(self.cnt.get_name(),
                                                      force=True)
        commands.run_container.expect_called_once_with(dummy.NEW_DOCKERFILE_PATH,
                                                       IMG_ID,
                                                       envvars_map=EXPECTED_ENVVARS_MAP)

    def test_get_name(self):
        self.pathconfig.docker_proj_path = lambda: ''
        # This is the result of sha1('')
        expected_hash = 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
        self.assertEquals(expected_hash, self.cnt.get_name())

    @patch('ebcli.containers.abstractcontainer.commands.is_running')
    def test_is_running_true(self, is_running):
        is_running.return_value = True
        self.assertTrue(self.cnt.is_running())

    @patch('ebcli.containers.abstractcontainer.commands.is_running')
    def test_is_running_false(self, is_running):
        is_running.return_value = False
        self.assertFalse(self.cnt.is_running())

    def test_final_envvars(self):
        self.fs_handler.get_setenv_env.return_value = SETENV_ENV
        self.assertDictEqual(EXPECTED_ENVVARS_MAP,
                             self.cnt.final_envvars())
