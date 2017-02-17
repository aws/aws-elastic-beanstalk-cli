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

from ebcli.lib import elasticbeanstalk
from ebcli.objects.platform import PlatformVersion
from ebcli.operations import platformops
from . import compat
from . import containerops
from . import dockerrun
from . import fshandler
from . import log

from cement.utils.misc import minimal_logger

from .envvarcollector import EnvvarCollector
from .pathconfig import PathConfig
from .fshandler import ContainerFSHandler, MultiContainerFSHandler
from .generic_container import GenericContainer
from .multicontainer import MultiContainer
from .preconfigured_container import PreconfiguredContainer
from ..controllers.create import get_and_validate_envars
from ..core import fileoperations as fops
from ..objects.exceptions import NotSupportedError, NotFoundError, \
        NotInitializedError
from ..operations import commonops
from ..resources.strings import strings


LOG = minimal_logger(__name__)


def make_container(envvars_str=None, host_port=None, allow_insecure_ssl=False,
                   pathconfig=PathConfig):
    """
    Factory function for making a container or multicontainer.
    :param envvars_str: str: key=val str of environment variables
    :param host_port: str: optional host port mapped to container port
    :param allow_insecure_ssl: bool: allow insecure connection to docker registry
    :param pathconfig: PathConfig: Holds path/existence info
    :return Container/MultiContainer
    """

    soln_stk = _get_solution_stack()
    container_cfg = containerops.get_configuration()
    opt_env = EnvvarCollector.from_str(envvars_str)

    if containerops.is_multi(soln_stk, container_cfg):
        return MultiContainer(fs_handler=make_multicontainer_fs_handler(pathconfig),
                              opt_env=opt_env,
                              allow_insecure_ssl=allow_insecure_ssl,
                              soln_stk=soln_stk)

    elif containerops.is_generic(soln_stk, container_cfg):
        return GenericContainer(fs_handler=make_container_fs_handler(pathconfig),
                                soln_stk=soln_stk,
                                container_cfg=container_cfg,
                                opt_env=opt_env,
                                host_port=host_port)

    elif containerops.is_preconfigured(soln_stk, container_cfg):
        return PreconfiguredContainer(fs_handler=make_container_fs_handler(pathconfig),
                                      soln_stk=soln_stk,
                                      container_cfg=container_cfg,
                                      opt_env=opt_env,
                                      host_port=host_port)

    else:
        raise NotSupportedError(strings['local.unsupported'])


def make_multicontainer_fs_handler(pathconfig):
    """
    Factory function for making MultiContainerFSHandler. Uses the current project
    directory to retrieve all paths and info about whether certain files exist.
    :param pathconfig: PathConfig: Holds path/existence info
    :return: MultiContainerFSHandler
    """

    dockerrun_dict = dockerrun.get_dockerrun(pathconfig.dockerrun_path())
    return MultiContainerFSHandler(pathconfig=pathconfig,
                                   dockerrun=dockerrun_dict)


def make_container_fs_handler(pathconfig):
    """
    Factory function for making ContainerFSHandler. Uses the current project
    directory to retrieve all paths and info about whether certain files exist.
    :param pathconfig: PathConfig: Holds path/existence info
    :return: ContainerFSHandler
    """

    dockerrun_dict = dockerrun.get_dockerrun(pathconfig.dockerrun_path())
    return ContainerFSHandler(pathconfig=pathconfig,
                              dockerrun=dockerrun_dict)


def _get_solution_stack():
    solution_string = commonops.get_default_solution_stack()
    soln_stk = None

    # Test out sstack and tier before we ask any questions (Fast Fail)
    if solution_string:
        if PlatformVersion.is_valid_arn(solution_string):
            try:
                elasticbeanstalk.describe_platform_version(solution_string)['PlatformDescription']
            except NotFoundError:
                raise NotFoundError('Platform arn %s does not appear to be valid' % solution_string)

            soln_stk = PlatformVersion(solution_string)
        else:
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
