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

    def __init__(self, fs_handler, envvars_map, soln_stk):
        """
        Constructor for MultiContainer.
        :param fs_handler: MultiContainerFSHandler: manage file operations
        :param envvars_map: dict: key val map of environment variables
        :param soln_stk: SolutionStack: the solution stack
        """

        self.fs_handler = fs_handler
        self.soln_stk = soln_stk
        self.envvars_map = envvars_map


    def start(self):
        self._containerize()
        self._remove()
        self._up()


    def is_running(self):
        return any(commands.is_running(cid) for cid in self.list_services())


    def list_services(self):
        compose_path = self.fs_handler.compose_path
        compose_dict = fileoperations._get_yaml_dict(compose_path)
        services = compose.iter_services(compose_dict)

        # This is the way docker-compose names the containers/services
        return ['{}_{}_1'.format(self.PROJ_NAME, s) for s in services]

    def validate(self):
        dockerrun.validate_dockerrun_v2(self.fs_handler.dockerrun)

    def _containerize(self):
        self.fs_handler.make_docker_compose(self.envvars_map)

    def _up(self):
        commands.up(self.fs_handler.compose_path)

    def _remove(self):
        for service in self.list_services():
            try:
                commands.rm_container(service, force=True)
            except CommandError:
                pass
