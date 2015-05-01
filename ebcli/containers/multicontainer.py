from . import commands
from . import compose
from . import dockerrun
from ..core import fileoperations
from ..objects.exceptions import CommandError


class MultiContainer(object):
    """
    Immutable class used to run Multi containers.
    """

    PROJ_NAME = 'elasticbeanstalk'

    def __init__(self, fs_handler, opt_env, soln_stk):
        """
        Constructor for MultiContainer.
        :param fs_handler: MultiContainerFSHandler: manages file operations
        :param envvars_map: dict: key val map of environment variables
        :param opt_env: EnvvarCollector: Optional env (--envvars) variables to add and remove
        :param soln_stk: SolutionStack: the solution stack
        """

        self.fs_handler = fs_handler
        self.pathconfig = fs_handler.pathconfig
        self.opt_env = opt_env
        self.soln_stk = soln_stk

    def start(self):
        self._containerize()
        self._remove()
        self._up()

    def validate(self):
        dockerrun.validate_dockerrun_v2(self.fs_handler.dockerrun)

    def is_running(self):
        return any(commands.is_running(cid) for cid in self.list_services())

    def list_services(self):
        compose_path = self.pathconfig.compose_path()
        compose_dict = fileoperations._get_yaml_dict(compose_path)
        services = compose.iter_services(compose_dict)

        # This is the way docker-compose names the containers/services
        return ['{}_{}_1'.format(self.PROJ_NAME, s) for s in services]

    def _containerize(self):
        opt_env = self.opt_env
        setenv_env = self.fs_handler.get_setenv_env()
        # merged_env contains env. variables from "eb local --envvars x=y ..." and
        # "eb local setenv a=b ..." but not ones in Dockerrun.aws.json
        merged_env = setenv_env.merge(opt_env)

        self.fs_handler.make_docker_compose(merged_env)

    def _up(self):
        commands.up(self.pathconfig.compose_path())

    def _remove(self):
        for service in self.list_services():
            try:
                commands.rm_container(service, force=True)
            except CommandError:
                pass
