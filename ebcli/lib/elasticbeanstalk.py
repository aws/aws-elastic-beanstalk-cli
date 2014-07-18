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

import dateutil
import datetime

from cement.utils.misc import minimal_logger

from ebcli.core import globals as eb
from ebcli.objects.solutionstack import SolutionStack
from ebcli.objects.exceptions import NotFoundException
from ebcli.lib import utils
from ebcli.lib import aws

LOG = minimal_logger(__name__)


def _make_api_call(operation_name, **operation_options):

    return aws.make_api_call('elasticbeanstalk',
                               operation_name,
                               **operation_options)


def describe_application(app_name):
    LOG.debug('Inside describe_application api wrapper')
    result = _make_api_call('describe-applications',
                            application_names=[app_name])
    return result['Applications']


def describe_applications():
    LOG.debug('Inside describe_applications api wrapper')
    result = _make_api_call('describe-applications')
    return result['Applications']


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

def get_storage_location():
    response = _make_api_call('create-storage-location')
    return response['S3Bucket']


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
    platform = utils.prompt_for_item_in_list(platforms, eb.app)

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
        version = utils.prompt_for_item_in_list(versions, eb.app)
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
        server = utils.prompt_for_item_in_list(servers, eb.app)
    else:
        server = servers[0]

    #filter
    solution_stacks = [x for x in solution_stacks if x.server == server]

    #should have 1 and only have 1 result
    if len(solution_stacks) != 1:
        eb.app.log.error('Filtered Solution Stack list contains '
                         'multiple results')
    return solution_stacks[0].string











