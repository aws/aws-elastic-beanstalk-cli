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

from six.moves import urllib
from six import iteritems
from cement.utils.misc import minimal_logger
from cement.utils.shell import exec_cmd, exec_cmd2

from ebcli.lib import elasticbeanstalk, s3, iam, aws, ec2
from ebcli.core import fileoperations, io
from ebcli.objects.sourcecontrol import SourceControl
from ebcli.resources.strings import strings, responses, prompts
from ebcli.objects import region as regions
from ebcli.lib import utils
from ebcli.objects import configuration
from ebcli.objects.exceptions import NoSourceControlError, \
    ServiceError, TimeoutError, CredentialsError, InvalidStateError, \
    AlreadyExistsError, InvalidSyntaxError, NotFoundError
from ebcli.objects.solutionstack import SolutionStack
from ebcli.objects.tier import Tier
from ebcli.lib.aws import InvalidParameterValueError
from ebcli.lib import heuristics

LOG = minimal_logger(__name__)
DEFAULT_ROLE_NAME = 'aws-elasticbeanstalk-ec2-role'


def wait_and_print_events(request_id, region,
                          timeout_in_seconds=60*10, sleep_time=5):
    start = datetime.now()
    timediff = timedelta(seconds=timeout_in_seconds)

    finished = False
    last_time = ''

    #Get first events
    events = []
    while not events:
        events = elasticbeanstalk.get_new_events(
            None, None, request_id, last_event_time='', region=region
        )

        if len(events) > 0:
            event = events[-1]
            app_name = event.app_name
            env_name = event.environment_name

            log_event(event)
            # Test event message for success string
            finished = _is_success_string(event.message)
            last_time = event.event_date
        else:
            time.sleep(sleep_time)

    while not finished and (datetime.now() - start) < timediff:
        time.sleep(sleep_time)

        events = elasticbeanstalk.get_new_events(
            app_name, env_name, None, last_event_time=last_time, region=region
        )

        for event in reversed(events):
            log_event(event)

            # Test event message for success string
            finished = _is_success_string(event.message)
            last_time = event.event_date

            if finished:
                break

    if not finished:
        raise TimeoutError('Timed out while waiting for command to CompleterController')


def _is_success_string(message):
    if message == responses['event.greenmessage']:
        return True
    if message.startswith(responses['event.launchsuccess']):
        return True
    if message == responses['event.redmessage']:
        raise ServiceError(message)
    if message.startswith(responses['event.launchbad']):
        raise ServiceError(message)
    if message == responses['logs.pulled']:
        return True
    if message == responses['env.terminated']:
        return True
    if message == responses['env.updatesuccess']:
        return True
    if message == responses['app.deletesuccess']:
        return True
    if responses['logs.successtail'] in message:
        return True
    if responses['logs.successbundle'] in message:
        return True

    return False


def log_event(event, echo=False):
    message = event.message
    severity = event.severity
    date = event.event_date
    if echo:
        io.echo(date.ljust(26) + severity.ljust(8) + message)
    elif severity == 'INFO':
        io.echo('INFO:', message)
    elif severity == 'WARN':
        io.log_warning(message)
    elif severity == 'ERROR':
        io.log_error(message)

    return message, date


def print_events(app_name, env_name, region, follow):
    if follow:
        io.echo(prompts['events.hanging'])
    last_time = ''
    while True:
        events = elasticbeanstalk.get_new_events(
            app_name, env_name, None, last_event_time=last_time, region=region
        )

        for event in reversed(events):
            log_event(event, echo=True)
            last_time = event.event_date

        if follow:
            time.sleep(4)
        else:
            break


def get_env_names(app_name, region):
    envs = elasticbeanstalk.get_all_environments(app_name, region)
    return [e.name for e in envs if not e.status == 'Terminated']


def list_env_names(app_name, region, verbose):
    current_env = get_setting_from_current_branch('environment')
    env_names = get_env_names(app_name, region)
    env_names.sort()

    if verbose:
        io.echo('Application:', app_name)
        io.echo('    Environments:', len(env_names))
        for e in env_names:
            instances = get_instance_ids(app_name, e, region)
            if e == current_env:
                e = '* ' + e

            io.echo('       ', e, ':', instances)

    else:
        for i in range(0, len(env_names)):
            if env_names[i] == current_env:
                env_names[i] = '* ' + env_names[i]

        if len(env_names) <= 10:
            for e in env_names:
                io.echo(e)
        else:
            utils.print_list_in_columns(env_names)


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
        correct = get_boolean_response()

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

    #filter
    solution_stacks = [x for x in solution_stacks if x.version == version]

    #Lastly choose a server type
    servers = []
    for stack in solution_stacks:
        if stack.server not in servers:
            servers.append(stack.server)

    # Default to latest version of server
    # We are assuming latest is always first in list.
    server = servers[0]

    #filter
    solution_stacks = [x for x in solution_stacks if x.server == server]

    #should have 1 and only have 1 result
    assert len(solution_stacks) == 1, 'Filtered Solution Stack list '\
                                      'contains multiple results'
    return solution_stacks[0]


def credentials_are_valid(region):
    try:
        elasticbeanstalk.get_available_solution_stacks(region)
        return True
    except CredentialsError:
        return False


def setup(app_name, region, solution, keyname):
    setup_directory(app_name, region, solution, keyname)

    create_app(app_name, region)

    try:
        setup_ignore_file()
    except NoSourceControlError:
        io.log_warning(strings['sc.notfound'])


def setup_credentials():
    io.log_info('Setting up ~/aws/ directory with config file')

    io.echo(strings['cred.prompt'])

    access_key = io.prompt('aws-access-id', default='ENTER_AWS_ACCESS_ID_HERE')
    secret_key = io.prompt('aws-secret-key', default='ENTER_SECRET_HERE')

    fileoperations.save_to_aws_config(access_key, secret_key)
    fileoperations.write_config_setting('global', 'profile', 'eb-cli')

    aws.set_session_creds(access_key, secret_key)


def create_app(app_name, region):
    # Attempt to create app
    try:
        io.log_info('Creating application: ' + app_name)
        elasticbeanstalk.create_application(
            app_name,
            strings['app.description'],
            region=region
        )

        io.echo('Application', app_name,
                'has been created')

    except AlreadyExistsError:
        io.log_info('Application already exists.')
        # App exists, do nothing
        pass


def get_default_profile(region):
    """  Get the default elasticbeanstalk IAM profile,
            Create it if it doesn't exist """

    # get list of profiles
    profile_names = iam.get_instance_profile_names(region=region)
    profile = DEFAULT_ROLE_NAME
    if profile not in profile_names:
        iam.create_instance_profile(profile)

    return profile


def open_app(app_name, env_name, region):
    # get cname
    env = elasticbeanstalk.get_environment(app_name, env_name, region)

    open_webpage_in_browser(env.cname)


def open_console(app_name, env_name, region):
    #Get environment id
    env = elasticbeanstalk.get_environment(app_name, env_name, region)

    console_url = 'console.aws.amazon.com/elasticbeanstalk/home?region' +\
                region + \
                '#/environment/dashboard?applicationName=' + app_name + \
                  '&environmentId=' + env.id

    open_webpage_in_browser(console_url, ssl=True)


def open_webpage_in_browser(url, ssl=False):
    io.log_info('Opening webpage with default browser')
    if ssl:
        url = 'https://' + url
    else:
        url = 'http://' + url

    stdout, stderr, exitcode = \
        exec_cmd(['python -m webbrowser \'' + url + '\''], shell=True)

    LOG.debug('browser stdout: ' + stdout)
    LOG.debug('browser stderr: ' + stderr)
    LOG.debug('browser exitcode: ' + str(exitcode))

    if exitcode == 127:
        # python probably isn't on path
        ## try to run webbrowser internally
        import webbrowser
        webbrowser.open(url)


def get_application_names(region):
    app_list = elasticbeanstalk.get_all_applications(region=region)

    return [n.name for n in app_list]


def scale(app_name, env_name, number, confirm, region):
    options = []
    # get environment
    env = elasticbeanstalk.describe_configuration_settings(
        app_name, env_name, region
    )['OptionSettings']

    # if single instance, offer to switch to load-balanced
    namespace = 'aws:elasticbeanstalk:environment'
    setting = next((n for n in env if n["Namespace"] == namespace), None)
    value = setting['Value']
    if value == 'SingleInstance':
        if not confirm:
            ## prompt to switch to LoadBalanced environment type
            io.echo(prompts['scale.switchtoloadbalance'])
            switch = get_boolean_response()
            if not switch:
                return

        options.append({'Namespace': namespace,
                        'OptionName': 'EnvironmentType',
                        'Value': 'LoadBalanced'})

    # change autoscaling min AND max to number
    namespace = 'aws:autoscaling:asg'
    max = 'MaxSize'
    min = 'MinSize'

    for name in [max, min]:
        options.append(
            {'Namespace': namespace,
             'OptionName': name,
             'Value': str(number)
             }
        )
    request_id = elasticbeanstalk.update_environment(env_name, options, region)
    try:
        wait_and_print_events(request_id, region, timeout_in_seconds=60*5)
    except TimeoutError:
        io.log_error(strings['timeout.error'])


def make_new_env(app_name, env_name, region, cname, solution_stack, tier,
                 label, profile, single, key_name, branch_default,
                 sample, nohang):
    if profile is None:
        # Service supports no profile, however it is not good/recommended
        # Get the eb default profile
        profile = get_default_profile(region)

    # deploy code
    if not sample and not label:
        io.log_info('Creating new application version using project code')
        label = create_app_version(app_name, region)

    # Create env
    io.log_info('Creating new environment')
    result, request_id = create_env(app_name, env_name, region, cname,
                                    solution_stack, tier, label, single,
                                    key_name, profile)

    env_name = result.name  # get the (possibly) updated name

    # Edit configurations
    ## Get default environment
    default_env = get_setting_from_current_branch('environment')
    ## Save env as branch default if needed
    if not default_env or branch_default:
        write_setting_to_current_branch('environment', env_name)

    # Print status of env
    print_env_details(result, health=False)

    if nohang:
        return

    io.echo('Printing Status:')
    try:
        wait_and_print_events(request_id, region)
    except TimeoutError:
        io.log_error(strings['timeout.error'])


def print_env_details(env, health=True, verbose=False):

    io.echo('Environment details for:', env.name)
    io.echo('  App name:', env.app_name)
    io.echo('  Environment ID:', env.id)
    io.echo('  Solution Stack:', env.solution_stack)
    io.echo('  Tier:', env.tier)
    io.echo('  Cname:', env.cname)
    io.echo('  Updated:', env.date_updated)

    if health:
        io.echo('  Status:', env.status)
        io.echo('  Health:', env.health)


def create_env(app_name, env_name, region, cname, solution_stack,
               tier, label, single, key_name, profile):
    description = strings['env.description']

    try:
        return elasticbeanstalk.create_environment(
            app_name, env_name, cname, description, solution_stack,
            tier, label, single, key_name, profile, region=region)

    except InvalidParameterValueError as e:
        LOG.debug('creating env returned error: ' + e.message)
        if re.match(responses['env.cnamenotavailable'], e.message):
            io.echo(prompts['cname.unavailable'])
            cname = io.prompt_for_cname()
        elif re.match(responses['env.nameexists'], e.message):
            io.echo(strings['env.exists'])
            current_environments = get_env_names(app_name, region)
            unique_name = utils.get_unique_name(env_name,
                                                current_environments)
            env_name = io.prompt_for_environment_name(default_name=unique_name)
        else:
            raise e

        # Try again with new values
        return create_env(app_name, env_name, region, cname, solution_stack,
                          tier, label, single, key_name, profile)


def make_cloned_env(app_name, env_name, clone_name, cname, region, nohang):
    io.log_info('Cloning environment')
    result, request_id = clone_env(app_name, env_name, clone_name,
                                   cname, region)

    # Print status of env
    print_env_details(result, health=False)

    if nohang:
        return

    io.echo('Printing Status:')
    try:
        wait_and_print_events(request_id, region)
    except TimeoutError:
        io.log_error(strings['timeout.error'])


def clone_env(app_name, env_name, clone_name, cname, region):
    description = strings['env.clonedescription'].replace('{env-name}',
                                                          env_name)

    try:
        return elasticbeanstalk.clone_environment(
            app_name, env_name, clone_name, cname, description, region=region)

    except InvalidParameterValueError as e:
        LOG.debug('cloning env returned error: ' + e.message)
        if re.match(responses['env.cnamenotavailable'], e.message):
            io.echo(prompts['cname.unavailable'])
            cname = io.prompt_for_cname()
        elif re.match(responses['env.nameexists'], e.message):
            io.echo(strings['env.exists'])
            current_environments = get_env_names(app_name, region)
            unique_name = utils.get_unique_name(clone_name,
                                                current_environments)
            clone_name = io.prompt_for_environment_name(default_name=unique_name)
        else:
            raise e

        #try again
        clone_env(app_name, env_name, clone_name, cname, region)


def delete_app(app_name, region, force):
    app = elasticbeanstalk.describe_application(app_name, region)

    if not force:
        #Confirm
        envs = get_env_names(app_name, region)
        confirm_message = prompts['delete.confirm'].replace(
            '{app-name}', app_name)
        confirm_message = confirm_message.replace('{env-num}', str(len(envs)))
        confirm_message = confirm_message.replace(
            '{config-num}', str(len(app['ConfigurationTemplates'])))
        confirm_message = confirm_message.replace(
            '{version-num}', str(len(app['Versions'])))
        io.echo()
        io.echo(confirm_message)
        result = io.get_input('Enter application name as shown to confirm')

        if result != app_name:
            io.log_error('Names do not match. Exiting')
            return


    request_id = elasticbeanstalk.delete_application_and_envs(app_name,
                                                                  region)

    cleanup_ignore_file()
    fileoperations.clean_up()
    wait_and_print_events(request_id, region, sleep_time=1,
                          timeout_in_seconds=60*5)


def deploy(app_name, env_name, region):
    if region:
        region_name = region
    else:
        region_name = 'DEFAULT'

    io.log_info('Deploying code to ' + env_name + " in region " + region_name)

    # Create app version
    app_version_label = create_app_version(app_name, region)

    # swap env to new app version
    request_id = elasticbeanstalk.update_env_application_version(env_name,
                                                    app_version_label, region)

    wait_and_print_events(request_id, region, 60*5)


def status(app_name, env_name, region, verbose):
    env = elasticbeanstalk.get_environment(app_name, env_name, region)
    print_env_details(env, True)

    if verbose:
        # Print number of running instances
        instances = get_instance_ids(app_name, env_name, region)
        io.echo('  Running instances:', len(instances))

        # Print environment Variables
        settings = elasticbeanstalk.describe_configuration_settings(
            app_name, env_name, region
        )['OptionSettings']
        namespace = 'aws:elasticbeanstalk:application:environment'
        vars = {n['OptionName']: n['Value'] for n in settings
                if n["Namespace"] == namespace}
        io.echo('  Environment Variables:')
        for key, value in vars.iteritems():
            key, value = utils.mask_vars(key, value)
            io.echo('       ', key, '=', value)


def logs(env_name, info_type, region, zip=False):
    # Request info
    result = elasticbeanstalk.request_environment_info(env_name, info_type,
                                                       region=region)

    # Wait for logs to finish
    request_id = result['ResponseMetadata']['RequestId']
    wait_and_print_events(request_id, region,
                        timeout_in_seconds=60*2, sleep_time=1)

    get_logs(env_name, info_type, region, zip=zip)


def get_logs(env_name, info_type, region, zip=False):
    # Get logs
    result = elasticbeanstalk.retrieve_environment_info(env_name, info_type,
                                                        region)

    """
    Results are ordered with latest last, we just want the latest
    """
    log_list = {}
    for log in result['EnvironmentInfo']:
        instance_id = log['Ec2InstanceId']
        url = log['Message']
        log_list[instance_id] = url

    if info_type == 'bundle':
        # save file, unzip, place in logs directory
        logs_folder_name = datetime.now().strftime("%y%m%d_%H%M%S")
        logs_location = fileoperations.get_logs_location(logs_folder_name)
        for instance_id, url in iteritems(log_list):
            zip_location = save_file_from_url(url, logs_location,
                                              instance_id + '.zip')
            instance_folder = os.path.join(logs_location, instance_id)
            fileoperations.upzip_folder(zip_location, instance_folder)
            fileoperations.delete_file(zip_location)

        if zip:
            fileoperations.zip_up_folder(logs_location, logs_location + '.zip')
            fileoperations.delete_directory(logs_location)
            logs_location += '.zip'

        io.echo('Logs saved at', logs_location)

    else:
        # print logs
        for instance_id, url in iteritems(log_list):
            io.echo('================', instance_id, '=================')
            print_from_url(url)


def setenv(app_name, env_name, var_list, region):
    namespace = 'aws:elasticbeanstalk:application:environment'

    options = []
    options_to_remove = []
    for pair in var_list:
        ## validate
        if not re.match('^[\w\\_.:/+-@][^=]*=([\w\\_.:/+-@][^=]*)?$', pair):
            io.log_error('Must use format VAR_NAME=KEY. Variable and keys '
                         'cannot contain any spaces or =. They must start'
                         ' with a letter, number or one of \\_.:/+-@')
            return
        else:
            option_name, value = pair.split('=')
            d = {'Namespace': namespace,
                 'OptionName': option_name}

            if not value:
                options_to_remove.append(d)
            else:
                d['Value'] = value
                options.append(d)

    result = elasticbeanstalk.update_environment(env_name, options, region,
                                                 remove=options_to_remove)
    try:
        request_id = result
        wait_and_print_events(request_id, region, timeout_in_seconds=60*4)
    except TimeoutError:
        io.log_error('Unknown state of environment. Operation timed out.')


def print_from_url(url):
    result = urllib.request.urlopen(url).read()
    io.echo(result)

def save_file_from_url(url, location, filename):
    result = urllib.request.urlopen(url).read()

    return fileoperations.save_to_file(result, location, filename)


def terminate(env_name, region):
    request_id = elasticbeanstalk.terminate_environment(env_name, region)

    # disassociate with branch if branch default
    ## Get default environment
    default_env = get_setting_from_current_branch('environment')
    if default_env == env_name:
        write_setting_to_current_branch('environment', None)

    wait_and_print_events(request_id, region,
                        timeout_in_seconds=60*5)


def ssh_into_instance(instance_id, region):
    instance = ec2.describe_instance(instance_id, region)
    keypair_name = instance['KeyName']
    ip = instance['PublicIpAddress']

    user = 'ec2-user'

    ident_file = fileoperations.get_ssh_folder() + keypair_name
    if not os.path.exists(ident_file):
        if os.path.exists(ident_file + '.pem'):
            ident_file += '.pem'
        else:
            raise NotFoundError(strings['ssh.filenotfound'].replace(
                '{key-name}', keypair_name)
            )

    returncode = exec_cmd2('ssh -i ' + ident_file + ' ' + user + '@' + ip,
                           shell=True)

    if returncode != 0:
        io.log_error(strings['ssh.notpresent'])


def save_env_file(api_model):
    usr_model = configuration.convert_api_to_usr_model(api_model)
    file_location = fileoperations.save_env_file(usr_model)
    return file_location


def open_file_for_editing(file_location):

    editor = fileoperations.get_editor()
    if editor:
        try:
            os.system(editor + ' ' + file_location)
        except OSError:
            io.log_error(prompts['fileopen.error1'].replace('{editor}',
                                                            editor))
    else:
        try:
            os.system(file_location)
        except OSError:
            io.log_error(prompts['fileopen.error2'])


def setup_directory(app_name, region, solution, keyname):
    io.log_info('Setting up .elasticbeanstalk directory')
    fileoperations.create_config_file(app_name, region, solution)
    fileoperations.write_config_setting('global', 'default_ec2_keyname',
                                        keyname)


def setup_ignore_file():
    io.log_info('Setting up ignore file for source control')
    sc = fileoperations.get_config_setting('global', 'sc')

    if not sc:
        source_control = SourceControl.get_source_control()
        source_control.set_up_ignore_file()
        sc_name = source_control.get_name()
        fileoperations.write_config_setting('global', 'sc', sc_name)


def cleanup_ignore_file():
    sc = fileoperations.get_config_setting('global', 'sc')

    if sc:
        source_control = SourceControl.get_source_control()
        source_control.clean_up_ignore_file()
        fileoperations.write_config_setting('global', 'sc', None)


def create_app_version(app_name, region):
    #get version_label
    source_control = SourceControl.get_source_control()
    version_label = source_control.get_version_label()

    #get description
    description = source_control.get_message()
    io.log_info('Creating app_version archive' + version_label)

    # Create zip file
    file_name = version_label + '.zip'
    file_path = fileoperations.get_zip_location(file_name)
    source_control.do_zip(file_path)

    # Get s3 location
    bucket = elasticbeanstalk.get_storage_location(region)
    # upload to s3
    key = app_name + '/' + file_name

    io.log_info('Uploading archive to s3 location: ' + key)
    s3.upload_application_version(bucket, key, file_path,
                                                region=region)
    fileoperations.delete_app_versions()
    try:
        io.log_info('Creating AppVersion ' + version_label)
        elasticbeanstalk.create_application_version(
            app_name, version_label, description, bucket, key, region
        )
    except InvalidParameterValueError as e:
        if e.message.startswith('Application Version ') and \
                e.message.endswith(' already exists.'):
            # we must be deploying with an existing app version
            io.log_warning('Deploying a previously deployed commit')
    return version_label


def update_environment(app_name, env_name, region, nohang):
    #get environment setting
    api_model = elasticbeanstalk.describe_configuration_settings(
        app_name, env_name, region=region
    )

    # Turn them into a yaml file and open
    file_location = save_env_file(api_model)
    open_file_for_editing(file_location)

    # Update and delete file
    try:
        usr_model = fileoperations.get_environment_from_file(env_name)
        changes, remove = configuration.collect_changes(api_model, usr_model)
        fileoperations.delete_env_file(env_name)
    except InvalidSyntaxError:
        io.log_error(prompts['update.invalidsyntax'])
        return

    if not changes and not remove:
        # no changes made, exit
        io.log_warning('No changes made. Exiting.')
        return

    try:
        request_id = elasticbeanstalk.update_environment(env_name, changes,
                                                         region=region,
                                                         remove=remove)
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
        wait_and_print_events(request_id, region)
    except TimeoutError:
        io.log_error(strings['timeout.error'])


def get_boolean_response():
    response = io.prompt('y/n', default='y').lower()
    while response not in ('y', 'n', 'yes', 'no'):
        io.echo(strings['prompt.invalid'],
                             strings['prompt.yes-or-no'])
        response = io.prompt('y/n').lower()

    if response in ('y', 'yes'):
        return True
    else:
        return False


def write_setting_to_current_branch(keyname, value):
    source_control = SourceControl.get_source_control()

    branch_name = source_control.get_current_branch()

    fileoperations.write_config_setting(
        'branch-defaults',
        branch_name,
        {keyname: value}
    )


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


def prompt_for_ec2_keyname(region):
    io.echo('Would you like to set up ssh for your instances?')
    ssh = get_boolean_response()

    if not ssh:
        return None

    keys = ec2.get_key_pairs(region)

    if len(keys) < 1:
        keyname = _generate_and_upload_keypair(region)

    else:
        keys = [k['KeyName'] for k in keys]
        new_key_option = '[ Create new KeyPair ]'
        keys.append(new_key_option)
        io.echo()
        io.echo('Choose a keypair')
        keyname = utils.prompt_for_item_in_list(keys, default=len(keys))

        if keyname == new_key_option:
            keyname = _generate_and_upload_keypair(region, keys)

    return keyname

def select_tier():
    tier_list = Tier.get_latest_tiers()
    io.echo('Please choose a tier')
    tier = utils.prompt_for_item_in_list(tier_list)
    return tier


def get_solution_stack(solution_string, region):
    return elasticbeanstalk.get_solution_stack(solution_string, region)


def is_cname_available(cname, region):
    return elasticbeanstalk.is_cname_available(cname, region)


def get_instance_ids(app_name, env_name, region):
    env = elasticbeanstalk.get_environment_resources(env_name, region)
    instances = [i['Id'] for i in env['EnvironmentResources']['Instances']]
    return instances



def _generate_and_upload_keypair(region, keys):
    # Get filename
    io.echo()
    io.echo('Enter keypair name')
    unique = utils.get_unique_name('aws-eb', keys)
    keyname = io.prompt('Default is ' + unique, default=unique)
    file_name = fileoperations.get_ssh_folder() + keyname

    exitcode = exec_cmd2('ssh-keygen -f ' + file_name, shell=True)

    if exitcode != 0:
        LOG.debug('ssh-keygen returned exitcode: ' + str(exitcode) +
                   ' with filename: ' + file_name)
        io.log_error(strings['ssh.notpresent'])
        return None
    else:
        key_material = open(file_name + '.pub', 'r').read()
        ec2.import_key_pair(keyname, key_material, region=region)

        return keyname