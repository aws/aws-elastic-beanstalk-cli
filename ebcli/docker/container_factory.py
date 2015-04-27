# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

from . import compat
from . import containerops
from . import dockerrun
from . import fshandler
from . import log

from cement.utils.misc import minimal_logger

from .fshandler import ContainerFSHandler, MultiContainerFSHandler
from .generic_container import GenericContainer
from .multicontainer import MultiContainer
from .preconfigured_container import PreconfiguredContainer
from ..controllers.create import get_and_validate_envars
from ..core import fileoperations as fops
from ..objects.exceptions import NotSupportedError, CommandError, \
        NotFoundError, NotInitializedError
from ..operations import commonops
from ..resources.strings import strings


ENVVAR_OPT_NAME_KEY = 'OptionName'
ENVVAR_VAL_KEY = 'Value'
LOG = minimal_logger(__name__)


def make_container(envvars=None, host_port=None):
    """
    Factory function for making a container or multicontainer.
    :param envvars: str: key=val str of environment variables
    :param host_port: str: optional host port mapped to container port
    :return Container/MultiContainer
    """

    soln_stk = _get_solution_stack()
    fs_handler = make_container_fs_handler()
    container_cfg = containerops.get_configuration()

    is_single_container = containerops.is_container(soln_stk, container_cfg)
    is_multi_container = containerops.is_multi(soln_stk, container_cfg)
    envvars_map = _dict_envvars(envvars)

    _validate(is_single_container, is_multi_container)

    if is_multi_container:
        return MultiContainer(fs_handler=make_multicontainer_fs_handler(),
                              envvars_map=envvars_map,
                              soln_stk=soln_stk)

    elif is_single_container:
        fs_handler = make_container_fs_handler()
        return _make_container(soln_stk=soln_stk,
                               fs_handler=fs_handler,
                               container_cfg=container_cfg,
                               envvars_map=envvars_map,
                               host_port=host_port)


def make_multicontainer_fs_handler():
    """
    Factory function for making MultiContainerFSHandler. Uses the current project
    directory to retrieve all paths and info about whether certain files exist.
    :return: MultiContainerFSHandler
    """

    docker_proj_path = fops.get_project_root()
    dockercfg_path = os.path.join(fops.get_home(), fshandler.DOCKERCFG_FILENAME)
    dockerignore_path = fops.project_file_path(fshandler.DOCKERIGNORE_FILENAME)
    logdir_path = fops.get_logs_location(log.HOST_LOGS_DIRNAME)
    hostlog_path = log.get_host_log_path(logdir_path)
    dockerrun_path = fops.project_file_path(fshandler.DOCKERRUN_FILENAME)
    compose_path = fops.get_eb_file_full_location(fshandler.COMPOSE_FILENAME)
    dockerrun_dict = dockerrun.get_dockerrun(dockerrun_path)

    return MultiContainerFSHandler(docker_proj_path=docker_proj_path,
                                   dockercfg_path=dockercfg_path,
                                   dockerignore_path=dockerignore_path,
                                   hostlog_path=hostlog_path,
                                   compose_path=compose_path,
                                   dockerrun=dockerrun_dict)


def make_container_fs_handler():
    """
    Factory function for making ContainerFSHandler. Uses the current project
    directory to retrieve all paths and info about whether certain files exist.
    :return: ContainerFSHandler
    """

    docker_proj_path = fops.get_project_root()
    dockerrun_path = fops.project_file_path(fshandler.DOCKERRUN_FILENAME)
    dockerfile_path = fops.project_file_path(fshandler.DOCKERFILE_FILENAME)
    dockercfg_path = os.path.join(fops.get_home(), fshandler.DOCKERCFG_FILENAME)
    dockerignore_path = fops.project_file_path(fshandler.DOCKERIGNORE_FILENAME)
    new_dockerfile_path = fops.get_eb_file_full_location(fshandler.NEW_DOCKERFILE_FILENAME)
    logdir_path = fops.get_logs_location(log.HOST_LOGS_DIRNAME)
    dockerfile_exists = fops.project_file_exists(fshandler.DOCKERFILE_FILENAME)
    dockerrun_exists = fops.project_file_exists(fshandler.DOCKERRUN_FILENAME)
    dockerrun_dict = dockerrun.get_dockerrun(dockerrun_path)

    return ContainerFSHandler(docker_proj_path=docker_proj_path,
                              dockerrun_path=dockerrun_path,
                              dockerfile_path=dockerfile_path,
                              dockercfg_path=dockercfg_path,
                              dockerignore_path=dockerignore_path,
                              new_dockerfile_path=new_dockerfile_path,
                              logdir_path=logdir_path,
                              dockerfile_exists=dockerfile_exists,
                              dockerrun_exists=dockerrun_exists,
                              dockerrun=dockerrun_dict)


def _make_container(soln_stk, fs_handler, container_cfg,
                    envvars_map=None, host_port=None):
    """
    Factory function for making containers. Depending on the solution stack
    given, creates appropriate PreconfiguredContainer or GenericContainer.
    :param soln_stk: SolutionStack: solution stack
    :param fs_handler: ContainerFSHandler: manages container related files
    :param container_cfg: dict: container_config.json as dict
    :param envvars_map: dict: optional key-val map of environment variables
    :param host_port: str: optional host port mapped to container port
    :return: Container
    """

    if containerops.is_generic(soln_stk, container_cfg):
        constructor = GenericContainer
    else:
        constructor = PreconfiguredContainer

    return constructor(fs_handler=fs_handler,
                       soln_stk=soln_stk,
                       container_cfg=container_cfg,
                       envvars_map=envvars_map,
                       host_port=host_port)


def _get_solution_stack():
    solution_string = commonops.get_default_solution_stack()
    soln_stk = None

    # Test out sstack and tier before we ask any questions (Fast Fail)
    if solution_string:
        try:
            soln_stk = commonops.get_solution_stack(solution_string)
        except NotFoundError:
            raise NotFoundError('Solution stack ' + solution_string +
                                ' does not appear to be valid')

    LOG.debug(soln_stk)
    if soln_stk is None:
        raise NotInitializedError
    else:
        return soln_stk


def _dict_envvars(envvars):
    if not envvars:
        return {}
    envvars_list = get_and_validate_envars(envvars)
    return {o[ENVVAR_OPT_NAME_KEY]: o[ENVVAR_VAL_KEY] for o in envvars_list}


def _validate(is_single_container, is_multi_container):
    if not is_multi_container and not is_single_container:
        raise NotSupportedError(strings['local.unsupported'])
