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

from six.moves import urllib
from six import iteritems
from cement.utils.misc import minimal_logger
from cement.utils.shell import exec_cmd
from botocore.exceptions import NoCredentialsError

from ebcli.lib import elasticbeanstalk, s3, iam
from ebcli.core import fileoperations, io
from ebcli.objects.sourcecontrol import SourceControl
from ebcli.resources.strings import strings, responses
from ebcli.objects import region as regions
from ebcli.lib import utils
from ebcli.objects import configuration
from ebcli.objects.exceptions import NoSourceControlError, \
    ServiceError, TimeoutError
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
    while not finished and (datetime.now() - start) < timediff:
        time.sleep(sleep_time)
        events = elasticbeanstalk.get_new_events(
            None, None, request_id, last_event_time=last_time, region=region
        )

        for event in reversed(events):
            log_event(event)

            # Test event message for success string
            finished = _is_success_string(event.message)
            last_time = event.event_date

    if not finished:
        raise TimeoutError('Timed out while waiting for command to complete')


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
        io.echo('Hanging and waiting for events. Use CTRL + C to exit.')
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
        io.echo('It appears you are using ' + platform + '. Is this correct?')
        correct = get_boolean_response()

    if not platform or not correct:
        # ask for platform
        io.echo('Please choose a platform type')
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
        io.echo('Please choose a version')
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

    #Default to latest version of server
            # if len(servers) > 1:
            #     io.echo('Please choose a server type')
            #     server = utils.prompt_for_item_in_list(servers)
            # else:
    server = servers[0]

    #filter
    solution_stacks = [x for x in solution_stacks if x.server == server]

    #should have 1 and only have 1 result
    if len(solution_stacks) != 1:
        LOG.error('Filtered Solution Stack list contains '
                  'multiple results')
    return solution_stacks[0]


def setup(app_name, region, solution):
    # try to get solution stacks to test for credentials
    try:
        elasticbeanstalk.get_available_solution_stacks(region)
    except NoCredentialsError:
        setup_aws_dir()  # fix credentials

    # Now that credentials are working, lets continue
    if solution:
        solution = elasticbeanstalk.get_solution_stack(solution, region)
    else:
        solution = prompt_for_solution_stack(region)

    setup_directory(app_name, region, solution.string)

    create_app(app_name, region)

    try:
        setup_ignore_file()
    except NoSourceControlError:
        io.log_warning(strings['sc.notfound'])


def setup_aws_dir():
    io.log_info('Setting up ~/aws/ directory with config file')
    # ToDo: ignore prompting for creds if they exist in path.
    # Maybe wait for an exception before bothering

    access_key, secret_key = \
        fileoperations.read_aws_config_credentials()

    change = False
    if not access_key or not secret_key:
        io.echo(strings['cred.prompt'])

        access_key = io.prompt('aws-access-id')
        secret_key = io.prompt('aws-secret-key')

        fileoperations.save_to_aws_config(access_key, secret_key)


def create_app(app_name, region):
    # check if app exists
    app_result = elasticbeanstalk.describe_application(app_name, region)

    if not app_result:  # no app found with that name
        # Create it
        io.log_info('Creating application: ' + app_name)
        elasticbeanstalk.create_application(
            app_name,
            strings['app.description'],
            region=region
        )

        io.echo('Application', app_name,
                'has been created')
    else:
        # App exists, pull down environments
        io.log_warning('App Exists: Syncing existing Environments')
        sync_app(app_name, region)
        pass


def pull_down_env(app_name, env_name, region):
    # we need the last time the env was updated
    env_details = elasticbeanstalk.get_environment(app_name,
                                                   env_name, region)
    api_model = elasticbeanstalk.describe_configuration_settings(
        app_name, env_name, region=region
    )

    # move date updated over to api_model for merging
    date = env_details.date_updated
    api_model['DateUpdated'] = date

    usr_model = configuration.convert_api_to_usr_model(api_model)
    fileoperations.save_env_file(usr_model)


def sync_app(app_name, region):
    envs_remote = elasticbeanstalk.get_all_environments(app_name, region)
    env_names_remote = []
    for env in envs_remote or []:
        env_name = env['EnvironmentName']
        env_names_remote.append(env_name)
        pull_down_env(app_name, env_name, region)

    envs_local = fileoperations.get_environments_from_files()
    for env in envs_local:
        env_name = env['EnvironmentName']
        if env_name not in env_names_remote:
            fileoperations.delete_env_file(env_name)


def get_default_profile():
    """  Get the default elasticbeanstalk IAM profile,
            Create it if it doesn't exist """

    # get list of profiles
    profile_names = iam.get_instance_profile_names()
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
        # python probably isnt on path
        ## try to run webbrowser internally
        import webbrowser
        webbrowser.open(url)


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
            io.echo('The environment is currently a Single Instance, would you'
                    ' like to switch to a Load Balanced environment?')
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
    result = elasticbeanstalk.update_environment(env_name, options, region)
    try:
        request_id = result['ResponseMetadata']['RequestId']
        wait_and_print_events(request_id, region, timeout_in_seconds=60*5)
        pull_down_env(app_name, env_name, region)
        io.echo('-- The environment has been created successfully! --')
    except TimeoutError:
        io.log_error('Unknown state of environment. Operation timed out.')


def make_new_env(app_name, env_name, region, cname, solution_stack, tier,
                 label, profile, key_name, branch_default, sample, nohang):
    if profile is None:
        # Service supports no profile, however it is not good/recommended
        # Get the eb default profile
        profile = get_default_profile()

    # deploy code
    if not sample and not label:
        io.log_info('Creating new application version using project code')
        label = create_app_version(app_name, region)

    # Create env
    io.log_info('Creating new environment')
    result, request_id = create_env(app_name, env_name, region, cname,
                                    solution_stack, tier, label, key_name,
                                    profile)

    env_name = result.name  # get the (possibly) updated name

    # Edit configurations
    ## Get default environment
    default_env = get_setting_from_current_branch('environment')
    ## Save env as branch default if needed
    if not default_env or branch_default:
        write_setting_to_current_branch('environment', env_name)

    # Print status of app
    io.echo('-- The environment is being created. --')
    print_env_details(result, health=False)

    if nohang:
        return

    io.log_info('Printing Status:')
    try:
        wait_and_print_events(request_id, region)
        pull_down_env(app_name, env_name, region)
        io.echo('-- The environment has been created successfully! --')
    except TimeoutError:
        io.log_error('Unknown state of environment. Operation timed out.')


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
               tier, label, key_name, profile):
    description = strings['env.description']

    try:
        return elasticbeanstalk.create_environment(
            app_name, env_name, cname, description, solution_stack,
            tier, label, key_name, profile, region=region)

    except InvalidParameterValueError as e:
        LOG.debug('creating app returned error: ' + e.message)
        if re.match(responses['env.cnamenotavailable'], e.message):
            io.echo('The CNAME you provided is currently not available.')
            io.echo('Please try again')
            cname = io.prompt_for_cname()
        elif re.match(responses['env.nameexists'], e.message):
            io.echo(strings['env.exists'])
            env_name = io.prompt_for_environment_name()
        else:
            raise e

        # Try again with new values
        return create_env(app_name, env_name, region, cname,
                          solution_stack, tier, label, profile)


def delete(app_name, region, confirm):
    try:
        request_id = elasticbeanstalk.delete_application(app_name, region)

    #ToDo catch more explicit
    ## Currently also catches "invalid app name"
    except InvalidParameterValueError:
        # Env's exist, let make sure the user is ok
        io.echo('This application has currently running environments, '
                'if you delete it, all environments will be terminated. '
                'Are you sure you want to delete the application?')
        if not confirm:
            confirm = get_boolean_response()

        if not confirm:
            return

        request_id = elasticbeanstalk.delete_application_and_envs(app_name,
                                                                  region)

    cleanup_ignore_file()
    fileoperations.clean_up()
    wait_and_print_events(request_id, region, timeout_in_seconds=60*5)


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
        # Print environment Variables
        settings = elasticbeanstalk.describe_configuration_settings(
            app_name, env_name, region
        )['OptionSettings']
        namespace = 'aws:elasticbeanstalk:application:environment'
        vars = {n['OptionName']: n['Value'] for n in settings
                if n["Namespace"] == namespace}
        io.echo('  Environment Variables:')
        for key, value in vars.iteritems():
            io.echo('       ', key, '=', value)

        # Print environment instances
        env = elasticbeanstalk.get_environment_resources(env_name, region)
        instances = env['EnvironmentResources']['Instances']
        io.echo('  Running instances:', len(instances))
        for i in instances:
            io.echo('       ', i['Id'])




def logs(env_name, region):
    # Request info
    result = elasticbeanstalk.request_environment_info(env_name, region)

    # Wait for logs to finish tailing
    request_id = result['ResponseMetadata']['RequestId']
    wait_and_print_events(request_id, region,
                        timeout_in_seconds=60, sleep_time=1)

    return print_logs(env_name, region)


def print_logs(env_name, region):
    # Get logs
    result = elasticbeanstalk.retrieve_environment_info(env_name, region)

    """
    Results are ordered with latest last, we just want the latest
    """
    log_list = {}
    for log in result['EnvironmentInfo']:
        instance_id = log['Ec2InstanceId']
        url = log['Message']
        log_list[instance_id] = url

    for instance_id, url in iteritems(log_list):
        io.echo('================ ' + instance_id + '=================')
        print_from_url(url)


def setenv(app_name, env_name, var_list, region):
    namespace = 'aws:elasticbeanstalk:application:environment'

    options = []
    for pair in var_list:
        ## validate
        if not re.match('^[\w\\_.:/+-@][^=]*=[\w\\_.:/+-@][^=]*$', pair):
            io.log_error('Must use format VAR_NAME=KEY. Variable and keys '
                         'cannot contain any spaces or =. They must start'
                         ' with a letter, number or one of \\_.:/+-@')
            return
        else:
            option_name, value = pair.split('=')
            options.append({'Namespace': namespace,
                            'OptionName': option_name,
                            'Value': value})

    result = elasticbeanstalk.update_environment(env_name, options, region)
    try:
        request_id = result['ResponseMetadata']['RequestId']
        wait_and_print_events(request_id, region, timeout_in_seconds=60*4)
        pull_down_env(app_name, env_name, region)
        io.echo('-- The environment has been created successfully! --')
    except TimeoutError:
        io.log_error('Unknown state of environment. Operation timed out.')


def print_from_url(url):
    result = urllib.request.urlopen(url).read()
    io.echo(result)


def terminate(env_name, region):
    result = elasticbeanstalk.terminate_environment(env_name, region)

    # disassociate with branch if branch default
    ## Get default environment
    default_env = get_setting_from_current_branch('environment')
    if default_env == env_name:
        write_setting_to_current_branch('environment', None)

    # remove config file
    fileoperations.delete_env_file(env_name)

    # Wait for logs to finish tailing
    request_id = result['ResponseMetadata']['RequestId']
    wait_and_print_events(request_id, region,
                        timeout_in_seconds=60*5)


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


def create_app_version(app_name, region):
    #get version_label
    source_control = SourceControl.get_source_control()
    version_label = source_control.get_version_label()

    #get description
    description = source_control.get_message()

    # Create zip file
    file_name = version_label + '.zip'
    file_path = fileoperations.get_zip_location(file_name)
    source_control.do_zip(file_path)

    # Get s3 location
    bucket = elasticbeanstalk.get_storage_location(region)
    # upload to s3
    key = app_name + '/' + file_name
    s3.upload_application_version(bucket, key, file_path,
                                                region=region)

    try:
        elasticbeanstalk.create_application_version(
            app_name, version_label, description, bucket, key, region
        )
    except InvalidParameterValueError as e:
        if e.message.startswith('Application Version ') and \
                e.message.endswith(' already exists.'):
            # we must be deploying with an existing app version
            io.log_warning('Deploying a previously deployed commit')
    return version_label


def update_environment(app_name, env_name, region):
    usr_model = fileoperations.get_environment_from_file(env_name)

    # pull down env details from cloud
    # check date of saved env and compare
    env_details = elasticbeanstalk.get_environment(app_name, env_name, region)

    if env_details['DateUpdated'] != usr_model['DateUpdated']:
        io.echo('Your environments settings are out of date. \n'
                'Please do an \'eb sync\' before updating environment')
        return

    api_model = elasticbeanstalk.describe_configuration_settings(
        app_name, env_name, region
    )
    changes = configuration.collect_changes(api_model, usr_model)
    result = elasticbeanstalk.update_environment(env_name, changes, region)

    io.log_info('Printing Status:')
    try:
        request_id = result['ResponseMetadata']['RequestId']
        wait_and_print_events(request_id, region)
        pull_down_env(app_name, env_name, region)
        io.echo('-- The environment has been created successfully! --')
    except TimeoutError:
        io.log_error('Unknown state of environment. Operation timed out.')


def remove_zip_file():
    pass


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