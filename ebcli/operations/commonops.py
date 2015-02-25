# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

from datetime import datetime, timedelta
import time
import re
import os

from cement.utils.misc import minimal_logger
from cement.utils.shell import exec_cmd

from ..lib import elasticbeanstalk, s3, aws, ec2
from ..core import fileoperations, io
from ..objects.sourcecontrol import SourceControl
from ..resources.strings import strings, responses, prompts
from ..lib import utils
from ..objects.exceptions import *
from ..objects.solutionstack import SolutionStack
from ..lib.aws import InvalidParameterValueError
from ..lib import heuristics

LOG = minimal_logger(__name__)


def wait_for_success_events(request_id, region, timeout_in_minutes=None,
                            sleep_time=5, stream_events=True):
    if timeout_in_minutes == 0:
        return
    if timeout_in_minutes is None:
        timeout_in_minutes = 10

    start = datetime.now()
    timediff = timedelta(seconds=timeout_in_minutes * 60)

    last_time = None

    #Get first events
    events = []
    while not events:
        events = elasticbeanstalk.get_new_events(
            None, None, request_id, last_event_time=None, region=region
        )

        if len(events) > 0:
            event = events[-1]
            app_name = event.app_name
            env_name = event.environment_name

            log_event(event)
            # Test event message for success string
            _is_success_string(event.message)
            last_time = event.event_date
        else:
            time.sleep(sleep_time)

    while (datetime.now() - start) < timediff:
        time.sleep(sleep_time)

        events = elasticbeanstalk.get_new_events(
            app_name, env_name, None, last_event_time=last_time, region=region
        )

        for event in reversed(events):
            if stream_events:
                log_event(event)
                # We dont need to update last_time if we are not printing.
                # This can solve timing issues
                last_time = event.event_date

            # Test event message for success string
            if _is_success_string(event.message):
                return

    # We have timed out
    raise TimeoutError('Timed out while waiting for command to Complete')


def _is_success_string(message):
    if message == responses['event.greenmessage']:
        return True
    if message.startswith(responses['event.launchsuccess']):
        return True
    if message == responses['event.redmessage']:
        raise ServiceError(message)
    if message.startswith(responses['event.launchbad']):
        raise ServiceError(message)
    if message.startswith(responses['event.updatebad']):
        raise ServiceError(message)
    if message == responses['event.failedlaunch']:
        raise ServiceError(message)
    if message == responses['logs.pulled']:
        return True
    if message == responses['env.terminated']:
        return True
    if message == responses['env.updatesuccess']:
        return True
    if message == responses['env.configsuccess']:
        return True
    if message == responses['app.deletesuccess']:
        return True
    if responses['logs.successtail'] in message:
        return True
    if responses['logs.successbundle'] in message:
        return True
    if message.startswith(responses['swap.success']):
        return True

    return False


def log_event(event, echo=False):
    message = event.message
    severity = event.severity
    date = event.event_date
    if echo:
        io.echo(date.strftime("%Y-%m-%d %H:%M:%S").ljust(23),
                severity.ljust(7), message)
    elif severity == 'INFO':
        io.echo('INFO:', message)
    elif severity == 'WARN':
        io.log_warning(message)
    elif severity == 'ERROR':
        io.log_error(message)

    return message, date


def get_all_env_names(region):
    envs = elasticbeanstalk.get_all_environments(region=region)
    return [e.name for e in envs]


def get_env_names(app_name, region):
    envs = elasticbeanstalk.get_app_environments(app_name, region)
    return [e.name for e in envs]


def get_app_version_labels(app_name, region):
    app_versions = elasticbeanstalk.get_application_versions(app_name, region)
    return [v['VersionLabel'] for v in app_versions]


def prompt_for_solution_stack(region):

    solution_stacks = elasticbeanstalk.get_available_solution_stacks(region)

    # get list of platforms
    platforms = []
    for stack in solution_stacks:
        if stack.platform not in platforms:
            platforms.append(stack.platform)

    # First check to see if we know what language the project is in
    platform = heuristics.find_language_type()

    if platform is not None:
        io.echo()
        io.echo(prompts['platform.validate'].replace('{platform}', platform))
        correct = io.get_boolean_response()

    if not platform or not correct:
        # ask for platform
        io.echo()
        io.echo(prompts['platform.prompt'])
        platform = utils.prompt_for_item_in_list(platforms)

    # filter
    solution_stacks = [x for x in solution_stacks if x.platform == platform]

    #get Versions
    versions = []
    for stack in solution_stacks:
        if stack.version not in versions:
            versions.append(stack.version)

    #now choose a version (if applicable)
    if len(versions) > 1:
        io.echo()
        io.echo(prompts['sstack.version'])
        version = utils.prompt_for_item_in_list(versions)
    else:
        version = versions[0]

    return get_latest_solution_stack(version, stack_list=solution_stacks)


def get_latest_solution_stack(platform_version, region=None, stack_list=None):
    if stack_list:
        solution_stacks = stack_list
    else:
        solution_stacks = elasticbeanstalk.\
            get_available_solution_stacks(region=region)

    #filter
    solution_stacks = [x for x in solution_stacks
                       if x.version == platform_version]

    #Lastly choose a server type
    servers = []
    for stack in solution_stacks:
        if stack.server not in servers:
            servers.append(stack.server)

    # Default to latest version of server
    # We are assuming latest is always first in list.
    if len(servers) < 1:
        raise NotFoundError(strings['sstacks.notaversion'].
                            replace('{version}', platform_version))
    server = servers[0]

    #filter
    solution_stacks = [x for x in solution_stacks if x.server == server]

    #should have 1 and only have 1 result
    assert len(solution_stacks) == 1, 'Filtered Solution Stack list ' \
                                      'contains multiple results'
    return solution_stacks[0]


def create_app(app_name, region, default_env=None):
    # Attempt to create app
    try:
        io.log_info('Creating application: ' + app_name)
        elasticbeanstalk.create_application(
            app_name,
            strings['app.description'],
            region=region
        )

        set_environment_for_current_branch(None)
        io.echo('Application', app_name,
                'has been created.')
        return None, None

    except AlreadyExistsError:
        io.log_info('Application already exists.')
        return pull_down_app_info(app_name, region, default_env=default_env)


def pull_down_app_info(app_name, region, default_env=None):
    # App exists, set up default environment
    envs = elasticbeanstalk.get_app_environments(app_name, region)
    if len(envs) == 0:
        # no envs, set None as default to override
        set_environment_for_current_branch(None)
        return None, None
    elif len(envs) == 1:
        # Set only env as default
        env = envs[0]
        io.log_info('Setting only environment "' +
                    env.name + '" as default')
    elif len(envs) > 1:
        if default_env:
            if default_env == '/ni':
                env = envs[0]
            else:
                env = next((env for env in envs if env.name == default_env),
                           None)
        if not default_env or env is None:
            # Prompt for default
            io.echo(prompts['init.selectdefaultenv'])
            env = utils.prompt_for_item_in_list(envs)

    set_environment_for_current_branch(env.name)

    io.log_info('Pulling down defaults from environment ' + env.name)
    # Get keyname
    keyname = elasticbeanstalk.get_specific_configuration_for_env(
        app_name, env.name, 'aws:autoscaling:launchconfiguration',
        'EC2KeyName', region=region
    )
    if keyname is None:
        keyname = -1
    return env.platform.name, keyname


def open_webpage_in_browser(url, ssl=False):
    io.log_info('Opening webpage with default browser.')
    if ssl:
        url = 'https://' + url
    else:
        url = 'http://' + url

    if (not fileoperations.program_is_installed('python')) or \
            utils.is_ssh():
        # python probably isn't on path
        ## try to run webbrowser internally
        import webbrowser
        webbrowser.open_new_tab(url)
    else:
        #By running as a subprocess, we can capture stdout
        from subprocess import Popen, PIPE

        Popen(['python -m webbrowser \'' + url + '\''], stderr=PIPE,
              stdout=PIPE, shell=True)


def get_application_names(region):
    app_list = elasticbeanstalk.get_all_applications(region=region)

    return [n.name for n in app_list]


def print_env_details(env, region, health=True):
    if region is None:
        region = aws.get_default_region()

    io.echo('Environment details for:', env.name)
    io.echo('  Application name:', env.app_name)
    io.echo('  Region:', region)
    io.echo('  Deployed Version:', env.version_label)
    io.echo('  Environment ID:', env.id)
    io.echo('  Platform:', env.platform)
    io.echo('  Tier:', env.tier)
    io.echo('  CNAME:', env.cname)
    io.echo('  Updated:', env.date_updated)

    if health:
        io.echo('  Status:', env.status)
        io.echo('  Health:', env.health)


def create_envvars_list(var_list):
    namespace = 'aws:elasticbeanstalk:application:environment'

    options = []
    options_to_remove = []
    for pair in var_list:
        ## validate
        if not re.match('^[\w\\_.:/+@-][^=]*=([\w\\_.:/+@-][^=]*)?$', pair):
            raise InvalidOptionsError(strings['setenv.invalidformat'])
        else:
            option_name, value = pair.split('=')
            d = {'Namespace': namespace,
                 'OptionName': option_name}

            if not value:
                options_to_remove.append(d)
            else:
                d['Value'] = value
                options.append(d)
    return options, options_to_remove


def create_app_version(app_name, region, label=None, message=None):
    cwd = os.getcwd()
    fileoperations._traverse_to_project_root()
    try:
        if heuristics.directory_is_empty():
            io.log_warning(strings['appversion.none'])
            return None
    finally:
        os.chdir(cwd)

    source_control = SourceControl.get_source_control()
    if source_control.untracked_changes_exist():
        io.log_warning(strings['sc.unstagedchanges'])

    #get version_label
    if label:
        version_label = label
    else:
        version_label = source_control.get_version_label()

    # get description
    if message:
        description = message
    else:
        description = source_control.get_message()

    if len(description) > 200:
        description = description[:195] + '...'


    # Check for zip or artifact deploy
    artifact = fileoperations.get_config_setting('deploy', 'artifact')
    if artifact:
        file_name, file_extension = os.path.splitext(artifact)
        file_name = version_label + file_extension
        file_path = artifact
    else:
        # Create zip file
        file_name = version_label + '.zip'
        file_path = fileoperations.get_zip_location(file_name)
        # Check to see if file already exists from previous attempt
        if not fileoperations.file_exists(file_path) and \
                                version_label not in \
                                get_app_version_labels(app_name, region):
            # If it doesn't already exist, create it
            io.echo(strings['appversion.create'].replace('{version}',
                                                         version_label))
            source_control.do_zip(file_path)

    # Get s3 location
    bucket = elasticbeanstalk.get_storage_location(region)
    # upload to s3
    key = app_name + '/' + file_name

    try:
        s3.get_object_info(bucket, key, region=region)
        io.log_info('S3 Object already exists. Skipping upload.')
    except NotFoundError:
        io.log_info('Uploading archive to s3 location: ' + key)
        s3.upload_application_version(bucket, key, file_path, region=region)

    fileoperations.delete_app_versions()
    io.log_info('Creating AppVersion ' + version_label)
    while True:
        try:
            elasticbeanstalk.create_application_version(
                app_name, version_label, description, bucket, key, region
            )
            return version_label
        except InvalidParameterValueError as e:
            if e.message.startswith('Application Version ') and \
                    e.message.endswith(' already exists.'):
                # we must be deploying with an existing app version
                io.log_warning('Deploying a previously deployed commit.')
                return version_label
            elif e.message == responses['app.notexists'].replace(
                    '{app-name}', '\'' + app_name + '\''):
                # App doesnt exist, must be a new region.
                ## Lets create the app in the region
                create_app(app_name, region)
            else:
                raise


def update_environment(env_name, changes, region, nohang, remove=None,
                       template=None, timeout=None, template_body=None):
    try:
        request_id = elasticbeanstalk.update_environment(
            env_name, changes, remove=remove, region=region, template=template,
            template_body=template_body)
    except InvalidStateError:
        io.log_error(prompts['update.invalidstate'])
        return
    except InvalidSyntaxError as e:
        io.log_error(prompts['update.invalidsyntax'] +
                     '\nError = ' + e.message)
        return

    if nohang:
        return

    io.echo('Printing Status:')
    try:
        wait_for_success_events(request_id, region, timeout_in_minutes=timeout)
    except TimeoutError:
        io.log_error(strings['timeout.error'])


def write_setting_to_current_branch(keyname, value):
    source_control = SourceControl.get_source_control()

    branch_name = source_control.get_current_branch()

    fileoperations.write_config_setting(
        'branch-defaults',
        branch_name,
        {keyname: value}
    )


def set_environment_for_current_branch(value):
    write_setting_to_current_branch('environment', value)


def get_setting_from_current_branch(keyname):
    source_control = SourceControl.get_source_control()

    branch_name = source_control.get_current_branch()

    branch_dict = fileoperations.get_config_setting('branch-defaults', branch_name)
    if branch_dict is None:
        return None
    else:
        try:
            return branch_dict[keyname]
        except KeyError:
            return None


def get_current_branch_environment():
    return get_setting_from_current_branch('environment')


def get_solution_stack(solution_string, region):
    #If string is explicit, do not check
    if re.match(r'^\d\dbit [\w\s]+[0-9.]* v[0-9.]+ running .*$',
                solution_string):
        return SolutionStack(solution_string)

    solution_string = solution_string.lower()
    solution_stacks = elasticbeanstalk.get_available_solution_stacks(region)

    # check for exact string
    stacks = [x for x in solution_stacks if x.name.lower() == solution_string]

    if len(stacks) == 1:
        return stacks[0]

    #should only have 1 result
    if len(stacks) > 1:
        LOG.error('Platform list contains '
                  'multiple results')
        return None

    # No exact match, check for versions
    string = solution_string.replace('-', ' ')
    # put dash back in preconfigured types
    string = re.sub('preconfigured\\s+docker', 'preconfigured - docker', string)
    string = re.sub(r'([a-z])([0-9])', '\\1 \\2', string)
    stacks = [x for x in solution_stacks if x.version.lower() == string]

    if len(stacks) > 0:
        # Give the latest version. Latest is always first in list
        return stacks[0]

    # No exact match, check for platforms
    stacks = [x for x in solution_stacks if x.platform.lower() == string]

    if len(stacks) > 0:
        # Give the latest version. Latest is always first in list
        return stacks[0]

    raise NotFoundError(prompts['sstack.invalidkey'].replace('{string}',
                                                             solution_string))


def is_cname_available(cname, region):
    return elasticbeanstalk.is_cname_available(cname, region)


def get_instance_ids(app_name, env_name, region):
    env = elasticbeanstalk.get_environment_resources(env_name, region)
    instances = [i['Id'] for i in env['EnvironmentResources']['Instances']]
    return instances


def upload_keypair_if_needed(region, keyname):
    keys = [k['KeyName'] for k in ec2.get_key_pairs(region=region)]
    if keyname in keys:
        return

    key_material = _get_public_ssh_key(keyname)

    try:
        ec2.import_key_pair(keyname, key_material, region=region)
    except AlreadyExistsError:
        return
    if region is None:
        region = aws.get_default_region()
    io.log_warning(strings['ssh.uploaded'].replace('{keyname}', keyname)
                   .replace('{region}', region))


def _get_public_ssh_key(keypair_name):
    key_file = fileoperations.get_ssh_folder() + keypair_name
    if os.path.exists(key_file):
        file_name = key_file
    elif os.path.exists(key_file + '.pem'):
        file_name = key_file + '.pem'
    else:
        raise NotSupportedError(strings['ssh.filenotfound'].replace(
            '{key-name}', keypair_name))

    try:
        stdout, stderr, returncode = exec_cmd(['ssh-keygen', '-y', '-f',
                                           file_name])
        if returncode != 0:
            raise CommandError('An error occurred while trying '
                               'to get ssh public key')
        key_material = stdout
        return key_material
    except OSError:
        CommandError(strings['ssh.notpresent'])