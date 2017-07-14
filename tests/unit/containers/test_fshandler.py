import sys

from unittest import TestCase

from mock import patch

from ebcli.containers import commands, dockerrun
from ebcli.containers.fshandler import ContainerFSHandler, MultiContainerFSHandler
from ebcli.resources.strings import docker_ignore
from tests.unit.containers import dummy

IMG_NAME = 'janedoe/image'
PORT = '5000'
NEW_DOCKERFILE_CONTENTS_UNIX = '{} {}\n{} {}'.format(commands.FROM_CMD, IMG_NAME, commands.EXPOSE_CMD, PORT)
NEW_DOCKERFILE_CONTENTS_WINDOWS = '{} {}\r\n{} {}'.format(commands.FROM_CMD, IMG_NAME, commands.EXPOSE_CMD, PORT)
DOCKERRUN = {dockerrun.IMG_KEY: {dockerrun.IMG_NAME_KEY: IMG_NAME},
             dockerrun.PORTS_KEY: [{dockerrun.CONTAINER_PORT_KEY: PORT}]}
RUNTIME_DOCKERFILE_PATH = '/abcd/runtime'
DOCKERIGNORE_CONTENTS = 'abcdefg'
COMPOSE_PATH = '/.elasticbeanstalk/docker-compose.yml'
COMPOSE_DICT = {'php': {'image': 'php'}}
COMPOSE_YAML = '\'php\':\n  image: php'
ENVVARS_MAP = {'a': 'b', 'z': '3', 'd': '5'}
HOSTLOG_PATH = '/.elasticbeanstalk/logs/local/1234_6789'


class TestContainerFSHandler(TestCase):
    def setUp(self):
        self.pathconfig = dummy.get_pathconfig()
        self.fs_handler = ContainerFSHandler(pathconfig=self.pathconfig,
                                             dockerrun=DOCKERRUN)

    def test_require_new_dockerfile(self):
        self.pathconfig.dockerfile_exists = lambda: True
        self.assertFalse(self.fs_handler.require_new_dockerfile())

    @patch('ebcli.containers.fshandler.fileoperations.write_to_text_file')
    def test_make_dockerfile(self, write_to_text_file):
        self.fs_handler.make_dockerfile()

        if sys.platform.startswith('win'):
            write_to_text_file.assert_called_once_with(location=dummy.NEW_DOCKERFILE_PATH,
                                                   data=NEW_DOCKERFILE_CONTENTS_WINDOWS)
        else:
            write_to_text_file.assert_called_once_with(location=dummy.NEW_DOCKERFILE_PATH,
                                                   data=NEW_DOCKERFILE_CONTENTS_UNIX)

    @patch('ebcli.containers.fshandler.shutil.copyfile')
    @patch('ebcli.containers.fshandler.containerops')
    def test_copy_dockerfile(self, containerops, copyfile):
        containerops.is_preconfigured.return_value = True
        containerops._get_runtime_dockerfile_path.return_value = RUNTIME_DOCKERFILE_PATH

        self.fs_handler.copy_dockerfile(dummy.SOLN_STK, dummy.CONTAINER_CFG)

        containerops._get_runtime_dockerfile_path.assert_called_once_with(dummy.SOLN_STK,
                                                                          dummy.CONTAINER_CFG)
        copyfile.assert_called_once_with(RUNTIME_DOCKERFILE_PATH, dummy.NEW_DOCKERFILE_PATH)

    @patch('ebcli.containers.fshandler.os')
    def test_require_append_dockerignore_not_existent(self, os):
        os.path.isfile.return_value = False
        self.assertTrue(self.fs_handler.require_append_dockerignore())

    @patch('ebcli.containers.fshandler.fileoperations')
    @patch('ebcli.containers.fshandler.os')
    def test_require_append_dockerignore_true(self, os, fileoperations):
        # That is, user already has a .dockerignore but is not ignoring
        # .elasticbeanstalk and others
        os.path.isfile.return_value = True
        fileoperations.readlines_from_text_file.return_value = []

        self.assertTrue(self.fs_handler.require_append_dockerignore())

    @patch('ebcli.containers.fshandler.fileoperations')
    @patch('ebcli.containers.fshandler.os')
    def test_require_append_dockerignore_false(self, os, fileoperations):
        os.path.isfile.return_value = True
        fileoperations.readlines_from_text_file.return_value = docker_ignore

        self.assertFalse(self.fs_handler.require_append_dockerignore())


class TestMultiContainerFSHandler(TestCase):
    def setUp(self):
        self.pathconfig = dummy.get_pathconfig()
        self.multi_fs_handler = MultiContainerFSHandler(pathconfig=self.pathconfig,
                                                        dockerrun=DOCKERRUN)

    @patch('ebcli.containers.fshandler.log')
    @patch('ebcli.containers.fshandler.compose.compose_dict')
    @patch('ebcli.containers.fshandler.yaml.safe_dump')
    @patch('ebcli.containers.fshandler.fileoperations.write_to_text_file')
    def test_multicontainer_make_docker_compose(self, write_to_text_file,
                                                safe_dump, compose_dict, log):
        multi_fs_handler = self.multi_fs_handler
        compose_dict.return_value = COMPOSE_DICT
        safe_dump.return_value = COMPOSE_YAML
        log.new_host_log_path.return_value = HOSTLOG_PATH

        multi_fs_handler.make_docker_compose(ENVVARS_MAP)

        compose_dict.assert_called_once_with(DOCKERRUN, dummy.DOCKER_PROJ_PATH,
                                             HOSTLOG_PATH, ENVVARS_MAP)
        safe_dump.assert_called_once_with(COMPOSE_DICT, default_flow_style=False)
        write_to_text_file.assert_called_once_with(location=dummy.COMPOSE_PATH, data=COMPOSE_YAML)
