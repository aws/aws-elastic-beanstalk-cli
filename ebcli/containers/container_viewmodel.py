from botocore.compat import six

from . import commands, compat
from .abstractcontainer import AbstractContainer
from ..lib import utils


class ContainerViewModel(object):
    """
    Container data used to display information.
    """

    def __init__(self, soln_stk, ip, service_infos):
        """
        :param soln_stk: SolutionStack: environment's solution stack
        :param ip: str: container ip
        :param service_infos: list: services running under this container
        """

        self.soln_stk = soln_stk
        self.ip = ip
        self.service_infos = service_infos

    def get_cids(self):
        return six.iterkeys(self.get_cid_hostports_map())

    def get_cid_hostports_map(self):
        return {s.cid: s.hostports for s in self.service_infos}

    def get_cid_hostport_pairs(self):
        return utils.flatten([[(cid, p) for p in hostports]
                             for cid, hostports
                             in six.iteritems(self.get_cid_hostports_map())])

    def is_running(self):
        return any(s.is_running for s in self.service_infos)

    def num_exposed_hostports(self):
        return sum(s.num_exposed_hostports() for s in self.service_infos)

    @classmethod
    def from_container(cls, container):
        """
        Converts a container to ContainerViewModel.
        :param container: Container/MultiContainer: container being converted
        :return ContainerViewModel
        """

        soln_stk = container.soln_stk
        cids = _get_cids(container)
        is_running = container.is_running()
        ip = compat.container_ip()
        services = [ServiceInfo(cid=cid,
                                ip=ip,
                                is_running=commands.is_running(cid),
                                hostports=commands.get_exposed_hostports(cid))
                    for cid in cids]

        return cls(soln_stk, ip, services)


class ServiceInfo(object):
    """
    A service running under a Container or MultiContainer
    """

    def __init__(self, cid, ip, is_running, hostports):
        """
        :param cid: str: the container name/id
        :param ip: str: the ip the service is running
        :param is_running: bool: whether the service is running
        :param hostports: list: all host ports that are exposed
        """

        self.cid = cid
        self.is_running = is_running
        self.ip = ip
        self.hostports = hostports

    def get_urls(self):
        return ['{}:{}'.format(self.ip, hp) for hp in self.hostports]

    def num_exposed_hostports(self):
        return len(self.hostports)


def _get_cids(c):
    return [c.get_name()] if isinstance(c, AbstractContainer) else c.list_services()
