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
import os
import pip

from pkg_resources import parse_version
from setuptools.command import easy_install

from ebcli.objects.exceptions import DockerVersionError


def docker_version_is_2_6_x():
	docker_package = get_package('docker')
	if docker_package:
		if (
			parse_version('2.6.0') <= parse_version(docker_package.version) < parse_version('2.7')
		):
			return True


def get_package(package_name):
	installed_packages = pip.get_installed_distributions(local_only=True)

	for package in installed_packages:
		if package.project_name == package_name:
			return package


def install_docker_py():
	raise_if_docker_py_and_an_incorrect_version_of_docker_exist()
	raise_if_docker_py_does_not_exist_and_an_incorrect_version_of_docker_exists()
	raise_if_docker_py_and_docker_exist()
	raise_if_docker_py_exists_but_not_docker()

	if get_package('docker'):
		return

	# Install `docker` on behalf of the customer
	easy_install.main(["docker>=2.6.0,<2.7"])


def raise_if_docker_py_exists_but_not_docker():
	docker_py_package = get_package('docker-py')
	docker_package = get_package('docker')
	if docker_py_package and not docker_package:
		message = os.linesep.join([
			"Your local host has the 'docker-py' version {docker_py_version} Python package installed on it.".format(
				docker_py_version=docker_py_package.version
			),
			"When you run a Multicontainer Docker application locally, the EB CLI requires the 'docker' Python package.",
			"",
			"To fix this error:",
			"Be sure that no applications on your local host require 'docker-py', and then run this command:",
			"   pip uninstall docker-py",
			"",
			"The EB CLI will install 'docker' the next time you run it."
		])

		raise DockerVersionError(message)


def raise_if_docker_py_and_docker_exist():
	docker_py_package = get_package('docker-py')
	docker_package = get_package('docker')
	if docker_py_package and docker_package:
		message = os.linesep.join([
			"Your local host has the 'docker-py' version {docker_py_version} and 'docker' version {docker_version} Python packages installed on it.".format(
				docker_py_version=docker_py_package.version,
				docker_version=docker_package.version
			),
			"When you run a Multicontainer Docker application locally using the EB CLI, these two packages are in conflict.",
			"",
			"To fix this error:",
			"Be sure that no applications on your local host require 'docker-py', and then run this command:",
			"   pip uninstall docker-py"
		])

		raise DockerVersionError(message)


def raise_if_docker_py_and_an_incorrect_version_of_docker_exist():
	docker_py_package = get_package('docker-py')
	docker_package = get_package('docker')
	if docker_py_package and docker_package and not docker_version_is_2_6_x():
		message = os.linesep.join([
			"Your local host has the 'docker-py' version {docker_py_version} and 'docker' version {docker_version} Python packages installed on it.".format(
				docker_py_version=docker_py_package.version,
				docker_version=docker_package.version
			),
			"When you run a Multicontainer Docker application locally, these two packages are in conflict. The EB CLI also requires a different version of 'docker'.",
			"",
			"To fix this error:",
			"Be sure that no applications on your local host requires 'docker-py', and that no applications need this specific version of 'docker', and then run these commands:",
			"   pip uninstall docker-py",
			"   pip install 'docker>=2.6.0,<2.7'"
		])

		raise DockerVersionError(message)


def raise_if_docker_py_does_not_exist_and_an_incorrect_version_of_docker_exists():
	docker_py_package = get_package('docker-py')
	docker_package = get_package('docker')
	if not docker_py_package and docker_package and not docker_version_is_2_6_x():
		message = os.linesep.join([
			"Your local host has the 'docker' version {docker_version} Python package installed on it.".format(
				docker_version=docker_package.version
			),
			"When you run a Multicontainer Docker application locally, the EB CLI requires a different version of 'docker'.",
			"",
			"To fix this error:",
			"Be sure that no applications on your local host require this specific version of 'docker', and then run this command:",
			"   pip install 'docker>=2.6.0,<2.7'"
		])

		raise DockerVersionError(message)
