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
import subprocess

from six.moves import urllib
from six import iteritems
from cement.utils.misc import minimal_logger
from cement.utils.shell import exec_cmd, exec_cmd2

from ..lib import elasticbeanstalk, s3, iam, aws, ec2, elb
from ..core import fileoperations, io
from ..objects.sourcecontrol import SourceControl
from ..resources.strings import strings, responses, prompts
from ..objects import region as regions
from ..lib import utils
from ..objects import configuration
from ..objects.exceptions import *
from ..objects.solutionstack import SolutionStack
from ..objects.tier import Tier
from ..lib.aws import InvalidParameterValueError
from ..lib import heuristics

LOG = minimal_logger(__name__)
DEFAULT_ROLE_NAME = 'aws-elasticbeanstalk-ec2-role'


def wait_and_print_events(request_id, region,
                          timeout_in_seconds=60*10, sleep_time=5):
    start = datetime.now()
    timediff = timedelta(seconds=timeout_in_seconds)

    finished = False
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
        io.echo(date.strftime("%Y-%m-%d %H:%M:%S").ljust(23),
                severity.ljust(7), message)
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
    last_time = None
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


def get_all_env_names(region):
    envs = elasticbeanstalk.get_all_environments(region=region)
    return [e.name for e in envs]


def get_env_names(app_name, region):
    envs = elasticbeanstalk.get_app_environments(app_name, region)
    return [e.name for e in envs]


def list_env_names(app_name, region, verbose, all_apps):
    if region is None:
        region = aws.get_default_region()

    if verbose:
        io.echo('Region:', region)

    if all_apps:
        for app_name in get_application_names(region):
            list_env_names_for_app(app_name, region, verbose)
    else:
        list_env_names_for_app(app_name, region, verbose)


def list_env_names_for_app(app_name, region, verbose):
    current_env = get_current_branch_environment()
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
    except NotAuthorizedError:
        io.log_error('The current user does not have the correct permissions.')
        return False


def setup(app_name, region, solution):
    setup_directory(app_name, region, solution)

    # Handle tomcat special case
    if 'tomcat' in solution.lower() and \
            heuristics.has_tomcat_war_file():
        war_file = fileoperations.get_war_file_location()
        fileoperations.write_config_setting('deploy', 'artifact', war_file)

    try:
        setup_ignore_file()
    except NoSourceControlError:
        # io.log_warning(strings['sc.notfound'])
        pass


def setup_credentials(access_id=None, secret_key=None):
    io.log_info('Setting up ~/aws/ directory with config file')

    if access_id is None or secret_key is None:
        io.echo(strings['cred.prompt'])

    if access_id is None:
        access_id = io.prompt('aws-access-id',
                              default='ENTER_AWS_ACCESS_ID_HERE')
    if secret_key is None:
        secret_key = io.prompt('aws-secret-key', default='ENTER_SECRET_HERE')

    fileoperations.save_to_aws_config(access_id, secret_key)

    fileoperations.touch_config_folder()
    fileoperations.write_config_setting('global', 'profile', 'eb-cli')

    aws.set_session_creds(access_id, secret_key)


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


def get_default_profile(region):
    """  Get the default elasticbeanstalk IAM profile,
            Create it if it doesn't exist """

    # get list of profiles
    try:
        profile = DEFAULT_ROLE_NAME
        try:
            iam.create_instance_profile(profile, region=region)
            role = get_default_role(region)
            iam.add_role_to_profile(profile, role, region=region)
        except AlreadyExistsError:
            pass
    except NotAuthorizedError:
        # Not a root account. Just assume role exists
        return DEFAULT_ROLE_NAME

    return profile


def get_default_role(region):
    role = DEFAULT_ROLE_NAME
    document = '{"Version": "2008-10-17","Statement": [{"Action":' \
               ' "sts:AssumeRole","Principal": {"Service": ' \
               '"ec2.amazonaws.com"},"Effect": "Allow","Sid": ""}]}'
    try:
        iam.create_role(role, document, region=region)
    except AlreadyExistsError:
        pass
    return role


def open_app(app_name, env_name, region):
    # get cname
    env = elasticbeanstalk.get_environment(app_name, env_name, region)

    open_webpage_in_browser(env.cname)


def open_console(app_name, env_name, region):
    if utils.is_ssh():
        raise NotSupportedError('The console command is not supported'
                                ' in an ssh type session')

    #Get environment id
    env = None
    if env_name is not None:
        env = elasticbeanstalk.get_environment(app_name, env_name, region)

    if env is not None:
        page = 'environment/dashboard'
    else:
        page = 'application/overview'

    #encode app name
    app_name = urllib.parse.quote(app_name)

    console_url = 'console.aws.amazon.com/elasticbeanstalk/home?'
    if region:
        console_url += 'region=' + region
    console_url += '#/' + page + '?applicationName=' + app_name

    if env is not None:
        console_url += '&environmentId=' + env.id

    open_webpage_in_browser(console_url, ssl=True)


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
            io.log_warning(prompts['scale.switchtoloadbalancewarn'])
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
                 itype, label, profile, single, key_name, branch_default,
                 sample, tags, size, database, vpc, nohang, interactive=True):
    if profile is None:
        # Service supports no profile, however it is not good/recommended
        # Get the eb default profile
        profile = get_default_profile(region)

    # deploy code
    if not sample and not label:
        io.log_info('Creating new application version using project code')
        label = create_app_version(app_name, region)

    # Create env
    if key_name:
        upload_keypair_if_needed(region, key_name)

    io.log_info('Creating new environment')
    result, request_id = create_env(app_name, env_name, region, cname,
                                    solution_stack, tier, itype, label, single,
                                    key_name, profile, tags, size, database,
                                    vpc, interactive=interactive)

    env_name = result.name  # get the (possibly) updated name

    # Edit configurations
    ## Get default environment
    default_env = get_current_branch_environment()
    ## Save env as branch default if needed
    if not default_env or branch_default:
        set_environment_for_current_branch(env_name)

    # Print status of env
    print_env_details(result, region, health=False)

    if nohang:
        return

    io.echo('Printing Status:')
    try:
        wait_and_print_events(request_id, region)
    except TimeoutError:
        io.log_error(strings['timeout.error'])


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


def create_env(app_name, env_name, region, cname, solution_stack, tier, itype,
               label, single, key_name, profile, tags, size, database, vpc,
               interactive=True):
    description = strings['env.description']
    while True:
        try:
            return elasticbeanstalk.create_environment(
                app_name, env_name, cname, description, solution_stack,
                tier, itype, label, single, key_name, profile, tags,
                region=region, database=database, vpc=vpc, size=size)

        except InvalidParameterValueError as e:
            if e.message == responses['app.notexists'].replace(
                '{app-name}', '\'' + app_name + '\''):
                # App doesnt exist, must be a new region.
                ## Lets create the app in the region
                create_app(app_name, region)
            elif interactive:
                LOG.debug('creating env returned error: ' + e.message)
                if re.match(responses['env.cnamenotavailable'], e.message):
                    io.echo(prompts['cname.unavailable'])
                    cname = io.prompt_for_cname()
                elif re.match(responses['env.nameexists'], e.message):
                    io.echo(strings['env.exists'])
                    current_environments = get_all_env_names(region)
                    unique_name = utils.get_unique_name(env_name,
                                                        current_environments)
                    env_name = io.prompt_for_environment_name(
                        default_name=unique_name)
                elif e.message == responses['app.notexists'].replace(
                        '{app-name}', '\'' + app_name + '\''):
                    # App doesnt exist, must be a new region.
                    ## Lets create the app in the region
                    create_app(app_name, region)
                else:
                    raise
            else:
                raise

        # Try again with new values


def make_cloned_env(app_name, env_name, clone_name, cname, scale, tags, region,
                    nohang):
    io.log_info('Cloning environment')
    # get app version from environment
    env = elasticbeanstalk.get_environment(app_name, env_name, region)
    label = env.version_label
    result, request_id = clone_env(app_name, env_name, clone_name,
                                   cname, label, scale, tags, region)

    # Print status of env
    print_env_details(result, region, health=False)

    if nohang:
        return

    io.echo('Printing Status:')
    try:
        wait_and_print_events(request_id, region)
    except TimeoutError:
        io.log_error(strings['timeout.error'])


def clone_env(app_name, env_name, clone_name, cname, label, scale,
              tags, region):
    description = strings['env.clonedescription'].replace('{env-name}',
                                                          env_name)

    while True:
        try:
            return elasticbeanstalk.clone_environment(
                app_name, env_name, clone_name, cname, description, label,
                scale, tags, region=region)

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
                clone_name = io.prompt_for_environment_name(
                    default_name=unique_name)
            else:
                raise e

        #try again


def delete_app(app_name, region, force, nohang=False, cleanup=True):
    app = elasticbeanstalk.describe_application(app_name, region)

    if 'Versions' not in app:
        app['Versions'] = []

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
        io.validate_action(prompts['delete.validate'], app_name)


    request_id = elasticbeanstalk.delete_application_and_envs(app_name,
                                                                  region)

    if cleanup:
        cleanup_ignore_file()
        fileoperations.clean_up()
    if not nohang:
        wait_and_print_events(request_id, region, sleep_time=1,
                              timeout_in_seconds=60*15)


def deploy(app_name, env_name, region, version, label, message):
    if region:
        region_name = region
    else:
        region_name = 'DEFAULT'

    io.log_info('Deploying code to ' + env_name + " in region " + region_name)

    if version:
        app_version_label = version
    else:
        # Create app version
        app_version_label = create_app_version(app_name, region,
                                               label=label, message=message)

    # swap env to new app version
    request_id = elasticbeanstalk.update_env_application_version(env_name,
                                                    app_version_label, region)

    wait_and_print_events(request_id, region, 60*5)


def status(app_name, env_name, region, verbose):
    env = elasticbeanstalk.get_environment(app_name, env_name, region)
    print_env_details(env, region, health=True)

    if verbose:
        # Print number of running instances
        env = elasticbeanstalk.get_environment_resources(env_name, region)
        instances = [i['Id'] for i in env['EnvironmentResources']['Instances']]
        io.echo('  Running instances:', len(instances))
        #Get elb health
        try:
            load_balancer_name = [i['Name'] for i in
                              env['EnvironmentResources']['LoadBalancers']][0]
            instance_states = elb.get_health_of_instances(load_balancer_name,
                                                          region=region)
            for i in instance_states:
                instance_id = i['InstanceId']
                state = i['State']
                descrip = i['Description']
                if state == 'Unknown':
                    state += '(' + descrip + ')'
                io.echo('     ', instance_id + ':', state)
            for i in instances:
                if i not in [x['InstanceId'] for x in instance_states]:
                    io.echo('     ', i + ':', 'N/A (Not registered '
                                              'with Load Balancer)')

        except (IndexError, KeyError, NotFoundError):
            #No load balancer. Dont show instance status
            pass


def print_environment_vars(app_name, env_name, region):
    settings = elasticbeanstalk.describe_configuration_settings(
        app_name, env_name, region
    )['OptionSettings']
    namespace = 'aws:elasticbeanstalk:application:environment'
    vars = {n['OptionName']: n['Value'] for n in settings
            if n["Namespace"] == namespace}
    io.echo(' Environment Variables:')
    for key, value in iteritems(vars):
        key, value = utils.mask_vars(key, value)
        io.echo('    ', key, '=', value)


def logs(env_name, info_type, region, do_zip=False, instance_id=None):
    # Request info
    result = elasticbeanstalk.request_environment_info(env_name, info_type,
                                                       region=region)

    # Wait for logs to finish
    request_id = result['ResponseMetadata']['RequestId']
    wait_and_print_events(request_id, region,
                        timeout_in_seconds=60*2, sleep_time=1)

    get_logs(env_name, info_type, region, do_zip=do_zip,
             instance_id=instance_id)


def get_logs(env_name, info_type, region, do_zip=False, instance_id=None):
    # Get logs
    result = elasticbeanstalk.retrieve_environment_info(env_name, info_type,
                                                        region)

    """
    Results are ordered with latest last, we just want the latest
    """
    log_list = {}
    for log in result['EnvironmentInfo']:
        i_id = log['Ec2InstanceId']
        url = log['Message']
        log_list[i_id] = url

    if instance_id:
        log_list = {instance_id: log_list[instance_id]}

    if info_type == 'bundle':
        # save file, unzip, place in logs directory
        logs_folder_name = datetime.now().strftime("%y%m%d_%H%M%S")
        logs_location = fileoperations.get_logs_location(logs_folder_name)
        #get logs for each instance
        for i_id, url in iteritems(log_list):
            zip_location = save_file_from_url(url, logs_location,
                                              i_id + '.zip')
            instance_folder = os.path.join(logs_location, i_id)
            fileoperations.unzip_folder(zip_location, instance_folder)
            fileoperations.delete_file(zip_location)

        fileoperations.set_user_only_permissions(logs_location)
        if do_zip:
            fileoperations.zip_up_folder(logs_location, logs_location + '.zip')
            fileoperations.delete_directory(logs_location)

            logs_location += '.zip'
            fileoperations.set_user_only_permissions(logs_location)
            io.echo(strings['logs.location'].replace('{location}',
                                                     logs_location))
        else:
            io.echo(strings['logs.location'].replace('{location}',
                                                     logs_location))
            # create symlink to logs/latest
            latest_location = fileoperations.get_logs_location('latest')
            try:
                os.unlink(latest_location)
            except OSError:
                # doesn't exist. Ignore
                pass
            try:
                os.symlink(logs_location, latest_location)
                io.echo('Updated symlink at', latest_location)
            except OSError:
                #Oh well.. we tried.
                ## Probably on windows, or logs/latest is not a symlink
                pass

    else:
        # print logs
        for i_id, url in iteritems(log_list):
            io.echo('================', i_id, '=================')
            print_from_url(url)


def setenv(app_name, env_name, var_list, region):
    namespace = 'aws:elasticbeanstalk:application:environment'

    options = []
    options_to_remove = []
    for pair in var_list:
        ## validate
        if not re.match('^[\w\\_.:/+@-][^=]*=([\w\\_.:/+@-][^=]*)?$', pair):
            io.log_error(strings['setenv.invalidformat'])
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
        io.log_error(strings['timeout.error'])


def print_from_url(url):
    result = urllib.request.urlopen(url).read()
    io.echo(result)


def save_file_from_url(url, location, filename):
    result = urllib.request.urlopen(url).read()

    return fileoperations.save_to_file(result, location, filename)


def terminate(env_name, region, nohang=False):
    request_id = elasticbeanstalk.terminate_environment(env_name, region)

    # disassociate with branch if branch default
    default_env = get_current_branch_environment()
    if default_env == env_name:
        set_environment_for_current_branch(None)

    if not nohang:
        wait_and_print_events(request_id, region,
                              timeout_in_seconds=60*5)


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


def setup_directory(app_name, region, solution):
    io.log_info('Setting up .elasticbeanstalk directory')
    fileoperations.create_config_file(app_name, region, solution)


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


def create_app_version(app_name, region, label=None, message=None):
    if heuristics.directory_is_empty():
        io.log_warning(strings['appversion.none'])
        return None

    source_control = SourceControl.get_source_control()
    # get version_label
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

    io.log_info('Creating app_version archive "' + version_label + '"')

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
                io.log_warning('Deploying a previously deployed commit')
                return version_label
            elif e.message == responses['app.notexists'].replace(
                    '{app-name}', '\'' + app_name + '\''):
                # App doesnt exist, must be a new region.
                ## Lets create the app in the region
                create_app(app_name, region)
            else:
                raise


def update_environment_configuration(app_name, env_name, region, nohang):
    # get environment setting
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

    update_environment(env_name, changes, region, nohang, remove=remove)


def update_environment(env_name, changes, region, nohang, remove=[]):
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


def switch_default_environment(app_name, env_name, region):
    #check that environment exists
    elasticbeanstalk.get_environment(app_name, env_name, region)
    set_environment_for_current_branch(env_name)


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


def ssh_into_instance(instance_id, region, keep_open=False):
    instance = ec2.describe_instance(instance_id, region)
    try:
        keypair_name = instance['KeyName']
    except KeyError:
        raise NoKeypairError()
    try:
        ip = instance['PublicIpAddress']
    except KeyError:
        raise NotFoundError(strings['ssh.noip'])
    security_groups = instance['SecurityGroups']


    user = 'ec2-user'

    # Open up port for ssh
    io.echo(strings['ssh.openingport'])
    for group in security_groups:
        ec2.authorize_ssh(group['GroupId'], region=region)
    io.echo(strings['ssh.portopen'])

    # do ssh
    try:
        ident_file = _get_ssh_file(keypair_name)
        returncode = subprocess.call(['ssh', '-i', ident_file,
                                      user + '@' + ip])
        if returncode != 0:
            LOG.debug('ssh returned exitcode: ' + str(returncode))
            raise CommandError('An error occurred while running ssh.')
    except OSError:
        CommandError(strings['ssh.notpresent'])
    finally:
        # Close port for ssh
        if keep_open:
            return
        else:
            for group in security_groups:
                ec2.revoke_ssh(group['GroupId'], region=region)
            io.echo(strings['ssh.closeport'])


def prompt_for_ec2_keyname(region, env_name=None):
    if env_name:
        io.validate_action(prompts['terminate.validate'], env_name)
    else:
        io.echo(prompts['ssh.setup'])
        ssh = get_boolean_response()
        if not ssh:
            return None

    keys = [k['KeyName'] for k in ec2.get_key_pairs(region=region)]

    if len(keys) < 1:
        keyname = _generate_and_upload_keypair(region, keys)

    else:
        new_key_option = '[ Create new KeyPair ]'
        keys.append(new_key_option)
        io.echo()
        io.echo(prompts['keypair.prompt'])
        keyname = utils.prompt_for_item_in_list(keys, default=len(keys))

        if keyname == new_key_option:
            keyname = _generate_and_upload_keypair(region, keys)

    return keyname


def select_tier():
    tier_list = Tier.get_latest_tiers()
    io.echo(prompts['tier.prompt'])
    tier = utils.prompt_for_item_in_list(tier_list)
    return tier


def get_solution_stack(solution_string, region):
    #If string is explicit, do not check
    if re.match('\d\dbit Amazon Linux [0-9.]+ v[0-9.]+ running .*', solution_string):
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


def _generate_and_upload_keypair(region, keys):
    # Get filename
    io.echo()
    io.echo(prompts['keypair.nameprompt'])
    unique = utils.get_unique_name('aws-eb', keys)
    keyname = io.prompt('Default is ' + unique, default=unique)
    file_name = fileoperations.get_ssh_folder() + keyname

    try:
        exitcode = subprocess.call(['ssh-keygen', '-f', file_name])
    except OSError:
        raise CommandError(strings['ssh.notpresent'])

    if exitcode == 0 or exitcode == 1:
        # if exitcode is 1, they file most likely exists, and they are
        ## just uploading it
        upload_keypair_if_needed(region, keyname)
        return keyname
    else:
        LOG.debug('ssh-keygen returned exitcode: ' + str(exitcode) +
                   ' with filename: ' + file_name)
        raise CommandError('An error occurred while running ssh-keygen.')


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


def _get_ssh_file(keypair_name):
    key_file = fileoperations.get_ssh_folder() + keypair_name
    if not os.path.exists(key_file):
        if os.path.exists(key_file + '.pem'):
            key_file += '.pem'
        else:
            raise NotFoundError(strings['ssh.filenotfound'].replace(
                '{key-name}', keypair_name))

    return key_file