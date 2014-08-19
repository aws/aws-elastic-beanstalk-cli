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
import urllib2

from six import iteritems
from cement.utils.shell import exec_cmd2
from cement.utils.misc import minimal_logger
from botocore.exceptions import NoCredentialsError

from ebcli.lib import elasticbeanstalk, s3, iam
from ebcli.core import fileoperations, io
from ebcli.objects.sourcecontrol import SourceControl
from ebcli.resources.strings import strings, responses
from ebcli.objects import region as regions
from ebcli.lib import utils
from ebcli.objects import environment
from ebcli.objects.exceptions import NoSourceControlError, \
    ServiceError, TimeoutError
from ebcli.objects.solutionstack import SolutionStack
from ebcli.objects.tier import Tier
from ebcli.lib.aws import InvalidParameterValueError

LOG = minimal_logger(__name__)
DEFAULT_ROLE_NAME = 'aws-elasticbeanstalk-ec2-role'


def wait_and_log_events(request_id, region,
                          timeout_in_seconds=60*10, sleep_time=5):
    start = datetime.now()
    timediff = timedelta(seconds=timeout_in_seconds)

    finished = False
    last_time = ''
    while not finished and (datetime.now() - start) < timediff:
        time.sleep(sleep_time)
        results = elasticbeanstalk.get_new_events(None, None,
                                                  request_id,
                                                  last_event_time=last_time,
                                                  region=region)

        for event in reversed(results['Events']):
            #Log event
            message, last_time = log_event(event)

            # Test event message for success string
            if message == responses['event.greenmessage'] or \
                    message.startswith(responses['event.launchsuccess']):
                finished = True
            if message.startswith(responses['event.launchsuccess']):
                finished = True
            if message == responses['event.redmessage']:
                raise ServiceError(message)
            if message == responses['logs.pulled']:
                finished = True
            if message == responses['env.terminated']:
                finished = True

    if not finished:
        raise TimeoutError('Timed out while waiting for environment to launch')


def log_event(event, echo=False):
    message = event['Message']
    severity = event['Severity']
    date = event['EventDate']
    if echo:
        io.echo(date.ljust(26) + severity.ljust(8) + message)
    elif severity == 'INFO':
        io.log_info(message)
    elif severity == 'WARN':
        io.log_warning(message)
    elif severity == 'ERROR':
        io.log_error(message)

    return message, date


def print_events(app_name, env_name, region):
    results = elasticbeanstalk.get_new_events(
        app_name, env_name, None, last_event_time='', region=region
    )

    for event in results['Events']:
        log_event(event, echo=True)


def setup(app_name, region):
    setup_directory(app_name, region)
    try:
        create_app(app_name, region)
    except NoCredentialsError:
        setup_aws_dir()  # only need this if there are no creds in env vars
        create_app(app_name, region)  # now that creds are set up, create app

    try:
        setup_ignore_file()
    except NoSourceControlError:
        io.log_warning(strings['git.notfound'])


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
        elasticbeanstalk.create_application(
            app_name,
            strings['app.description'],
            region=region
        )

        # ToDo: save app details
        io.echo('Application', app_name,
                'has been created')
    else:
        # App exists, pull down environments
        io.log_warning('App Exists: Syncing existing Environments')
        sync_app(app_name, region)
        pass


def pull_down_env(app_name, env_name, region):
    api_model = elasticbeanstalk.describe_configuration_settings(
        app_name, env_name, region=region
    )
    usr_model = environment.convert_api_to_usr_model(api_model)
    fileoperations.save_env_file(usr_model)


def sync_app(app_name, region):
    envs = elasticbeanstalk.get_all_environments(app_name, region)
    for env in envs or []:
        pull_down_env(app_name, env, region)

    # ToDo: Remove all deleted, non-paused env's


def get_default_profile():
    """  Get the default elasticbeanstalk IAM profile,
            Create it if it doesn't exist """

    # get list of profiles
    profile_names = iam.get_instance_profile_names()
    profile = DEFAULT_ROLE_NAME
    if profile not in profile_names:
        iam.create_instance_profile(profile)

    return profile


def make_new_env(app_name, env_name, region, cname, solution_stack,
                 tier, label, profile, branch_default):
    if profile is None:
        # Service supports no profile, however it is not good/recommended
        # Get the eb default profile
        profile = get_default_profile()

    # Create env
    result = create_env(app_name, env_name, region, cname, solution_stack,
                        tier, label, profile)

    env_name = result['EnvironmentName']  # get the (possibly) updated name

    # Edit configurations
    ## Get default environment
    default_env = get_setting_from_current_branch('environment')
    ## Save env as branch default if needed
    if not default_env or branch_default:
        write_setting_to_current_branch('environment', env_name)

    # Print status of app
    io.echo('-- The environment is being created. --')
    print_env_details(result, health=False)

    io.log_info('Printing Status:')
    try:
        request_id = result['ResponseMetadata']['RequestId']
        wait_and_log_events(request_id, region)
        pull_down_env(app_name, env_name, region)
        io.echo('-- The environment has been created successfully! --')
    except TimeoutError:
        io.log_error('Unknown state of environment. Operation timed out.')


def print_env_details(env, health=True):

    app_name = env['ApplicationName']
    env_name = env['EnvironmentName']
    env_id = env['EnvironmentId']
    solution_stack = env['SolutionStackName']
    try:
        cname = env['CNAME']
    except KeyError:
        cname = 'UNKNOWN'
    tier = env['Tier']
    env_status = env['Status']
    health = env['Health']

    # Convert solution_stack and tier to objects
    solution_stack = SolutionStack(solution_stack)
    tier = Tier(tier['Name'], tier['Type'], tier['Version'])

    io.echo('Environment details for:', env_name)
    io.echo('  App name:', app_name)
    io.echo('  Environment ID:', env_id)
    io.echo('  Solution Stack:', solution_stack)
    io.echo('  Tier:', tier)
    io.echo('  Cname:', cname)

    if health:
        io.echo('Status:', env_status)
        io.echo('Health:', health)


def create_env(app_name, env_name, region, cname, solution_stack,
               tier, label, profile):
    description = strings['env.description']

    try:
        return elasticbeanstalk.create_environment(
            app_name, env_name, cname, description, solution_stack,
            tier, label, profile, region=region)

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


def deploy(app_name, env_name, region):
    if region:
        region_name = region
    else:
        region_name = 'DEFAULT'

    io.log_info('Deploying code to ' + env_name + " in region " + region_name)

    # Create app version
    app_version_label = create_app_version(app_name, region)

    # swap env to new app version
    elasticbeanstalk.update_env_application_version(env_name,
                                                    app_version_label, region)

    wait_and_log_events(app_name, env_name, region)


def status(app_name, env_name, region):
    env = elasticbeanstalk.get_environment(app_name, env_name, region)
    print_env_details(env, True)


def logs(env_name, region):
    # Request info
    result = elasticbeanstalk.request_environment_info(env_name, region)

    # Wait for logs to finish tailing
    request_id = result['ResponseMetadata']['RequestId']
    wait_and_log_events(request_id, region,
                        timeout_in_seconds=60, sleep_time=1)

    return print_logs(env_name, region, '')


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
        print_url(url)


def print_url(url):
    result = urllib2.urlopen(url).read()
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
    wait_and_log_events(request_id, region,
                        timeout_in_seconds=60*5)



def setup_directory(app_name, region):
    fileoperations.create_config_file(app_name, region)


def setup_ignore_file():
    git_installed = fileoperations.get_config_setting('global', 'git')

    if not git_installed:
        source_control = SourceControl.get_source_control()
        source_control.set_up_ignore_file()
        fileoperations.write_config_setting('global', 'git', True)


def zip_up_code():
    pass


def create_app_version(app_name, region):
    # NOTE: Requires instance to be running

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
                e.message.endswith(' already exists'):
            # we must be deploying with an existing app version
            io.log_warning('Your are deploying a previously deployed commit')
    return version_label


def update_environment():
    pass


def remove_zip_file():
    pass


def get_boolean_response():
    response = io.prompt('y/n').lower()
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