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
import re
import sys
import tempfile
from datetime import datetime
from shutil import copyfile, move
import threading
import yaml

from semantic_version import Version
from termcolor import colored

from ebcli.core.ebglobals import Constants
from ebcli.operations import logsops
from ebcli.core import io, fileoperations
from ebcli.lib import elasticbeanstalk, heuristics, s3, utils
from ebcli.objects import api_filters
from ebcli.objects.exceptions import (
    InvalidPlatformVersionError,
    NotFoundError,
    PlatformWorkspaceEmptyError,
    ValidationError
)
from ebcli.objects.platform import PlatformVersion
from ebcli.objects.sourcecontrol import SourceControl
from ebcli.operations import commonops
from ebcli.operations.commonops import _zip_up_project, get_app_version_s3_location
from ebcli.operations.eventsops import print_events
from ebcli.resources.statics import namespaces, option_names
from ebcli.resources.strings import strings, prompts


VALID_PLATFORM_VERSION_FORMAT = re.compile('^\d+\.\d+\.\d+$')
VALID_PLATFORM_SHORT_FORMAT = re.compile('^([^:/]+)/(\d+\.\d+\.\d+)$')
VALID_PLATFORM_NAME_FORMAT = re.compile('^([^:/]+)$')

LOG_MESSAGE_REGEX = re.compile(r'.* -- (.+)$')
LOG_MESSAGE_SEVERITY_REGEX = re.compile(r'.*(INFO|ERROR|WARN) -- .*')
PACKER_UI_MESSAGE_FORMAT_REGEX = re.compile(r'Packer:.*ui,.*,(.*)')
PACKER_OTHER_MESSAGE_DATA_REGEX = re.compile(r'Packer: \d+,([^,]*),.*')
PACKER_OTHER_MESSAGE_TARGET_REGEX = re.compile(r'Packer: \d+,[^,]*,(.+)')
OTHER_FORMAT_REGEX = re.compile(r'[^:]+: (.+)')

PLATFORM_ARN = re.compile("^arn:aws(?:-[a-z\-0-9]+)?:elasticbeanstalk:(?:[a-z\-0-9]*):\d+:platform/([^/]+)/(\d+\.\d+\.\d+)$")


class PackerStreamMessage(object):
    def __init__(self, event):
        self.event = event

    def raw_message(self):
        event = self.event

        if isinstance(event, bytes):
            event = event.decode('utf-8')

        matches = LOG_MESSAGE_REGEX.search(event)

        return matches.groups(0)[0] if matches else None

    def message_severity(self):
        matches = LOG_MESSAGE_SEVERITY_REGEX.search(self.event)

        return matches.groups(0)[0] if matches else None

    def format(self):
        ui_message = self.ui_message()
        if ui_message:
            return ui_message

        other_packer_message = self.other_packer_message()

        if other_packer_message:
            if sys.version_info < (3, 0):
                other_packer_message = other_packer_message.encode('utf-8')

            other_packer_message_target = self.other_packer_message_target()
            formatted_other_message = '{}:{}'.format(
                other_packer_message_target,
                other_packer_message
            )

            if sys.version_info < (3, 0):
                formatted_other_message = formatted_other_message.decode('utf-8')

            return formatted_other_message

        other_message = self.other_message()
        if other_message:
            return other_message

    def ui_message(self):
        return self.__return_match(PACKER_UI_MESSAGE_FORMAT_REGEX)

    def other_packer_message(self):
        return self.__return_match(PACKER_OTHER_MESSAGE_DATA_REGEX)

    def other_packer_message_target(self):
        return self.__return_match(PACKER_OTHER_MESSAGE_TARGET_REGEX)

    def other_message(self):
        return self.__return_match(OTHER_FORMAT_REGEX)

    def __return_match(self, regex):
        raw_message = self.raw_message()
        if not raw_message:
            return

        if isinstance(raw_message, bytes):
            raw_message = raw_message.decode('utf-8')

        matches = regex.search(raw_message)

        return matches.groups(0)[0].strip() if matches else None


class PackerStreamFormatter(object):
    def format(self, message, stream_name=None):
        packer_stream_message = PackerStreamMessage(message)

        if packer_stream_message.raw_message():
            formatted_message = packer_stream_message.format()
        else:
            formatted_message = '{0} {1}'.format(stream_name, message)

        return formatted_message


def create_platform_version(
        version,
        major_increment,
        minor_increment,
        patch_increment,
        instance_type,
        vpc = None,
        staged=False,
        timeout=None):

    _raise_if_directory_is_empty()
    _raise_if_platform_definition_file_is_missing()
    version and _raise_if_version_format_is_invalid(version)
    platform_name = fileoperations.get_platform_name()
    instance_profile = fileoperations.get_instance_profile(None)
    key_name = commonops.get_default_keyname()
    version = version or _resolve_version_number(platform_name, major_increment, minor_increment, patch_increment)
    source_control = SourceControl.get_source_control()
    io.log_warning(strings['sc.unstagedchanges']) if source_control.untracked_changes_exist() else None
    version_label = _resolve_version_label(source_control, staged)
    bucket, key, file_path = _resolve_s3_bucket_and_key(platform_name, version_label, source_control, staged)
    _upload_platform_version_to_s3_if_necessary(bucket, key, file_path)
    io.log_info('Creating Platform Version ' + version_label)
    response = elasticbeanstalk.create_platform_version(
        platform_name, version, bucket, key, instance_profile, key_name, instance_type, vpc)

    environment_name = 'eb-custom-platform-builder-packer'

    io.echo(colored(
        strings['platformbuildercreation.info'].format(environment_name), attrs=['reverse']))

    fileoperations.update_platform_version(version)
    commonops.set_environment_for_current_branch(environment_name)

    stream_platform_logs(response, platform_name, version, timeout)


def delete_platform_version(platform_version, force=False):
    arn = _version_to_arn(platform_version)

    if not force:
        io.echo(prompts['platformdelete.confirm'].replace('{platform-arn}', arn))
        io.validate_action(prompts['platformdelete.validate'], arn)

    environments = []
    try:
        environments = [env for env in elasticbeanstalk.get_environments() if env.platform.version == arn]
    except NotFoundError:
        pass

    if len(environments) > 0:
        _, platform_name, platform_version = PlatformVersion.arn_to_platform(arn)
        raise ValidationError(strings['platformdeletevalidation.error'].format(
            platform_name,
            platform_version,
            '\n '.join([env.name for env in environments])
        ))

    response = elasticbeanstalk.delete_platform(arn)
    request_id = response['ResponseMetadata']['RequestId']
    timeout = 10

    commonops.wait_for_success_events(request_id, timeout_in_minutes=timeout, platform_arn=arn)


def describe_custom_platform_version(
        owner=None,
        platform_arn=None,
        platform_name=None,
        platform_version=None,
        status=None
):
    if not platform_arn:
        platforms = list_custom_platform_versions(
            platform_name=platform_name,
            platform_version=platform_version,
            status=status
        )

        platform_arn = platforms[0]

    return elasticbeanstalk.describe_platform_version(platform_arn)


def find_custom_platform_from_string(solution_string):
    available_custom_platforms = list_custom_platform_versions()

    for custom_platform_matcher in [
        PlatformVersion.match_with_complete_arn,
        PlatformVersion.match_with_platform_name,
    ]:
        matched_custom_platform = custom_platform_matcher(available_custom_platforms, solution_string)

        if matched_custom_platform:
            return matched_custom_platform


def get_all_platforms():
    return elasticbeanstalk.get_available_solution_stacks()


def get_custom_platform_from_customer(custom_platforms):
    selected_platform_name = prompt_customer_for_custom_platform_name(custom_platforms)

    return resolve_custom_platform_version(custom_platforms, selected_platform_name)


def get_environment_platform(app_name, env_name, want_solution_stack=False):
    env = elasticbeanstalk.get_environment(app_name=app_name, env_name=env_name, want_solution_stack=want_solution_stack)
    return env.platform


def get_latest_custom_platform(platform):
    """
    :param platform: A custom platform ARN or a custom platform name
    :return: A PlatformVersion object representing the latest version of `platform`
    """
    account_id, platform_name, platform_version = PlatformVersion.arn_to_platform(platform)

    if account_id:
        matching_platforms = list_custom_platform_versions(
            platform_name=platform_name,
            status='Ready'
        )

        if matching_platforms:
            return PlatformVersion(matching_platforms[0])


def get_latest_eb_managed_platform(platform_arn):
    account_id, platform_name, platform_version = PlatformVersion.arn_to_platform(platform_arn)

    if not account_id:
        matching_platforms = list_eb_managed_platform_versions(
            platform_name=platform_name,
            status='Ready'
        )

        if matching_platforms:
            return PlatformVersion(matching_platforms[0])


def get_platforms(platform_name=None, ignored_states=None, owner=None, platform_version=None):
    platform_list = list_custom_platform_versions(
        platform_name=platform_name,
        platform_version=platform_version
    )
    platforms = dict()

    for platform in platform_list:
        if ignored_states and platform['PlatformStatus'] in ignored_states:
            continue

        _, platform_name, platform_version = PlatformVersion.arn_to_platform(platform)
        platforms[platform_name] = platform_version

    return platforms


def get_platform_name_and_version_interactive():
    platforms = get_platforms(owner=Constants.OWNED_BY_SELF, platform_version="latest")
    platform_list = list(platforms)

    file_name = fileoperations.get_current_directory_name()
    new_platform = False
    version = None

    if len(platform_list) > 0:
        io.echo()
        io.echo('Select a platform to use')
        new_platform_option = '[ Create new Platform ]'
        platform_list.append(new_platform_option)
        try:
            default_option = platform_list.index(file_name) + 1
        except ValueError:
            default_option = len(platform_list)
        platform_name = utils.prompt_for_item_in_list(platform_list, default=default_option)
        if platform_name == new_platform_option:
            new_platform = True
        else:
            version = platforms[platform_name]

    if len(platform_list) == 0 or new_platform:
        io.echo()
        io.echo('Enter Platform Name')
        unique_name = utils.get_unique_name(file_name, platform_list)
        platform_name = io.prompt_for_unique_name(unique_name, platform_list)

    return platform_name, version


def get_version_status(version):
    platform_name = fileoperations.get_platform_name()

    if version is None:
        version = fileoperations.get_platform_version()

    if version is None:
        version = _get_latest_version(platform_name)
        fileoperations.update_platform_version(version)

    if version is None:
        raise InvalidPlatformVersionError(strings['exit.nosuchplatformversion'])

    arn = _version_to_arn(version)

    _, platform_name, platform_version = PlatformVersion.arn_to_platform(arn)

    platform = describe_custom_platform_version(
        platform_arn=arn,
        owner=Constants.OWNED_BY_SELF,
        platform_name=platform_name,
        platform_version=platform_version,
    )

    if not platform:
        raise InvalidPlatformVersionError(strings['exit.nosuchplatformversion'])

    created = platform.get('DateCreated')
    description = platform.get('Description')
    maintainer = platform.get('Maintainer')
    status = platform.get('PlatformStatus')
    updated = platform.get('DateUpdated')
    framework_name = platform.get('FrameworkName')
    framework_version = platform.get('FrameworkVersion')
    os_name = platform.get('OperatingSystemName')
    os_version = platform.get('OperatingSystemVersion')
    language_name = platform.get('ProgrammingLanguageName')
    language_version = platform.get('ProgrammingLanguageVersion')
    supported_tiers = platform.get('SupportedTierList')

    io.echo('Platform: ', arn)
    io.echo('Name: ', platform_name)
    io.echo('Version: ', version)
    io.echo('Maintainer: ', maintainer) if maintainer else None
    io.echo('Description: ', description) if description else None
    io.echo('Framework: ', framework_name) if framework_name else None
    io.echo('Framework: ', framework_name) if framework_name else None
    io.echo('Framework Version: ', framework_version) if framework_version else None
    io.echo('Operating System: ', os_name) if os_name else None
    io.echo('Operating System Version: ', os_version) if os_version else None
    io.echo('Programming Language: ', language_name) if language_name else None
    io.echo('Programming Language Version: ', language_version) if language_version else None
    io.echo('Supported Tiers: ', supported_tiers) if supported_tiers else None
    io.echo('Status: ', status)
    io.echo('Created: ', created)
    io.echo('Updated: ', updated)


def generate_version_to_arn_mappings(custom_platforms, specified_platform_name):
    version_to_arn_mappings = {}
    for custom_platform in custom_platforms:
        custom_platform_name = PlatformVersion.get_platform_name(custom_platform)
        if custom_platform_name == specified_platform_name:
            version_to_arn_mappings[PlatformVersion.get_platform_version(custom_platform)] = custom_platform

    return version_to_arn_mappings


def group_custom_platforms_by_platform_name(custom_platforms):
    return sorted(set([PlatformVersion.get_platform_name(custom_platform) for custom_platform in custom_platforms]))


def list_custom_platform_versions(
        platform_name=None,
        platform_version=None,
        show_status=False,
        status=None
):
    filters = [api_filters.PlatformOwnerFilter(values=[Constants.OWNED_BY_SELF]).json()]

    return list_platform_versions(filters, platform_name, platform_version, show_status, status)


def list_eb_managed_platform_versions(
        platform_name=None,
        platform_version=None,
        show_status=False,
        status=None
):
    filters = [api_filters.PlatformOwnerFilter(values=['AWSElasticBeanstalk']).json()]

    return list_platform_versions(filters, platform_name, platform_version, show_status, status)


def list_platform_versions(
        filters,
        platform_name=None,
        platform_version=None,
        show_status=False,
        status=None
):
    if platform_name:
        filters.append(
            api_filters.PlatformNameFilter(values=[platform_name]).json()
        )

    if platform_version:
        filters.append(
            api_filters.PlatformVersionFilter(values=[platform_version]).json()
        )

    if status:
        filters.append(
            api_filters.PlatformStatusFilter(values=[status]).json()
        )

    platforms_list = elasticbeanstalk.list_platform_versions(filters=filters)

    return __formatted_platform_descriptions(platforms_list, show_status)


def prompt_customer_for_custom_platform_name(custom_platforms):
    custom_platform_names_to_display = group_custom_platforms_by_platform_name(custom_platforms)

    return utils.prompt_for_item_in_list(custom_platform_names_to_display)


def prompt_customer_for_custom_platform_version(version_to_arn_mappings):
    custom_platform_versions_to_display = sorted(version_to_arn_mappings.keys())
    io.echo()
    io.echo(prompts['sstack.version'])
    chosen_custom_platform_version = utils.prompt_for_item_in_list(custom_platform_versions_to_display)

    return version_to_arn_mappings[chosen_custom_platform_version]


def resolve_custom_platform_version(
        custom_platforms,
        selected_platform_name
):
    version_to_arn_mappings = generate_version_to_arn_mappings(
        custom_platforms,
        selected_platform_name
    )

    custom_platform_versions = []
    for custom_platform_version in version_to_arn_mappings.keys():
        custom_platform_versions.append(Version(custom_platform_version))

    if len(custom_platform_versions) > 1:
        chosen_custom_platform_arn = prompt_customer_for_custom_platform_version(
            version_to_arn_mappings
        )
    else:
        chosen_custom_platform_arn = custom_platforms[0]

    return PlatformVersion(chosen_custom_platform_arn)


def set_platform(platform_name, platform_version=None, verify=True):

    if verify:
        arn = _name_to_arn(platform_name)

        _, platform_name, platform_version = PlatformVersion.arn_to_platform(arn)

    fileoperations.update_platform_name(platform_name)
    fileoperations.update_platform_version(platform_version)

    io.echo(strings['platformset.version'])

    # This could fail if the customer elected to create a new platform
    try:
        get_version_status(platform_version)
    except InvalidPlatformVersionError:
        io.echo(strings['platformset.newplatform'] % platform_name)


def set_workspace_to_latest():
    platform_name = fileoperations.get_platform_name()

    version = _get_latest_version(platform_name, owner=Constants.OWNED_BY_SELF)
    fileoperations.update_platform_version(version)

    if version is not None:
        io.echo(strings['platformset.version'])
        get_version_status(version)


def show_platform_events(follow, version):
    platform_name = fileoperations.get_platform_name()

    if version is None:
        version = fileoperations.get_platform_version()

        if version is None:
            raise InvalidPlatformVersionError(strings['exit.nosuchplatformversion'])

        platform = describe_custom_platform_version(
            platform_name=platform_name,
            platform_version=version,
            owner=Constants.OWNED_BY_SELF
        )

        if platform is None:
            raise InvalidPlatformVersionError(strings['exit.nosuchplatformversion'])

        arn = platform['PlatformArn']
    else:
        arn = _version_to_arn(version)

    print_events(follow=follow, platform_arn=arn, app_name=None, env_name=None)


def stream_platform_logs(response, platform_name, version, timeout):
    arn = response['PlatformSummary']['PlatformArn']
    request_id = response['ResponseMetadata']['RequestId']

    # Share streamer for platform events and builder events
    streamer = io.get_event_streamer()

    builder_events = threading.Thread(
        target=logsops.stream_platform_logs,
        args=(platform_name, version, streamer, 5, None, PackerStreamFormatter()))
    builder_events.daemon = True

    # Watch events from builder logs
    builder_events.start()
    commonops.wait_for_success_events(
        request_id,
        platform_arn=arn,
        streamer=streamer,
        timeout_in_minutes=timeout or 30
    )


def _create_app_version_zip_if_not_present_on_s3(
        platform_name,
        version_label,
        source_control,
        staged
):
    s3_bucket, s3_key = get_app_version_s3_location(platform_name, version_label)
    file_name, file_path = None, None
    if s3_bucket is None and s3_key is None:
        file_name, file_path = _zip_up_project(version_label, source_control, staged=staged)
        s3_bucket = elasticbeanstalk.get_storage_location()
        s3_key = platform_name + '/' + file_name

    return s3_bucket, s3_key, file_path


def _datetime_now():
    return datetime.now()


def _enable_healthd():
    option_settings = []

    option_settings.append({
        'namespace': namespaces.HEALTH_SYSTEM,
        'option_name': option_names.SYSTEM_TYPE,
        'value': 'enhanced'
    })

    # Attach service role
    option_settings.append({
        'namespace': namespaces.ENVIRONMENT,
        'option_name': option_names.SERVICE_ROLE,
        'value': 'aws-elasticbeanstalk-service-role'
    })

    fileoperations._traverse_to_project_root()
    with open('platform.yaml', 'r') as stream:
        platform_yaml = yaml.load(stream)

    try:
        platform_options = platform_yaml['option_settings']
    except KeyError:
        platform_options = []

    options_to_inject = []

    for option in option_settings:
        found_option = False
        for platform_option in platform_options:
            # Don't add an option if it was defined by the customer
            if option['namespace'] == platform_option['namespace'] and option['option_name']== platform_option['option_name']:
                found_option = True
                break

        if not found_option:
            options_to_inject.append(option)

    # inject new options
    platform_options.extend(options_to_inject)

    platform_yaml['option_settings'] = list(platform_options)

    with open('platform.yaml', 'w') as stream:
        stream.write(yaml.dump(platform_yaml, default_flow_style=False))


def _generate_platform_yaml_copy():
    file_descriptor, original_platform_yaml = tempfile.mkstemp()
    os.close(file_descriptor)

    copyfile('platform.yaml', original_platform_yaml)

    return original_platform_yaml


def _get_latest_version(platform_name=None, owner=None, ignored_states=None):
    if ignored_states is None:
        ignored_states=['Deleting', 'Failed']

    platforms = get_platforms(platform_name=platform_name, ignored_states=ignored_states, owner=owner, platform_version="latest")

    try:
        return platforms[platform_name]
    except KeyError:
        return None


def _get_platform_arn(platform_name, platform_version, owner=None):
    platform = describe_custom_platform_version(
        platform_name=platform_name,
        platform_version=platform_version,
        owner=owner
    )

    if platform:
        return platform['PlatformArn']


def _name_to_arn(platform_name):
    arn = None
    if VALID_PLATFORM_NAME_FORMAT.match(platform_name):
        arn = _get_platform_arn(platform_name, "latest", owner=Constants.OWNED_BY_SELF)
    elif PlatformVersion.is_valid_arn(platform_name):
        arn = platform_name
    elif VALID_PLATFORM_SHORT_FORMAT.match(platform_name):
        match = VALID_PLATFORM_SHORT_FORMAT.match(platform_name)
        platform_name, platform_version = match.group(1, 2)
        arn = _get_platform_arn(platform_name, platform_version, owner=Constants.OWNED_BY_SELF)

    if not arn:
        raise InvalidPlatformVersionError(strings['exit.nosuchplatform'])

    return arn


def _raise_if_directory_is_empty():
    cwd = os.getcwd()
    fileoperations._traverse_to_project_root()
    try:
        if heuristics.directory_is_empty():
            raise PlatformWorkspaceEmptyError(strings['exit.platformworkspaceempty'])
    finally:
        os.chdir(cwd)


def _raise_if_platform_definition_file_is_missing():
    if not heuristics.has_platform_definition_file():
        raise PlatformWorkspaceEmptyError(strings['exit.no_pdf_file'])


def _raise_if_version_format_is_invalid(version):
    if not VALID_PLATFORM_VERSION_FORMAT.match(version):
        raise InvalidPlatformVersionError(strings['exit.invalidversion'])


def _resolve_version_label(source_control, staged):
    version_label = source_control.get_version_label()
    if staged:
        # Make a unique version label
        timestamp = _datetime_now().strftime("%y%m%d_%H%M%S")
        version_label = version_label + '-stage-' + timestamp
    return version_label


def _resolve_version_number(
        platform_name,
        major_increment,
        minor_increment,
        patch_increment
):
    version = _get_latest_version(platform_name=platform_name, owner=Constants.OWNED_BY_SELF, ignored_states=[])

    if version is None:
        version = '1.0.0'
    else:
        major, minor, patch = version.split('.', 3)

        if major_increment:
            major = str(int(major) + 1)
            minor = '0'
            patch = '0'
        if minor_increment:
            minor = str(int(minor) + 1)
            patch = '0'
        if patch_increment or not(major_increment or minor_increment):
            patch = str(int(patch) + 1)

        version = "%s.%s.%s" % (major, minor, patch)

    return version


def _resolve_s3_bucket_and_key(
        platform_name,
        version_label,
        source_control,
        staged
):
    platform_yaml_copy = _generate_platform_yaml_copy()

    try:
        _enable_healthd()
        s3_bucket, s3_key, file_path = _create_app_version_zip_if_not_present_on_s3(
            platform_name,
            version_label,
            source_control,
            staged
        )
    finally:
        # Restore original platform.yaml
        move(platform_yaml_copy, 'platform.yaml')

    return s3_bucket, s3_key, file_path


def _upload_platform_version_to_s3_if_necessary(bucket, key, file_path):
    try:
        s3.get_object_info(bucket, key)
        io.log_info('S3 Object already exists. Skipping upload.')
    except NotFoundError:
        io.log_info('Uploading archive to s3 location: ' + key)
        s3.upload_platform_version(bucket, key, file_path)
    fileoperations.delete_app_versions()


def _version_to_arn(platform_version):
    platform_name = fileoperations.get_platform_name()

    arn = None
    if VALID_PLATFORM_VERSION_FORMAT.match(platform_version):
        arn = _get_platform_arn(platform_name, platform_version, owner=Constants.OWNED_BY_SELF)
    elif PlatformVersion.is_valid_arn(platform_version):
        arn = platform_version
    elif VALID_PLATFORM_SHORT_FORMAT.match(platform_version):
        match = VALID_PLATFORM_SHORT_FORMAT.match(platform_version)
        platform_name, platform_version = match.group(1, 2)
        arn = _get_platform_arn(platform_name, platform_version, owner=Constants.OWNED_BY_SELF)

    if not arn:
        raise InvalidPlatformVersionError(strings['exit.nosuchplatformversion'])

    return arn


def __formatted_platform_descriptions(platforms_list, show_status):
    platform_tuples = []
    for platform in platforms_list:
        platform_tuples.append(
            {
                'PlatformArn': platform['PlatformArn'],
                'PlatformStatus': platform['PlatformStatus']
            }
        )

    # Sort by name, then by version
    platform_tuples.sort(
        key=lambda platform_tuple: (
            PlatformVersion.get_platform_name(platform_tuple['PlatformArn']),
            Version(PlatformVersion.get_platform_version(platform_tuple['PlatformArn']))
        ),
        reverse=True
    )

    formatted_platform_descriptions = []
    for index, platform_tuple in enumerate(platform_tuples):
        if show_status:
            formatted_platform_description = '{platform_arn}  Status: {platform_status}'.format(
                platform_arn=platform_tuple['PlatformArn'],
                platform_status=platform_tuple['PlatformStatus']
            )
        else:
            formatted_platform_description = platform_tuple['PlatformArn']

        formatted_platform_descriptions.append(formatted_platform_description)

    return formatted_platform_descriptions
