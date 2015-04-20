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

from ..core import fileoperations, io
from ..lib import utils
from ..operations import commonops
from ..resources.strings import strings


def print_container_details(cnt_viewmodel):
    """
    Dispalays information about all the services of container.
    :param cnt_viewmodel: ContainerViewModel: contains view info about container
    :return: None
    """

    io.echo('Platform:', cnt_viewmodel.soln_stk)

    for i, service_info in enumerate(cnt_viewmodel.service_infos):
        _print_service_details(service_info)

        if i != len(cnt_viewmodel.service_infos) - 1:
            io.echo()


def open_webpage(cnt_viewmodel):
    """
    Open the webpage at container ip and host port we exposed when we ran this container.
    Raise error if container not running and prompt user to choose host port if multiple
    host ports exposed under this container.
    :param cnt_viewmodel: ContainerViewModel: contains view info about container
    :return: None
    """

    if not cnt_viewmodel.is_running():
        raise RuntimeError(strings['local.open.nocontainer'])

    # Get container id, exposed host port pairs
    cid_hostports = cnt_viewmodel.get_cid_hostport_pairs()
    num_exposed_hostports = cnt_viewmodel.num_exposed_hostports()

    if num_exposed_hostports == 1:
        _, host_port = cid_hostports[0]

    elif num_exposed_hostports > 1:
        io.echo()
        io.echo('Select a container applcation to open')
        io.echo()

        disp = ['Container {}, host port {}'.format(cid, p) for cid, p in cid_hostports]
        ind = utils.prompt_for_index_in_list(disp)

        _, host_port = cid_hostports[ind]

    else:
        raise RuntimeError(strings['local.open.noexposedport'])


    url = '{}:{}'.format(cnt_viewmodel.ip, host_port)
    commonops.open_webpage_in_browser(url)


def _print_service_details(service_info):
    exposed_host_ports_str = ', '.join(service_info.hostports) or None
    urls = ', '.join(service_info.get_urls()) or None

    io.echo('Container name:', service_info.cid)
    io.echo('Container ip:', service_info.ip)
    io.echo('Container running:', service_info.is_running)
    io.echo('Exposed host port(s):', exposed_host_ports_str)
    io.echo('Full local URL(s):', urls)


def _get_cids(c):
    return [c.get_name()] if isinstance(c, Container) else c.iter_services()
