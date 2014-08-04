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

from ebcli.core import io
from ebcli.objects.solutionstack import SolutionStack
from ebcli.objects.exceptions import NotFoundException
from ebcli.objects.tier import Tier
from ebcli.lib import utils
from ebcli.lib import aws

LOG = minimal_logger(__name__)


DEFAULT_ROLE_NAME = 'aws-elasticbeanstalk-ec2-role'


def _make_api_call(operation_name, region=None, **operation_options):

    return aws.make_api_call('elasticbeanstalk',
                               operation_name,
                               region=region,
                               **operation_options)


def create_application(app_name, descrip, region=None):
    LOG.debug('Inside create_application api wrapper')
    return _make_api_call('create-application',
                          application_name=app_name,
                          description=descrip,
                          region=region)


def create_application_version(app_name, vers_label, descrip, s3_bucket,
                               s3_key, region=None):
    LOG.debug('Inside create_application_version api wrapper')
    return _make_api_call('create-application-version',
                          application_name=app_name,
                          version_label=vers_label,
                          description=descrip,
                          source_bundle={'S3Bucket': s3_bucket,
                                         'S3Key': s3_key},
                          region=region)


def create_environment(app_name, env_name, cname, description, solution_stck,
                       tier, label, profile, region=None):
    LOG.debug('Inside create_environment api wrapper')

    assert app_name is not None, 'App name can not be empty'
    assert env_name is not None, 'Environment name can not be empty'
    assert description is not None, 'Description can not be empty'
    assert solution_stck is not None, 'Solution stack can not be empty'

    settings = [
        # ToDo: Remove code below: reserved for testing reasons
        # {'Namespace': 'aws:autoscaling:launchconfiguration',
        # 'OptionName': 'EC2KeyName',
        # 'Value': 'amazonPersonal'},
    ]

    # ToDo : we should default to t2.micro, but maybe at a service level

    kwargs = {
        'application_name': app_name,
        'environment_name': env_name,
        'description': description,
        'cname_prefix': cname,
        'solution_stack_name': solution_stck.name,
        'option_settings': settings,
    }
    if tier:
        kwargs['tier'] = tier.to_struct()
    if label:
        kwargs['label'] = label
    if profile:
        settings.append(
            {'Namespace': 'aws:autoscaling:launchconfiguration',
             'OptionName': 'IamInstanceProfile',
             'Value': profile}
        )

    return _make_api_call('create-environment', region=region, **kwargs)


def delete_application(app_name, region=None):
    LOG.debug('Inside delete_application api wrapper')
    result = _make_api_call('delete-application',
                            region=region)


def describe_application(app_name, region=None):
    LOG.debug('Inside describe_application api wrapper')
    result = _make_api_call('describe-applications',
                            application_names=[app_name],
                            region=region)
    return result['Applications']


def describe_applications(region=None):
    LOG.debug('Inside describe_applications api wrapper')
    result = _make_api_call('describe-applications', region=region)
    return result['Applications']


def describe_configuration_settings(app_name, env_name, region=None):
    LOG.debug('Inside describe_configuration_settings api wrapper')
    result = _make_api_call('describe-configuration-settings',
                            application_name=app_name,
                            environment_name=env_name,
                            region=region)
    return result['ConfigurationSettings'][0]


def get_available_solution_stacks(region=None):
    result = _make_api_call('list-available-solution-stacks', region=region)
    stack_strings = result['SolutionStacks']

    LOG.debug('Solution Stack result size = ' + str(len(stack_strings)))

    solution_stacks = []
    for s in stack_strings:
        stack = SolutionStack(s)
        solution_stacks.append(stack)

    return solution_stacks


def get_all_environments(app_name, region=None):
    LOG.debug('Inside get_all_environments api wrapper')
    return _make_api_call('describe-environments',
                          application_name=app_name,
                          region=region)


def get_environment(app_name, env_name, region=None):
    LOG.debug('Inside get_environment api wrapper')
    result = _make_api_call('describe-environments',
                          application_name=app_name,
                          environment_names=[env_name],
                          region=region)
    return result['Environments'][0]


def get_new_events(app_name, env_name, last_event_time='', region=None):
    LOG.debug('Inside get_new_events api wrapper')
    if last_event_time is not '':
        time = dateutil.parser.parse(last_event_time)
        new_time = time + datetime.timedelta(0, 0, 1000)
        timestamp = new_time.isoformat()[0:-9] + 'Z'
    else:
        timestamp = ''
    return _make_api_call('describe-events',
                          application_name=app_name,
                          environment_name=env_name,
                          start_time=timestamp,
                          region=region)


def get_storage_location(region=None):
    LOG.debug('Inside get_storage_location api wrapper')
    response = _make_api_call('create-storage-location', region=region)
    return response['S3Bucket']


def update_environment(app_name, env_name, region=None):
    LOG.debug('Inside update_environment api wrapper')
    pass


def update_env_application_version(env_name,
                                   version_label, region=None):
    LOG.debug('Inside update_env_application_version api wrapper')
    response = _make_api_call('update-environment',
                              environment_name=env_name,
                              version_label=version_label,
                              region=region)
    return response


def get_solution_stack(string):
    solution_stacks = get_available_solution_stacks()
    # filter
    solution_stacks = [x for x in solution_stacks if x.string == string]

    #check for a valid result
    if len(solution_stacks) == 0:
        raise NotFoundException('Solution stack not found')

    #should only have 1 result
    if len(solution_stacks) > 1:
        LOG.error('Solution Stack list contains '
                         'multiple results')
    return solution_stacks[0]


def select_solution_stack():
    solution_stacks = get_available_solution_stacks()

    # get platforms
    platforms = []
    for stack in solution_stacks:
        if stack.platform not in platforms:
            platforms.append(stack.platform)

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

    #now choose a server (if applicable)
    if len(servers) > 1:
        io.echo('Please choose a server type')
        server = utils.prompt_for_item_in_list(servers)
    else:
        server = servers[0]

    #filter
    solution_stacks = [x for x in solution_stacks if x.server == server]

    #should have 1 and only have 1 result
    if len(solution_stacks) != 1:
        LOG.error('Filtered Solution Stack list contains '
                         'multiple results')
    return solution_stacks[0]


def select_tier():
    tier_list = Tier.get_all_tiers()
    io.echo('Please choose a tier')
    tier = utils.prompt_for_item_in_list(tier_list)
    return tier









