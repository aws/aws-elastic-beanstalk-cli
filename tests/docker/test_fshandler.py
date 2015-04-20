from ebcli.docker import commands, dockerrun
from ebcli.docker.fshandler import ContainerFSHandler, MultiContainerFSHandler
from ebcli.resources.strings import docker_ignore
from mock import patch
from unittest import TestCase


DOCKERFILE_EXISTS = False
DOCKERRUN_EXISTS = True
DOCKER_PROJ_PATH = '/'
DOCKERRUN_PATH = '/Dockerrun.aws.json'
DOCKERFILE_PATH = '/Dockerfile'
DOCKERCFG_PATH = '/.dockercfg'
DOCKERIGNORE_PATH = '/.dockerignore'
HOSTLOG_PATH = '/.elasticbeanstalk/logs/local/1234_5678'
NEW_DOCKERFILE_PATH = '/.elasticbeanstalk/Dockerfile.local'
LOGDIR_PATH = '/.elasticbeanstalk/logs/local'
IMG_NAME = 'janedoe/image'
PORT = '5000'
NEW_DOCKERFILE_CONTENTS = '''{} {}
{} {}'''.format(commands.FROM_CMD, IMG_NAME, commands.EXPOSE_CMD, PORT)

DOCKERRUN = {dockerrun.IMG_KEY: {dockerrun.IMG_NAME_KEY: IMG_NAME},
             dockerrun.PORTS_KEY: [{dockerrun.CONTAINER_PORT_KEY: PORT}]}
SOLN_STK = 'abc'
CONTAINER_CFG = {}
RUNTIME_DOCKERFILE_PATH = '/abcd/runtime'
S3_BUCKET = 'bucket'
S3_KEY = 'key'
DOCKERCFG = 'hello, world'
DOCKERIGNORE_CONTENTS = 'abcdefg'
COMPOSE_PATH = '/.elasticbeanstalk/docker-compose.yml'
COMPOSE_DICT = {'php': {'image': 'php'}}
COMPOSE_YAML = '\'php\':\n  image: php'
ENVVARS_MAP = {'a': 'b', 'z': '3', 'd': '5'}


class TestContainerFSHandler(TestCase):
    def setUp(self):
        self.fs_handler = ContainerFSHandler(docker_proj_path=DOCKER_PROJ_PATH,
                                             dockerrun_path=DOCKERRUN_PATH,
                                             dockerfile_path=DOCKERFILE_PATH,
                                             dockercfg_path=DOCKERCFG_PATH,
                                             dockerignore_path=DOCKERIGNORE_PATH,
                                             new_dockerfile_path=NEW_DOCKERFILE_PATH,
                                             logdir_path=LOGDIR_PATH,
                                             dockerfile_exists=DOCKERFILE_EXISTS,
                                             dockerrun_exists=DOCKERRUN_EXISTS,
                                             dockerrun=DOCKERRUN)

    def test_require_new_dockerfile(self):
        self.assertTrue(self.fs_handler.require_new_dockerfile())

    @patch('ebcli.docker.fshandler.fileoperations.write_to_text_file')
    def test_make_dockerfile(self, write_to_text_file):
            self.fs_handler.make_dockerfile()
            write_to_text_file.assert_called_once_with(location=NEW_DOCKERFILE_PATH,
                                                       data=NEW_DOCKERFILE_CONTENTS)

    @patch('ebcli.docker.fshandler.shutil.copyfile')
    @patch('ebcli.docker.fshandler.containerops')
    def test_copy_dockerfile(self, containerops, copyfile):
        containerops.is_preconfigured.return_value = True
        containerops._get_runtime_dockerfile_path.return_value = RUNTIME_DOCKERFILE_PATH

        self.fs_handler.copy_dockerfile(SOLN_STK, CONTAINER_CFG)

        containerops._get_runtime_dockerfile_path.assert_called_once_with(SOLN_STK,
                                                                          CONTAINER_CFG)
        copyfile.assert_called_once_with(RUNTIME_DOCKERFILE_PATH, NEW_DOCKERFILE_PATH)

    @patch('ebcli.docker.fshandler.dockerrun')
    def test_require_dockercfg_true(self, dockerrun):
        dockerrun.require_auth_download.return_value = True
        self.assertTrue(self.fs_handler.require_dockercfg())

    @patch('ebcli.docker.fshandler.dockerrun')
    def test_require_dockercfg_false(self, dockerrun):
        dockerrun.require_auth_download.return_value = False
        self.assertFalse(self.fs_handler.require_dockercfg())

    @patch('ebcli.docker.fshandler.os')
    def test_require_append_dockerignore_not_existent(self, os):
        os.path.isfile.return_value = False
        self.assertTrue(self.fs_handler.require_append_dockerignore())

    @patch('ebcli.docker.fshandler.fileoperations')
    @patch('ebcli.docker.fshandler.os')
    def test_require_append_dockerignore_true(self, os, fileoperations):
        # That is, user already has a .dockerignore but is not ignoring
        # .elasticbeanstalk and others
        os.path.isfile.return_value = True
        fileoperations.readlines_from_text_file.return_value = []

        self.assertTrue(self.fs_handler.require_append_dockerignore())

    @patch('ebcli.docker.fshandler.fileoperations')
    @patch('ebcli.docker.fshandler.os')
    def test_require_append_dockerignore_false(self, os, fileoperations):
        os.path.isfile.return_value = True
        fileoperations.readlines_from_text_file.return_value = docker_ignore

        self.assertFalse(self.fs_handler.require_append_dockerignore())

    @patch('ebcli.docker.fshandler.compose.compose_dict')
    @patch('ebcli.docker.fshandler.yaml.safe_dump')
    @patch('ebcli.docker.fshandler.fileoperations.write_to_text_file')
    def test_multicontainer_make_docker_compose(self, write_to_text_file,
                                                safe_dump, compose_dict):
        multi_fs_handler = MultiContainerFSHandler(docker_proj_path=DOCKER_PROJ_PATH,
                                                   dockercfg_path=DOCKERCFG_PATH,
                                                   dockerignore_path=DOCKERIGNORE_PATH,
                                                   hostlog_path=HOSTLOG_PATH,
                                                   compose_path=COMPOSE_PATH,
                                                   dockerrun=DOCKERRUN)
        compose_dict.return_value = COMPOSE_DICT
        safe_dump.return_value = COMPOSE_YAML

        multi_fs_handler.make_docker_compose(ENVVARS_MAP)

        compose_dict.assert_called_once_with(DOCKERRUN, DOCKER_PROJ_PATH,
                                             HOSTLOG_PATH, ENVVARS_MAP)
        safe_dump.assert_called_once_with(COMPOSE_DICT, default_flow_style=False)
        write_to_text_file.assert_called_once_with(location=COMPOSE_PATH, data=COMPOSE_YAML)
