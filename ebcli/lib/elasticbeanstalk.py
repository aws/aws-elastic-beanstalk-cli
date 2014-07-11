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

import sys
import dateutil
import datetime
import re

import botocore.session
import botocore.exceptions

from ebcli import __version__
from ebcli.core import globals as eb
from ebcli.resources.strings import strings
from ebcli.objects.solutionstack import SolutionStack
from ebcli.objects.notfoundexception import NotFoundException


def get_beanstalk_session():
    eb.app.log.info('Creating new Botocore session')
    session = botocore.session.get_session()
    _set_user_agent_for_session(session)
    eb.app.log.debug('Successfully created session')

    beanstalk = session.get_service('elasticbeanstalk')
    return beanstalk


def _set_user_agent_for_session(session):
    session.user_agent_name = 'eb-cli'
    session.user_agent_version = __version__


def _make_api_call(operation_name, **operation_options):
    global app
    beanstalk = get_beanstalk_session()
    operation = beanstalk.get_operation(operation_name)
    endpoint = beanstalk.get_endpoint('us-west-2')

    try:
        eb.app.log.debug('Making api call')
        http_response, response_data = operation.call(endpoint,
                                                      **operation_options)
        status = http_response.status_code
        eb.app.log.debug('API call finished, response =', status)

        if status is not 200:
            if status is 403:
                eb.app.log.error('Operation Denied. Are your '
                                 'credentials correct?')
            else:
                eb.app.log.error('API Call unsuccessful. '
                                 'Status code returned' + status)
            if response_data:
                eb.app.log.debug('Response:', response_data)
            return None
    except botocore.exceptions.NoCredentialsError:
        eb.app.log.error('No credentials file found')
        eb.app.print_to_console(strings['error.nocreds'])
        sys.exit(0)

    except (Exception, IOError) as error:
        eb.app.log.error('Error while contacting Elastic Beanstalk Service')
        eb.app.log.debug(error)
        return None

    return response_data


def describe_applications():
    eb.app.log.info('Inside describe_applications api wrapper')
    return _make_api_call('describe-applications')


def create_application(app_name, descrip):
    eb.app.log.info('Inside create_application api wrapper')
    return _make_api_call('create-application',
                          application_name=app_name,
                          description=descrip)


def create_application_version(app_name, vers_label, descrip):
    eb.app.log.info('Inside create_application_version api wrapper')
    return _make_api_call('create-application-version',
                          application_name=app_name,
                          version_label=vers_label,
                          description=descrip)


def create_environment(app_name, env_name, descrip, solution_stck, tier0):
    eb.app.log.info('Inside create_environment api wrapper')
    return _make_api_call('create-environment',
                          application_name=app_name,
                          environment_name=env_name,
                          description=descrip,
                          solution_stack=solution_stck,
                          tier=tier0)


def get_available_solution_stacks():
    result = _make_api_call('list-available-solution-stacks')
    stack_strings = result['SolutionStacks']

    eb.app.log.debug('Solution Stack result size = ' + str(len(stack_strings)))

    solution_stacks = []
    for s in stack_strings:
        stack = SolutionStack(s)
        solution_stacks.append(stack)

    return solution_stacks


def get_environment_details(app_name):
    return _make_api_call('describe-environments',
                          application_name=app_name)


def get_new_events(app_name, last_event_time=''):
    if last_event_time is not '':
        time = dateutil.parser.parse(last_event_time)
        new_time = time + datetime.timedelta(0, 0, 1000)
        timestamp = new_time.isoformat()[0:-9] + 'Z'
    else:
        timestamp = ''
    return _make_api_call('describe-events',
                          application_name=app_name,
                          start_time=timestamp)


def get_solution_stack(string):
    solution_stacks = get_available_solution_stacks()
    # filter
    solution_stacks = [x for x in solution_stacks if x.string == string]

    #check for a valid result
    if len(solution_stacks) == 0:
        raise NotFoundException('Solution stack not found')

    #should only have 1 result
    if len(solution_stacks) > 1:
        eb.app.log.error('Solution Stack list contains '
                         'multiple results')
    return solution_stacks[0]


def select_solution_stack():
    solution_stacks = get_available_solution_stacks()

    # get platforms
    platforms = []
    for stack in solution_stacks:
        if stack.platform not in platforms:
            platforms.append(stack.platform)

    eb.app.print_to_console('Please choose a platform type')
    platform = _prompt_for_item_in_list(platforms)

    # filter
    solution_stacks = [x for x in solution_stacks if x.platform == platform]

    #get Versions
    versions = []
    for stack in solution_stacks:
        if stack.version not in versions:
            versions.append(stack.version)

    #now choose a version (if applicable)
    if len(versions) > 1:
        eb.app.print_to_console('Please choose a version')
        version = _prompt_for_item_in_list(versions)
    else:
        version = versions[0]

    #filter
    solution_stacks = [x for x in solution_stacks if x.version == version]

    #Lastly choose a server type
    servers = []
    for stack in solution_stacks:
        if stack.server not in servers:
            servers.append(stack.server)

    #now choose a server (if applicable)
    if len(servers) > 1:
        eb.app.print_to_console('Please choose a server type')
        server = _prompt_for_item_in_list(servers)
    else:
        server = servers[0]

    #filter
    solution_stacks = [x for x in solution_stacks if x.server == server]

    #should have 1 and only have 1 result
    if len(solution_stacks) != 1:
        eb.app.log.error('Filtered Solution Stack list contains '
                         'multiple results')
    return solution_stacks[0].string


def _prompt_for_item_in_list(list):
    for x in range(0, len(list)):
        eb.app.print_to_console(str(x + 1) + ') ' + list[x])


    choice = int(eb.app.prompt('number'))
    while not (0 < choice <= len(list)):
        eb.app.print_to_console('Sorry, that is not a valid choice, '
                                'please choose again')
        choice = int(eb.app.prompt('number'))
    return list[choice - 1]


def select_region():
    pass












