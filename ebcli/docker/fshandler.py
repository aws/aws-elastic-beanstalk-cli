import os
import shutil
import yaml

from . import commands
from . import compose
from . import containerops
from . import dockerrun
from . import log
from ..core import fileoperations
from ..lib import s3
from ..resources.strings import docker_ignore


COMPOSE_FILENAME = 'docker-compose.yml'
DOCKERCFG_FILENAME = '.dockercfg'
DOCKERIGNORE_FILENAME = '.dockerignore'
DOCKERFILE_FILENAME = 'Dockerfile'
DOCKERRUN_FILENAME = 'Dockerrun.aws.json'
NEW_DOCKERFILE_FILENAME = 'Dockerfile.local'


class ContainerFSHandler(object):
    """
    Handles Container related file operations.
    """

    def __init__(self,
                 docker_proj_path,
                 dockerrun_path,
                 dockerfile_path,
                 dockercfg_path,
                 dockerignore_path,
                 new_dockerfile_path,
                 logdir_path,
                 dockerfile_exists,
                 dockerrun_exists,
                 dockerrun):
        """
        Constructor for ContainerFSHandler.
        :param docker_proj_path: str: path of the project directory
        :param dockerrun_path: str: path to the Dockerrun.aws.json
        :param dockerfile_path: str: path where we expect user's Dockerfile
        :param dockercfg_path: str: path to .dockercfg
        :param dockerignore: str: path to .dockerignore
        :param logdir_path: str: path to the dir containing volume mapped logs
        :param new_dockerfile_path: str: path we put new Dockerfile if needed
        :param dockerfile_exists: bool: whether user provided Dockerfile
        :param dockerrun_exists: bool: whether user provided Dockerrun.aws.json
        :param dockerrun: dict: Dockerrun.aws.json as dict
        """

        self.docker_proj_path = docker_proj_path
        self.dockerrun_path = dockerrun_path
        self.dockerfile_path = dockerfile_path
        self.dockercfg_path = dockercfg_path
        self.dockerignore_path = dockerignore_path
        self.new_dockerfile_path = new_dockerfile_path
        self.logdir_path = logdir_path
        self.dockerfile_exists = dockerfile_exists
        self.dockerrun_exists = dockerrun_exists
        self.dockerrun = dockerrun

    def require_new_dockerfile(self):
        """
        Return whether we need to make a new Dockerfile since user didn't
        provide one.
        :return bool
        """

        return not self.dockerfile_exists

    def make_dockerfile(self):
        """
        Create a new Dockerfile using info provided in Dockerrun.aws.json.
        :return None
        """

        destination = self.new_dockerfile_path

        base_img = dockerrun.get_base_img(self.dockerrun)
        exposed_port = dockerrun.get_exposed_port(self.dockerrun)

        from_line = '{} {}'.format(commands.FROM_CMD, base_img)
        expose_line = '{} {}'.format(commands.EXPOSE_CMD, exposed_port)
        dockerfile_contents = os.linesep.join([from_line, expose_line])

        fileoperations.write_to_text_file(location=destination,
                                          data=dockerfile_contents)

    def require_append_dockerignore(self):
        """
        Return whether we need to append dockerignore because user isn't already
        ignoring .elasticbeanstalk/* (and others) already.
        :return bool
        """

        return _require_append_dockerignore(self.dockerignore_path)

    def append_dockerignore(self):
        """
        Append .dockerignore to include .elasticbeanstalk/* and others.
        :return None
        """

        _append_dockerignore(self.dockerignore_path)

    def copy_dockerfile(self, soln_stk, container_cfg):
        """
        Copies the appropriate Dockerfile (preconfigured Docker) that match the
        given solution stack to given destination. For example, with the given
        solution stack:

        64bit Debian jessie v1.2.0 running GlassFish 4.1 Java 8 (Preconfigured - Docker)

        copy Dockerfile with name

        glassfish-runtime-4.1-jdk8

        to destination_dockerfile.

        :param destination_dockerfile: str: destination Dockerfile location
        :param soln_stk: SolutionStack: solution stack
        :param container_cfg: dict: container_config.json
        :return: None
        """

        assert(containerops.is_preconfigured(soln_stk, container_cfg))

        dfile_path = containerops._get_runtime_dockerfile_path(soln_stk,
                                                               container_cfg)
        shutil.copyfile(dfile_path, self.new_dockerfile_path)

    def download_dockercfg(self):
        """
        Download the S3 bucket using bucket and key info in Dockerrun.aws.json.
        :return None
        """

        _download_dockercfg(self.dockerrun, self.dockercfg_path)

    def require_dockercfg(self):
        return dockerrun.require_auth_download(self.dockerrun)


class MultiContainerFSHandler(object):
    """
    Handles MultiContainer related file operations.
    """
    def __init__(self,
                 docker_proj_path,
                 dockercfg_path,
                 dockerignore_path,
                 hostlog_path,
                 compose_path,
                 dockerrun):
        """
        Constructor for MultiContainerFSHandler.
        :param docker_proj_path: str: path of the project directory
        :param dockercfg_path: str: path to .dockercfg
        :param dockerignore_path: str: path to .dockerignore
        :param hostlog_path: str: path to the dir containing container logs
        :param compose_path: str: path to docker-compose.yml
        :param dockerrun: dict: Dockerrun.aws.json as dict
        """

        self.docker_proj_path = docker_proj_path
        self.dockercfg_path = dockercfg_path
        self.dockerignore_path = dockerignore_path
        self.hostlog_path = hostlog_path
        self.compose_path = compose_path
        self.dockerrun = dockerrun

    def make_docker_compose(self, envvars_map):
        """
        Create docker-compose.yml by using Dockerrun.aws.json.
        :param envvars_map: dict: key val map of environment variables
        :return None
        """
        compose_dict = compose.compose_dict(self.dockerrun,
                                            self.docker_proj_path,
                                            self.hostlog_path,
                                            envvars_map)
        compose_yaml = yaml.safe_dump(compose_dict, default_flow_style=False)
        fileoperations.write_to_text_file(location=self.compose_path,
                                          data=compose_yaml)

    def require_dockercfg(self):
        return dockerrun.require_auth_download(self.dockerrun)


def _require_append_dockerignore(dockerignore_path):
    if not os.path.isfile(dockerignore_path):
        return True

    lines = fileoperations.readlines_from_text_file(dockerignore_path)
    return all(line.strip() != docker_ignore[0] for line in lines)


def _append_dockerignore(dockerignore_path):
    dockerignore_contents = os.linesep.join(docker_ignore)
    fileoperations.append_to_text_file(dockerignore_path,
                                       dockerignore_contents)
