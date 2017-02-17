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
import tempfile
from datetime import datetime
from shutil import copyfile, move

from termcolor import colored

import threading
import yaml

from ebcli.core.ebglobals import Constants
from ebcli.operations import logsops
from ebcli.core import io, fileoperations
from ebcli.lib import elasticbeanstalk, heuristics, s3, utils
from ebcli.objects.exceptions import NotFoundError, InvalidPlatformVersionError, PlatformWorkspaceEmptyError, TimeoutError, ValidationError
from ebcli.objects.platform import PlatformVersion
from ebcli.objects.sourcecontrol import SourceControl, NoSC
from ebcli.operations import commonops
from ebcli.operations.commonops import _zip_up_project, get_app_version_s3_location
from ebcli.operations.eventsops import print_events
from ebcli.resources.statics import namespaces, option_names
from ebcli.resources.strings import strings, prompts

from ebcli.lib import iam


VALID_PLATFORM_VERSION_FORMAT = re.compile('^\d+\.\d+\.\d+$')
VALID_PLATFORM_SHORT_FORMAT = re.compile('^([^:/]+)/(\d+\.\d+\.\d+)$')
VALID_PLATFORM_NAME_FORMAT = re.compile('^([^:/]+)$')

PLATFORM_ARN = re.compile("^arn:aws(?:-[a-z\-0-9]+)?:elasticbeanstalk:(?:[a-z\-0-9]*):\d+:platform/([^/]+)/(\d+\.\d+\.\d+)$")

class PackerStreamFormatter:
    LOG_TYPE = 1
    LOG_MESSAGE = 2
    LOG_FORMAT = re.compile(b'.*(INFO|ERROR|WARN) -- (.+)$')

    PACKER_MESSAGE = 1
    PACKER_MSG_FORMAT = re.compile(b'^Packer: \d+,(?:[^,]*),ui,(?:[^,]*),(.*)')

    PACKER_OTHER_TARGET = 1
    PACKER_OTHER_DATA = 2
    PACKER_OTHER_FORMAT = re.compile(b'^Packer: \d+,([^,]*),(.+)')

    OTHER_DATA = 1
    OTHER_FORMAT = re.compile(b'^[^:]+: (.+)')

    def __init__(self, show_timestamp=True):
        self.show_timestamp = show_timestamp

    def format(self, stream_name, message, timestamp):
        matches = PackerStreamFormatter.LOG_FORMAT.match(message)
        formatted_message = None

        if matches:
            message = matches.group(PackerStreamFormatter.LOG_MESSAGE)

            packer_message = PackerStreamFormatter.PACKER_MSG_FORMAT.match(message)
            other_packer_message = PackerStreamFormatter.PACKER_OTHER_FORMAT.match(message)
            other_message = PackerStreamFormatter.OTHER_FORMAT.match(message)

            if packer_message:
                message = packer_message.group(PackerStreamFormatter.PACKER_MESSAGE)
            elif other_packer_message:
                message = "%s: %s" % (
                    other_packer_message.group(PackerStreamFormatter.PACKER_OTHER_TARGET),
                    other_packer_message.group(PackerStreamFormatter.PACKER_OTHER_DATA))
            elif other_message:
                message = other_message.group(PackerStreamFormatter.OTHER_DATA)

            utc_time = datetime.utcfromtimestamp(timestamp / 1e3).strftime("%Y-%m-%d %H:%M:%S")

            if self.show_timestamp:
                formatted_message = "{0}    {1}    {2}".format(
                    utc_time,
                    matches.group(PackerStreamFormatter.LOG_TYPE).decode('utf-8'),
                    message.decode('utf-8'))
            else:
                formatted_message = "{0}: {1}".format(
                    matches.group(PackerStreamFormatter.LOG_TYPE).decode('utf-8'),
                    message.decode('utf-8'))

        else:
            formatted_message = "{0} {1}".format(
                stream_name,
                message.decode('utf-8'))

        return formatted_message


def get_all_platforms():
    return elasticbeanstalk.get_available_solution_stacks()


def get_environment_platform(app_name, env_name, want_solution_stack=False):
    env = elasticbeanstalk.get_environment(app_name, env_name, want_solution_stack=want_solution_stack)
    return env.platform


def list_platform_versions(platform_name=None, status=None, owner=None, show_status=False):
    return commonops.list_platform_versions_sorted_by_name(platform_name, status, owner, show_status)


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


def show_platform_events(follow, version):
    platform_name = fileoperations.get_platform_name()

    if version is None:
        version = fileoperations.get_platform_version()

        if version is None:
            raise InvalidPlatformVersionError(strings['exit.nosuchplatformversion'])

        platform = _get_platform(platform_name, version, owner=Constants.OWNED_BY_SELF)

        if platform is None:
            raise InvalidPlatformVersionError(strings['exit.nosuchplatformversion'])

        arn = platform['PlatformArn']
    else:
        arn = _version_to_arn(version)

    if arn is None:
        raise InvalidPlatformVersionError(strings['exit.nosuchplatformversion'])

    print_events(follow=follow, platform_arn=arn, app_name=None, env_name=None)


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

    if arn is None:
        raise InvalidPlatformVersionError(strings['exit.nosuchplatformversion'])

    _, platform_name, platform_version = PlatformVersion.arn_to_platform(arn)

    platform = _get_platform(platform_name, platform_version, owner=Constants.OWNED_BY_SELF)
    platform_status = elasticbeanstalk.list_platform_versions(
        platform_name=platform_name,
        platform_version=platform_version,
        owner=Constants.OWNED_BY_SELF)

    if platform is None:
        raise InvalidPlatformVersionError(strings['exit.nosuchplatformversion'])

    try:
        description = platform['Description']
    except KeyError:
        description = None

    status = platform['PlatformStatus']
    created = platform['DateCreated']
    updated = platform['DateUpdated']

    io.echo('Platform: ', arn)
    io.echo('Name: ', platform_name)
    io.echo('Version: ', version)

    # TODO: Cleanup this odd pattern used here.
    try:
        io.echo('Maintainer: ', platform['Maintainer'])
    except KeyError:
        pass

    if description:
        io.echo('Description: ', description)

    if platform_status:
        platform_status = platform_status[0]

        try:
            io.echo('Framework: ', platform_status['FrameworkName'])
        except KeyError:
            pass

        try:
            io.echo('Framework Version: ', platform_status['FrameworkVersion'])
        except KeyError:
            pass

        try:
            io.echo('Operating System: ', platform_status['OperatingSystemName'])
        except KeyError:
            pass

        try:
            io.echo('Operating System Version: ', platform_status['OperatingSystemVersion'])
        except KeyError:
            pass

        try:
            io.echo('Programming Language: ', platform_status['ProgrammingLanguageName'])
        except KeyError:
            pass

        try:
            io.echo('Programming Language Version: ', platform_status['ProgrammingLanguageVersion'])
        except KeyError:
            pass

        try:
            io.echo('Supported Tiers: ', str.join(',', platform_status['SupportedTierList']))
        except KeyError:
            pass

    io.echo('Status: ', status)
    io.echo('Created: ', created)
    io.echo('Updated: ', updated)


def create_platform_version(
        version,
        major_increment,
        minor_increment,
        patch_increment,
        instance_type,
        vpc = None,
        staged=False,
        timeout=None):

    platform_name = fileoperations.get_platform_name()
    instance_profile = fileoperations.get_instance_profile(None)
    key_name = commonops.get_default_keyname()

    if version is None:
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

    if not VALID_PLATFORM_VERSION_FORMAT.match(version):
        raise InvalidPlatformVersionError(strings['exit.invalidversion'])

    cwd = os.getcwd()
    fileoperations._traverse_to_project_root()

    try:
        if heuristics.directory_is_empty():
            raise PlatformWorkspaceEmptyError(strings['exit.platformworkspaceempty'])
    finally:
        os.chdir(cwd)

    if not heuristics.has_platform_definition_file():
        raise PlatformWorkspaceEmptyError(strings['exit.no_pdf_file'])

    source_control = SourceControl.get_source_control()
    if source_control.untracked_changes_exist():
        io.log_warning(strings['sc.unstagedchanges'])

    version_label = source_control.get_version_label()
    if staged:
        # Make a unique version label
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        version_label = version_label + '-stage-' + timestamp

    file_descriptor, original_platform_yaml = tempfile.mkstemp()
    os.close(file_descriptor)

    copyfile('platform.yaml', original_platform_yaml)

    s3_bucket = None
    s3_key = None

    try:
        # Add option settings to platform.yaml
        _enable_healthd()

        s3_bucket, s3_key = get_app_version_s3_location(platform_name, version_label)

        # Create zip file if the application version doesn't exist
        if s3_bucket is None and s3_key is None:
            file_name, file_path = _zip_up_project(version_label, source_control, staged=staged)
        else:
            file_name = None
            file_path = None
    finally:
        # Restore original platform.yaml
        move(original_platform_yaml, 'platform.yaml')

    # Use existing bucket if it exists
    bucket = elasticbeanstalk.get_storage_location() if s3_bucket is None else s3_bucket

    # Use existing key if it exists
    key = platform_name + '/' + file_name if s3_key is None else s3_key

    try:
        s3.get_object_info(bucket, key)
        io.log_info('S3 Object already exists. Skipping upload.')
    except NotFoundError:
        io.log_info('Uploading archive to s3 location: ' + key)
        s3.upload_platform_version(bucket, key, file_path)

    # Just deletes the local zip
    fileoperations.delete_app_versions()
    io.log_info('Creating Platform Version ' + version_label)
    response = elasticbeanstalk.create_platform_version(
        platform_name, version, bucket, key, instance_profile, key_name, instance_type, vpc)


    # TODO: Enable this once the API returns the name of the environment associated with a
    # CreatePlatformRequest, and remove hard coded value. There is currently only one type
    # of platform builder, we may support additional builders in the future.
    #environment_name = response['PlatformSummary']['EnvironmentName']
    environment_name = 'eb-custom-platform-builder-packer'

    io.echo(colored(
        strings['platformbuildercreation.info'].format(environment_name), attrs=['reverse']))

    fileoperations.update_platform_version(version)
    commonops.set_environment_for_current_branch(environment_name)

    arn = response['PlatformSummary']['PlatformArn']
    request_id = response['ResponseMetadata']['RequestId']

    if not timeout:
        timeout = 30

    # Share streamer for platform events and builder events
    streamer = io.get_event_streamer()

    builder_events = threading.Thread(
        target=logsops.stream_platform_logs,
        args=(platform_name, version, streamer, 5, None, PackerStreamFormatter(show_timestamp=False)))
    builder_events.daemon = True

    try:
        # Watch events from builder logs
        builder_events.start()
        commonops.wait_for_success_events(request_id, timeout_in_minutes=timeout, platform_arn=arn, streamer=streamer)
    except TimeoutError:
        io.log_error(strings['timeout.error'])


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


def _version_to_arn(platform_version):
    platform_name = fileoperations.get_platform_name()

    if VALID_PLATFORM_VERSION_FORMAT.match(platform_version):
        arn = _get_platform_arn(platform_name, platform_version, owner=Constants.OWNED_BY_SELF)
    elif PlatformVersion.is_valid_arn(platform_version):
        arn = platform_version
    elif VALID_PLATFORM_SHORT_FORMAT.match(platform_version):
        match = VALID_PLATFORM_SHORT_FORMAT.match(platform_version)
        platform_name, platform_version = match.group(1, 2)
        arn = _get_platform_arn(platform_name, platform_version, owner=Constants.OWNED_BY_SELF)
    else:
        raise InvalidPlatformVersionError(strings['exit.invalidversion'])

    return arn


def delete_platform_version(platform_version, force=False):
    arn = _version_to_arn(platform_version)

    if arn is None:
        raise InvalidPlatformVersionError(strings['exit.nosuchplatformversion'])

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


def set_workspace_to_latest():
    platform_name = fileoperations.get_platform_name()

    version = _get_latest_version(platform_name, owner=Constants.OWNED_BY_SELF)
    fileoperations.update_platform_version(version)

    if version is not None:
        io.echo(strings['platformset.version'])
        get_version_status(version)


def _get_platform(platform_name, platform_version, owner=None):
    platforms = elasticbeanstalk.list_platform_versions(platform_name=platform_name, platform_version=platform_version, owner=owner)

    for platform in platforms:
        arn = platform['PlatformArn']
        return elasticbeanstalk.describe_platform_version(arn)['PlatformDescription']

    return None


def _get_platform_arn(platform_name, platform_version, owner=None):
    platform = _get_platform(platform_name, platform_version, owner=owner)

    if platform is None:
        return None

    return platform['PlatformArn']


def _get_latest_version(platform_name=None, owner=None, ignored_states=None):
    if ignored_states is None:
        ignored_states=['Deleting', 'Failed']

    platforms = get_platforms(platform_name=platform_name, ignored_states=ignored_states, owner=owner, platform_version="latest")

    try:
        return platforms[platform_name]
    except KeyError:
        return None


def get_custom_platforms(platform_name=None, platform_version=None):
    platform_list = elasticbeanstalk.list_platform_versions(platform_name=platform_name, platform_version=platform_version)
    platforms = list()

    for platform in platform_list:
        # Ignore EB owned plaforms
        if platform['PlatformOwner'] == Constants.AWS_ELASTIC_BEANSTALK_ACCOUNT:
            continue

        platforms.append(platform['PlatformArn'])

    return platforms


def get_platforms(platform_name=None, ignored_states=None, owner=None, platform_version=None):
    platform_list = elasticbeanstalk.list_platform_versions(platform_name=platform_name, owner=owner, platform_version=platform_version)
    platforms = dict()

    for platform in platform_list:
        if ignored_states and platform['PlatformStatus'] in ignored_states:
            continue

        _, platform_name, platform_version = PlatformVersion.arn_to_platform(platform['PlatformArn'])
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
