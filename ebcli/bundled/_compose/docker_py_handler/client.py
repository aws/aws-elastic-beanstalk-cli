# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import re
import subprocess

from pkg_resources import parse_version

from ebcli.objects.exceptions import DockerVersionError


def api_version():
	p = subprocess.Popen(['docker', 'version', '--format', "'{{.Client.APIVersion}}'"], stdout=subprocess.PIPE)
	stdout, _ = p.communicate()

	return __process_version(stdout)


def client_version():
	p = subprocess.Popen(['docker', 'version', '--format', "'{{.Client.Version}}'"], stdout=subprocess.PIPE)
	stdout, _ = p.communicate()

	version_string = stdout

	if not version_string:
		# older versions of Docker engine do not have a '--format' argument for the `docker version` command
		# so we attempt to retrieve the Docker client version from the output of `docker version`
		p = subprocess.Popen(['docker', 'version'], stdout=subprocess.PIPE)
		stdout, _ = p.communicate()

		version_regexp = re.compile(r'Client version:\s+([\d.]+)', re.IGNORECASE)
		match = re.search(version_regexp, stdout.decode())

		if match:
			version_string = match.groups(0)[0].encode()

	return __process_version(version_string)


def raise_if_client_version_is_less_than_1_9_1():
	docker_client_version = client_version()
	if docker_client_version < parse_version('1.9.1'):
		raise DockerVersionError("""Your local host has Docker client version {client_version}.
When you run a Multicontainer Docker application locally, the EB CLI requires Docker client version 1.9.1 or later.
Find the latest Docker client version for your operating system here: https://www.docker.com/community-edition
""".format(client_version=str(docker_client_version)))


def __process_version(string):
	version = string.decode().strip().replace("'", "").replace('-ce', '')

	if not version:
		raise DockerVersionError("""Couldn't connect to Docker daemon - is it running?

If it's at a non-standard location, specify the URL with the DOCKER_HOST environment variable.
""")

	return parse_version(version)
