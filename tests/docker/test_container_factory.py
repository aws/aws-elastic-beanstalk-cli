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

from ebcli.docker import container_factory
from ebcli.docker.fshandler import ContainerFSHandler
from ebcli.objects.exceptions import NotSupportedError, CommandError
from mock import patch, Mock
from unittest import TestCase


COMPOSE_PATH = '/.elasticbeanstalk/docker-compose.yml'
DOCKERFILE_EXISTS = True
DOCKERRUN_EXISTS = False
DOCKER_PROJ_PATH = '/'
DOCKERRUN_PATH = '/Dockerrun.aws.json'
DOCKERFILE_PATH = '/Dockerfile'
HOME_PATH = '/'
DOCKERCFG_PATH = '/.dockercfg'
DOCKERIGNORE_PATH = '/.dockerignore'
HOSTLOG_PATH = '/.elasticbeanstalk/logs/local/1234_6789'
NEW_DOCKERFILE_PATH = '/.elasticbeanstalk/Dockerfile.local'
LOGDIR_PATH = '/.elasticbeanstalk/logs/local'
HOST_PORT = '9000'
DOCKERRUN = {'AWSEBDockerrunVersion': '1'}
FS_HANDLER = ContainerFSHandler(docker_proj_path=DOCKER_PROJ_PATH,
                                dockerrun_path=DOCKERRUN_PATH,
                                dockerfile_path=DOCKERFILE_PATH,
                                dockercfg_path=DOCKERCFG_PATH,
                                dockerignore_path=DOCKERIGNORE_PATH,
                                new_dockerfile_path=NEW_DOCKERFILE_PATH,
                                logdir_path=LOGDIR_PATH,
                                dockerfile_exists=DOCKERFILE_EXISTS,
                                dockerrun_exists=DOCKERRUN_EXISTS,
                                dockerrun=DOCKERRUN)
SOLN_STK = Mock()
SUPPORTED_DOCKER_INSTALLED = True
CONTAINER_CFG = {'foo': 'bar'}
ENVVARS_MAP = {'a': 'b'}


class TestContainerFactory(TestCase):
    def setUp(self):
        self._make_container_args = dict(soln_stk=SOLN_STK,
                                         fs_handler=FS_HANDLER,
                                         container_cfg=CONTAINER_CFG,
                                         envvars_map=ENVVARS_MAP,
                                         host_port=HOST_PORT)

        self.constructor_args = dict(fs_handler=FS_HANDLER,
                                     soln_stk=SOLN_STK,
                                     container_cfg=CONTAINER_CFG,
                                     envvars_map=ENVVARS_MAP,
                                     host_port=HOST_PORT)

    @patch('ebcli.docker.container_factory.containerops.is_container')
    @patch('ebcli.docker.container_factory.GenericContainer')
    @patch('ebcli.docker.container_factory.containerops.is_generic')
    def test_make_container_helper_generic_container(self, is_generic,
                                                     GenericContainer,
                                                     is_container):
        is_container.return_value = True
        is_generic.return_value = True
        _assert_correct_constructor_called(GenericContainer,
                                           self._make_container_args,
                                           self.constructor_args)

    @patch('ebcli.docker.container_factory.containerops.is_container')
    @patch('ebcli.docker.container_factory.PreconfiguredContainer')
    @patch('ebcli.docker.container_factory.containerops.is_generic')
    def test_make_container_helper_preconfigured_container(self, is_generic,
                                                           PreconfiguredContainer,
                                                           is_container):
        is_container.return_value = True
        is_generic.return_value = False
        _assert_correct_constructor_called(PreconfiguredContainer,
                                           self._make_container_args,
                                           self.constructor_args)

    @patch('ebcli.docker.container_factory.dockerrun.get_dockerrun')
    @patch('ebcli.docker.container_factory.ContainerFSHandler')
    @patch('ebcli.docker.container_factory.fops')
    def test_make_container_fs_handler(self, fops, ContainerFSHandler, get_dockerrun):
        fops.get_project_root.side_effect = [DOCKER_PROJ_PATH]
        fops.project_file_path.side_effect = [DOCKERRUN_PATH,
                                              DOCKERFILE_PATH,
                                              DOCKERIGNORE_PATH]
        fops.project_file_exists.side_effect = [DOCKERFILE_EXISTS,
                                                DOCKERRUN_EXISTS]
        fops.get_eb_file_full_location.side_effect = [NEW_DOCKERFILE_PATH]
        fops.get_logs_location.side_effect = [LOGDIR_PATH]
        fops.get_home.side_effect = [HOME_PATH]
        get_dockerrun.side_effect = [DOCKERRUN]

        container_factory.make_container_fs_handler()

        ContainerFSHandler.assert_called_once_with(docker_proj_path=DOCKER_PROJ_PATH,
                                                   dockerrun_path=DOCKERRUN_PATH,
                                                   dockerfile_path=DOCKERFILE_PATH,
                                                   dockercfg_path=DOCKERCFG_PATH,
                                                   dockerignore_path=DOCKERIGNORE_PATH,
                                                   new_dockerfile_path=NEW_DOCKERFILE_PATH,
                                                   logdir_path=LOGDIR_PATH,
                                                   dockerfile_exists=DOCKERFILE_EXISTS,
                                                   dockerrun_exists=DOCKERRUN_EXISTS,
                                                   dockerrun=DOCKERRUN)

    @patch('ebcli.docker.container_factory.dockerrun.get_dockerrun')
    @patch('ebcli.docker.container_factory.MultiContainerFSHandler')
    @patch('ebcli.docker.container_factory.fops')
    @patch('ebcli.docker.container_factory.log')
    def test_make_multicontainer_fs_handler(self, log, fops,
                                            MultiContainerFSHandler,
                                            get_dockerrun):
        fops.get_project_root.side_effect = [DOCKER_PROJ_PATH]
        fops.project_file_path.side_effect = [DOCKERIGNORE_PATH, DOCKERRUN_PATH]
        fops.get_logs_location.side_effect = [LOGDIR_PATH]
        fops.get_home.side_effect = [HOME_PATH]
        log.get_host_log_path.side_effect = [HOSTLOG_PATH]

        fops.get_eb_file_full_location.side_effect = [COMPOSE_PATH]
        get_dockerrun.side_effect = [DOCKERRUN]

        container_factory.make_multicontainer_fs_handler()

        MultiContainerFSHandler.assert_called_once_with(docker_proj_path=DOCKER_PROJ_PATH,
                                                        dockercfg_path=DOCKERCFG_PATH,
                                                        dockerignore_path=DOCKERIGNORE_PATH,
                                                        hostlog_path=HOSTLOG_PATH,
                                                        compose_path=COMPOSE_PATH,
                                                        dockerrun=DOCKERRUN)

    def test_validate_non_docker_soln_stk(self):
        self.assertRaises(NotSupportedError, container_factory._validate,
                          False, False)

    def test_validate_single_container(self):
        try:
            container_factory._validate(True, False)
        except Exception:
            self.fail('Single containers are supported')

    def test_validate_multicontainer(self):
        try:
            container_factory._validate(False, True)
        except Exception as e:
            self.fail('Multicontainers are supported')


def _assert_correct_constructor_called(constructor, container_args,
                                       constructor_args):
    container_factory._make_container(**container_args)
    constructor.assert_called_once_with(**constructor_args)
