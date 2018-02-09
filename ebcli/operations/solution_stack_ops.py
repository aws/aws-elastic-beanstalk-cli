# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

from cement.utils.misc import minimal_logger

from ebcli.core import io
from ebcli.core.ebglobals import Constants
from ebcli.lib import elasticbeanstalk, heuristics, utils
from ebcli.objects.exceptions import NotFoundError
from ebcli.objects.platform import PlatformVersion
from ebcli.objects.solutionstack import SolutionStack
from ebcli.operations import commonops, platformops
from ebcli.resources.strings import prompts, strings

CUSTOM_PLATFORM_OPTION = 'Custom Platform'

LOG = minimal_logger(__name__)


def get_default_solution_stack():
	return commonops.get_config_setting_from_branch_or_default('default_platform')


def find_solution_stack_from_string(solution_string, find_newer=False):
	"""
	Method returns a SolutionStack object representing the given `solution_string`.

	If the `solution_string` matches ARNs and complete names of solution stacks, the exact
	match is returned. In the event when there are multiple matches, the latest version is
	returned.

	:param solution_string: A string in one of the following (case-insensitive) forms:
		- PlatformArn:
			- EB-managed: 'arn:aws:elasticbeanstalk:us-west-2::platform/Multi-container Docker running on 64bit Amazon Linux/2.8.0'
			- Custom: arn:aws:elasticbeanstalk:us-west-2:123412341234:platform/custom_platform/1.0.0
		- complete name: '64bit Amazon Linux 2017.03 v2.7.5 running Multi-container Docker 17.03.2-ce (Generic)'
		- shorthand: 'Multi-container Docker 17.03.2-ce (Generic)'
		- language name: 'Multi-container Docker'
		- pythonified shorthand: 'multi-container-docker-17.03.2-ce-(generic)'
	:param find_newer: If solution_string is a complete name or a PlatformArn that uniquely matches a
			solution stack or platform, find the newest version of the solution stack.

	:return: A SolutionStack object representing the latest version of the `solution_string`. In case of a custom
		platform, the return value is a PlatformVersion object.
	"""

	# Compare input with PlatformARNs
	match = None
	if PlatformVersion.is_eb_managed_platform_arn(solution_string):
		if find_newer:
			match = platformops.get_latest_eb_managed_platform(solution_string)
		else:
			match = platform_arn_to_solution_stack(solution_string)
	elif PlatformVersion.is_custom_platform_arn(solution_string):
		if find_newer:
			match = platformops.get_latest_custom_platform(solution_string)
		else:
			match = platformops.find_custom_platform_from_string(solution_string)

	# Compare input with complete SolutionStack name and retrieve latest SolutionStack
	# in the series if `find_newer` is set to True
	if not match:
		available_solution_stacks = elasticbeanstalk.get_available_solution_stacks()

		match = SolutionStack.match_with_complete_solution_string(available_solution_stacks, solution_string)
		if match and find_newer:
			language_name = SolutionStack(solution_string).language_name
			match = SolutionStack.match_with_solution_string_language_name(available_solution_stacks, language_name)

	# Compare input with other forms
	for solution_string_matcher in [
		SolutionStack.match_with_solution_string_shorthand,
		SolutionStack.match_with_solution_string_language_name,
		SolutionStack.match_with_pythonified_solution_string,
	]:
		if not match:
			match = solution_string_matcher(available_solution_stacks, solution_string)

	# Compare input with custom platform names
	if not match:
		match = platformops.find_custom_platform_from_string(solution_string)

	if not match:
		raise NotFoundError('Platform "{}" does not appear to be valid'.format(solution_string))

	return match


def get_solution_stack_from_customer(module_name=None):
	"""
	Method prompts customer for a platform name, and if applicable, a platform version name

	:param module_name: An `module_name` to choose a platform corresponding to a
		particular module in the EB application. This is applicable if the directory
		is being `eb init`-ed with the `--modules` argument.

	:return: A SolutionStack object representing the the customers choice of platform
	"""
	solution_stacks = elasticbeanstalk.get_available_solution_stacks()
	solution_stacks_grouped_by_language_name = SolutionStack.group_solution_stacks_by_language_name(solution_stacks)
	language_names_to_display = [solution_stack['LanguageName'] for solution_stack in solution_stacks_grouped_by_language_name]

	custom_platforms = platformops.list_custom_platform_versions()

	if custom_platforms:
		language_names_to_display.append(CUSTOM_PLATFORM_OPTION)

	chosen_language_name = prompt_for_language_name(language_names_to_display, module_name)

	if chosen_language_name == CUSTOM_PLATFORM_OPTION:
		return platformops.get_custom_platform_from_customer(custom_platforms)

	return SolutionStack(resolve_language_version(chosen_language_name, solution_stacks))


def detect_platform():
	"""
	Method attempts to guess the language name depending on the application source code
	and asks the customer to verify whether the guess is correct.

	:return: A string containing the name of the platform if the customer approves, otherwise None
	"""
	detected_platform = heuristics.find_language_type()

	if detected_platform:
		io.echo()
		io.echo(prompts['platform.validate'].replace('{platform}', detected_platform))
		correct = io.get_boolean_response()

		if correct:
			return detected_platform


def prompt_for_language_name(language_names_to_display, module_name=None):
	"""
	Method prompts the customer to select a platform name in the interactive flow.

	:param language_names_to_display: A list of platform names to ask the customer
			to pick from.

			e.g.
				1. Node.js
				2. PHP
				3. Docker
				4. ...

	:param module_name: In case of a multi-module application, the name of the module
						the present selection of platform is for.

	:return: A string representing the platform the customer picked in the interactive
			flow
	"""
	chosen_solution_stack = detect_platform()

	if not chosen_solution_stack:
		io.echo()

		if not module_name:
			io.echo(prompts['platform.prompt'])
		else:
			io.echo(prompts['platform.prompt.withmodule'].replace('{module_name}', module_name))

		chosen_solution_stack = utils.prompt_for_item_in_list(language_names_to_display)

	return chosen_solution_stack


def platform_arn_to_solution_stack(platform_arn):
	"""
	Method determines the EB-managed solution stack represented by a PlatformArn

	:param platform_arn: PlatformArn of a solution stack
	:return: SolutionStack representing the PlatformArn if it an EB-managed platform, otherwise None
	"""
	if not PlatformVersion.is_eb_managed_platform_arn(platform_arn):
		return

	platform_description = elasticbeanstalk.describe_platform_version(platform_arn)

	return SolutionStack(platform_description['SolutionStackName'])


def prompt_for_solution_stack_version(matching_language_versions):
	"""
	Method prompts customer to pick a solution stack version, given a set of platform
	versions of a language

	:param matching_language_versions: A list of platform versions of a language to allow
			the customer to choose from.

				e.g. Given Platform, Ruby, the following options will be presented
					1. Ruby 2.4 (Passenger standalone)
					2. Ruby 2.4 (Puma)
					3. ...

	:return: A string representing te platform version the customer would like to use.
	"""
	io.echo()
	io.echo(prompts['sstack.version'])
	language_versions_to_display = [version['PlatformShorthand'] for version in matching_language_versions]

	return utils.prompt_for_item_in_list(language_versions_to_display)


def resolve_language_version(chosen_language_name, solution_stacks):
	"""
	Method determines the list of platform versions matching a platform name and
	returns a SolutionStack object representing the platform version the customer
	would like to use.

	:param chosen_language_name: Name of language the customer would like to use
	:param solution_stacks: A list of SolutionStack objects to assemble the list
	of related platform versions from.

	:return: A SolutionStack object representing customer's choice of language
	version.
	"""
	matching_language_versions = SolutionStack.group_solution_stacks_by_platform_shorthand(
		solution_stacks,
		language_name=chosen_language_name
	)

	if len(matching_language_versions) > 1:
		version = prompt_for_solution_stack_version(matching_language_versions)
	else:
		version = matching_language_versions[0]['PlatformShorthand']

	for language_version in matching_language_versions:
		if language_version['PlatformShorthand'] == version:
			return language_version['SolutionStack']
