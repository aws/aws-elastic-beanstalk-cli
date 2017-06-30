from __future__ import unicode_literals

from ebcli.bundled._compose.docker_py_handler import client, installer

client.raise_if_client_version_is_less_than_1_9_1()
installer.install_docker_py()

from .service import Service

__version__ = '1.3.0dev'

