from __future__ import unicode_literals
from pkg_resources import DistributionNotFound
from setuptools.command import easy_install

from ebcli.bundled._compose.service import Service
from ebcli.objects.exceptions import DockerVersionError


try:
	if easy_install.get_distribution('docker-py'):
		raise DockerVersionError(
			"""Your local host has the 'docker-py' Python package installed on it.

When you run a Multicontainer Docker application locally, the EB CLI requires the 'docker' Python package.

To fix this error:

Be sure that no applications on your local host require 'docker-py', and then run this command:"
	pip uninstall docker-py"""
		)
except DistributionNotFound:
	pass


__version__ = '1.3.0dev'

