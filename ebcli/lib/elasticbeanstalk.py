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

import datetime
import time

from cement.utils.misc import minimal_logger
from ebcli.objects.platform import PlatformVersion
from ebcli.resources.statics import namespaces, option_names

from ebcli.objects.solutionstack import SolutionStack
from ebcli.objects.exceptions import NotFoundError, InvalidStateError, \
    AlreadyExistsError
from ebcli.objects.tier import Tier
from ebcli.lib import aws
from ebcli.lib.aws import InvalidParameterValueError
from ebcli.objects.event import Event
from ebcli.objects.environment import Environment
from ebcli.objects.application import Application
from ebcli.resources.strings import strings, responses

LOG = minimal_logger(__name__)

DEFAULT_ROLE_NAME = 'aws-elasticbeanstalk-ec2-role'


def _make_api_call(operation_name, **operation_options):
    return aws.make_api_call('elasticbeanstalk',
                             operation_name,
                             **operation_options)


def delete_platform(arn):
    LOG.debug('Inside delete_platform api wrapper')
    return _make_api_call('delete_platform_version',
                          PlatformArn=arn,
                          DeleteResources=True)

def _make_equal_filter(filter_type, filter_value):
    return { 'Type': filter_type, 'Operator': '=', 'Values': [filter_value] }    

def list_platform_versions(platform_name=None, platform_version=None, status=None, owner=None):
    kwargs = dict()
    result_filters = []

    if platform_name is not None:
        result_filters.append(_make_equal_filter('PlatformName', platform_name))

    if platform_version is not None:
        result_filters.append(_make_equal_filter('PlatformVersion', platform_version))

    if status:
        result_filters.append(_make_equal_filter('PlatformStatus', status))

    if owner:
        result_filters.append(_make_equal_filter('PlatformOwner', owner))

    kwargs['Filters'] = result_filters

    LOG.debug('Inside list_platform_versions api wrapper')
    platforms, nextToken = _list_platform_versions(kwargs)

    while nextToken is not None:
        time.sleep(0.1)  # To avoid throttling we sleep for 100ms before requesting the next page
        next_platforms, nextToken = _list_platform_versions(kwargs, nextToken)
        platforms = platforms + next_platforms

    return platforms


def describe_platform_version(arn):
    LOG.debug('Inside describe_platform_version api wrapper')
    return _make_api_call('describe_platform_version',
                          PlatformArn=arn)


def _list_platform_versions(kwargs, nextToken=None):
    if nextToken is not None:
        # Sleep for 100ms before pulling the next page
        time.sleep(0.1)
        kwargs['NextToken'] = nextToken

    response = _make_api_call(
        'list_platform_versions',
        **kwargs
    )

    platforms = response['PlatformSummaryList']
    try:
        nextToken = response['NextToken']
    except KeyError:
        nextToken = None

    return platforms, nextToken


def create_application(app_name, descrip):
    LOG.debug('Inside create_application api wrapper')
    try:
        result = _make_api_call('create_application',
                                ApplicationName=app_name,
                                Description=descrip)
    except InvalidParameterValueError as e:
        string = responses['app.exists'].replace('{app-name}', app_name)
        if e.message == string:
            raise AlreadyExistsError(e)
        else:
            raise e

    return result


def create_platform_version(platform_name, version, s3_bucket, s3_key, instance_profile, key_name, instance_type, vpc = None):
    kwargs = dict()

    if s3_bucket and s3_key:
        kwargs['PlatformDefinitionBundle'] = {'S3Bucket': s3_bucket, 'S3Key': s3_key}

    option_settings = []

    if instance_profile:
        option_settings.append({
            'Namespace': namespaces.LAUNCH_CONFIGURATION,
            'OptionName': option_names.IAM_INSTANCE_PROFILE,
            'Value': instance_profile
        })
    if key_name:
        option_settings.append({
            'Namespace': namespaces.LAUNCH_CONFIGURATION,
            'OptionName': option_names.EC2_KEY_NAME,
            'Value': key_name
        })
    if instance_type:
        option_settings.append({
            'Namespace': namespaces.LAUNCH_CONFIGURATION,
            'OptionName': option_names.INSTANCE_TYPE,
            'Value': instance_type
        })
    if vpc:
        if vpc['id']:
            option_settings.append({
                'Namespace': namespaces.VPC,
                'OptionName': option_names.VPC_ID,
                'Value': vpc['id']
            })
        if vpc['subnets']:
            option_settings.append({
                'Namespace': namespaces.VPC,
                'OptionName': option_names.SUBNETS,
                'Value': vpc['subnets']
            })
        if vpc['publicip']:
            option_settings.append({
                'Namespace': namespaces.VPC,
                'OptionName': option_names.PUBLIC_IP,
                'Value': 'true'
            })

    # Always enable healthd for the Platform Builder environment
    option_settings.append({
        'Namespace': namespaces.HEALTH_SYSTEM,
        'OptionName': option_names.SYSTEM_TYPE,
        'Value': 'enhanced'
    })

    # Attach service role
    option_settings.append({
        'Namespace': namespaces.ENVIRONMENT,
        'OptionName': option_names.SERVICE_ROLE,
        'Value': 'aws-elasticbeanstalk-service-role'
    })

    LOG.debug('Inside create_platform_version api wrapper')
    return _make_api_call('create_platform_version',
                          PlatformName=platform_name,
                          PlatformVersion=version,
                          OptionSettings=option_settings,
                          **kwargs)


def create_application_version(app_name, vers_label, descrip, s3_bucket,
                               s3_key, process=False, repository=None, commit_id=None, build_configuration=None):
    kwargs = dict()
    kwargs['Process'] = process
    if descrip is not None:
        kwargs['Description'] = descrip
    if s3_bucket and s3_key:
        if build_configuration is None:
            kwargs['SourceBundle'] = {'S3Bucket': s3_bucket,
                                      'S3Key': s3_key}
        else:
            kwargs['SourceBuildInformation'] = {'SourceType': 'Zip',
                                                'SourceRepository': 'S3',
                                                'SourceLocation': "{0}/{1}".format(s3_bucket, s3_key)}
    elif repository and commit_id:
        kwargs['SourceBuildInformation'] = {'SourceType': 'Git',
                                  'SourceRepository': 'CodeCommit',
                                  'SourceLocation': "{0}/{1}".format(repository, commit_id)}
        kwargs['Process'] = True

    if build_configuration is not None:
        kwargs['BuildConfiguration'] = {"CodeBuildServiceRole": build_configuration.service_role,
                                        "Image": build_configuration.image,
                                        "ComputeType": build_configuration.compute_type,
                                        "TimeoutInMinutes": build_configuration.timeout}
        kwargs['Process'] = True

    LOG.debug('Inside create_application_version api wrapper')
    return _make_api_call('create_application_version',
                          ApplicationName=app_name,
                          VersionLabel=vers_label,
                          **kwargs)


def create_environment(environment):
    """
    Creates an Elastic Beanstalk environment
    """
    LOG.debug('Inside create_environment api wrapper')

    kwargs = environment.convert_to_kwargs()

    if environment.database:
        # need to know region for database string
        region = aws.get_region_name()

        # Database is a dictionary
        kwargs['TemplateSpecification'] = {
            'TemplateSnippets': [
                {'SnippetName': 'RdsExtensionEB',
                 'Order': 10000,
                 'SourceUrl': 'https://s3.amazonaws.com/'
                              'elasticbeanstalk-env-resources-' + region +
                              '/eb_snippets/rds/rds.json'}
            ]
        }

    result = _make_api_call('create_environment', **kwargs)

    # convert to object
    env = _api_to_environment(result)
    request_id = result['ResponseMetadata']['RequestId']
    return env, request_id


def clone_environment(clone):
    LOG.debug('Inside clone_environment api wrapper')

    kwargs = clone.convert_to_kwargs()

    kwargs['TemplateSpecification'] = \
        {'TemplateSource': {'EnvironmentName': clone.original_name}}

    result = _make_api_call('create_environment', **kwargs)

    # convert to object
    env = _api_to_environment(result)
    request_id = result['ResponseMetadata']['RequestId']
    return env, request_id


def _api_to_environment(api_dict, want_solution_stack = False):
    # Convert solution_stack and tier to objects
    try:
        if want_solution_stack:
            solution_stack_name = api_dict['SolutionStackName']
            platform = SolutionStack(solution_stack_name)
        else:
            platform_arn = api_dict['PlatformArn']
            platform = PlatformVersion(platform_arn)
    except KeyError:
        platform = SolutionStack(api_dict['SolutionStackName'])

    tier = api_dict['Tier']
    tier = Tier(tier['Name'], tier['Type'], tier['Version'])

    env = Environment(
        version_label=api_dict.get('VersionLabel'),
        status=api_dict.get('Status'),
        app_name=api_dict.get('ApplicationName'),
        health=api_dict.get('Health'),
        id=api_dict.get('EnvironmentId'),
        date_updated=api_dict.get('DateUpdated'),
        platform=platform,
        description=api_dict.get('Description'),
        name=api_dict.get('EnvironmentName'),
        date_created=api_dict.get('DateCreated'),
        tier=tier,
        cname=api_dict.get('CNAME', 'UNKNOWN'),
        option_settings=api_dict.get('OptionSettings'),
        is_abortable=api_dict.get('AbortableOperationInProgress', False),
        environment_links=api_dict.get('EnvironmentLinks')
    )
    return env


def delete_application(app_name):
    LOG.debug('Inside delete_application api wrapper')
    result = _make_api_call('delete_application',
                            ApplicationName=app_name)
    return result['ResponseMetadata']['RequestId']


def delete_application_version(app_name, version_label):
    LOG.debug('Inside delete_application_version api wrapper')
    result = _make_api_call('delete_application_version',
                            ApplicationName=app_name,
                            VersionLabel=version_label,
                            DeleteSourceBundle=True)
    return result['ResponseMetadata']['RequestId']


def delete_application_and_envs(app_name):
    LOG.debug('Inside delete_application_and_envs')
    result = _make_api_call('delete_application',
                            ApplicationName=app_name,
                            TerminateEnvByForce=True)
    return result['ResponseMetadata']['RequestId']


def describe_application(app_name):
    LOG.debug('Inside describe_application api wrapper')
    result = _make_api_call('describe_applications',
                            ApplicationNames=[app_name])
    apps = result['Applications']
    if len(apps) != 1:
        raise NotFoundError('Application "' + app_name + '" not found.')
    return apps[0]


def is_cname_available(cname):
    LOG.debug('Inside is_cname_available api wrapper')
    result = _make_api_call('check_dns_availability',
                            CNAMEPrefix=cname)
    return result['Available']


def swap_environment_cnames(source_env, dest_env):
    LOG.debug('Inside swap_environment_cnames api wrapper')
    result = _make_api_call('swap_environment_cnames',
                            SourceEnvironmentName=source_env,
                            DestinationEnvironmentName=dest_env)
    return result['ResponseMetadata']['RequestId']


def describe_applications():
    LOG.debug('Inside describe_applications api wrapper')
    result = _make_api_call('describe_applications')
    return result['Applications']


def application_exist(app_name):
    try:
        describe_application(app_name)
    except NotFoundError:
        return False
    return True


def describe_configuration_settings(app_name, env_name):
    LOG.debug('Inside describe_configuration_settings api wrapper')
    result = _make_api_call('describe_configuration_settings',
                            ApplicationName=app_name,
                            EnvironmentName=env_name)
    return result['ConfigurationSettings'][0]


def get_option_setting_from_environment(app_name, env_name, namespace, option):
    env = describe_configuration_settings(app_name, env_name)
    try:
        option_settings = env['OptionSettings']
        return get_option_setting(option_settings, namespace, option)
    except KeyError:
        return None


def get_option_setting(option_settings, namespace, option):
    for setting in option_settings:
        if setting['Namespace'] == namespace and \
                                setting['OptionName'] == option:
            try:
                return setting['Value']
            except KeyError:
                return None

    return None


def create_option_setting(namespace, option, value):
    return {
        'Namespace': namespace,
        'OptionName': option,
        'Value': value
    }


def get_specific_configuration(env_config, namespace, option):
    return get_option_setting(env_config['OptionSettings'], namespace, option)


def get_specific_configuration_for_env(app_name, env_name, namespace, option):
    env_config = describe_configuration_settings(app_name, env_name)
    return get_specific_configuration(env_config, namespace, option)


def get_available_solution_stacks(fail_on_empty_response=True):
    LOG.debug('Inside get_available_solution_stacks api wrapper')
    result = _make_api_call('list_available_solution_stacks')
    stack_strings = result['SolutionStacks']

    LOG.debug('Solution Stack result size = ' + str(len(stack_strings)))

    if fail_on_empty_response and len(stack_strings) == 0:
        raise NotFoundError(strings['sstacks.notfound'])

    solution_stacks = [SolutionStack(s) for s in stack_strings]

    return solution_stacks


def get_application_versions(app_name, version_labels=None, max_records=None, next_token=None):
    LOG.debug('Inside get_application_versions api wrapper')
    kwargs = {}
    if version_labels:
        kwargs['VersionLabels'] = version_labels
    if max_records:
        kwargs['MaxRecords'] = max_records
    if next_token:
        time.sleep(0.1) # To avoid throttling we sleep for 100ms before requesting the next page
        kwargs['NextToken'] = next_token
    result = _make_api_call('describe_application_versions',
                            ApplicationName=app_name,
                            **kwargs)
    return result


def get_all_applications():
    LOG.debug('Inside get_all_applications api wrapper')
    result = _make_api_call('describe_applications')
    app_list = []
    for app in result['Applications']:
        try:
            description = app['Description']
        except KeyError:
            description = None

        try:
            versions = app['Versions']
        except KeyError:
            versions = None
        app_list.append(
            Application(
                name=app['ApplicationName'],
                date_created=app['DateCreated'],
                date_updated=app['DateUpdated'],
                description=description,
                versions=versions,
                templates=app['ConfigurationTemplates'],
            )
        )

    return app_list


def get_raw_app_environments(app_name, include_deleted=False, deleted_back_to=None):
    LOG.debug('Inside get_app_environments api wrapper')

    kwargs = {}
    if include_deleted and deleted_back_to is not None:
        kwargs['IncludedDeletedBackTo'] = deleted_back_to

    result = _make_api_call('describe_environments',
                            ApplicationName=app_name,
                            IncludeDeleted=include_deleted,
                            **kwargs)
    return result['Environments']


def get_app_environments(app_name, include_deleted=False, deleted_back_to=None):
    LOG.debug('Inside get_app_environments api wrapper')

    kwargs = {}
    if include_deleted and deleted_back_to is not None:
        kwargs['IncludedDeletedBackTo'] = deleted_back_to

    result = _make_api_call('describe_environments',
                            ApplicationName=app_name,
                            IncludeDeleted=include_deleted,
                            **kwargs)
    # convert to objects
    envs = [_api_to_environment(env) for env in result['Environments']]

    return envs


def get_all_environments():
    LOG.debug('Inside get_all_environments api wrapper')
    result = _make_api_call('describe_environments',
                            IncludeDeleted=False)
    # convert to object
    envs = []
    for env in result['Environments']:
        envs.append(_api_to_environment(env))
    return envs


def get_environment(app_name, env_name, env_id=None, include_deleted=False, deleted_back_to=None, want_solution_stack=False):
    LOG.debug('Inside get_environment api wrapper')

    kwargs = {}
    if app_name is not None:
        kwargs['ApplicationName'] = app_name
    if env_name is not None:
        kwargs['EnvironmentNames'] = [env_name]
    if env_id is not None:
        kwargs['EnvironmentIds'] = [env_id]
    if include_deleted and deleted_back_to is not None:
        kwargs['IncludedDeletedBackTo'] = deleted_back_to

    result = _make_api_call('describe_environments',
                            IncludeDeleted=include_deleted,
                            **kwargs)

    envs = result['Environments']
    if len(envs) < 1:
        env_str = env_id if env_name is None else env_name
        raise NotFoundError('Environment "' + env_str + '" not Found.')
    else:
        return _api_to_environment(envs[0], want_solution_stack)


def get_environments(env_names=[]):
    LOG.debug('Inside get_environments api wrapper')
    result = _make_api_call('describe_environments',
                            EnvironmentNames=env_names,
                            IncludeDeleted=False)

    envs = result['Environments']
    if len(envs) < 1:
        raise NotFoundError('Could not find any environments '
                            'from the list: [' + env_names + ']')
    return [_api_to_environment(env) for env in envs]


def get_environment_settings(app_name, env_name):
    LOG.debug('Inside get_environment_settings api wrapper')
    result = _make_api_call('describe_configuration_settings',
                            ApplicationName=app_name,
                            EnvironmentName=env_name)

    return _api_to_environment(result['ConfigurationSettings'][0])


def get_environment_resources(env_name):
    LOG.debug('Inside get_environment_resources api wrapper')
    result = _make_api_call('describe_environment_resources',
                            EnvironmentName=env_name)
    return result


def get_new_events(app_name, env_name, request_id,
                   last_event_time=None, version_label=None, platform_arn=None):
    LOG.debug('Inside get_new_events api wrapper')
    # make call
    if last_event_time is not None:
        # In python 2 time is a datetime, in 3 it is a string
        ## Convert to string for compatibility
        time = last_event_time
        new_time = time + datetime.timedelta(0, 0, 1000)
    else:
        new_time = None
    kwargs = {}
    if app_name:
        kwargs['ApplicationName'] = app_name
    if version_label:
        kwargs['VersionLabel'] = version_label
    if env_name:
        kwargs['EnvironmentName'] = env_name
    if request_id:
        kwargs['RequestId'] = request_id
    if new_time:
        kwargs['StartTime'] = str(new_time)
    if platform_arn:
        kwargs['PlatformArn'] = platform_arn

    result = _make_api_call('describe_events',
                            **kwargs)

    # convert to object
    events = []
    for event in result['Events']:
        try:
            version_label = event['VersionLabel']
        except KeyError:
            version_label = None

        try:
            environment_name = event['EnvironmentName']
        except KeyError:
            environment_name = None

        try:
            app_name = event['ApplicationName']
        except KeyError:
            app_name = None

        events.append(
            Event(message=event['Message'],
                  event_date=event['EventDate'],
                  version_label=version_label,
                  app_name=app_name,
                  environment_name=environment_name,
                  severity=event['Severity'],
                  platform=platform_arn
            )
        )
    return events


def get_storage_location():
    LOG.debug('Inside get_storage_location api wrapper')
    response = _make_api_call('create_storage_location')
    return response['S3Bucket']


def update_environment(env_name, options, remove=None,
                       template=None, template_body=None,
                       solution_stack_name=None,
                       platform_arn=None):
    LOG.debug('Inside update_environment api wrapper')
    if remove is None:
        remove = []
    kwargs = {
        'EnvironmentName': env_name,

    }
    if options:
        kwargs['OptionSettings'] = options
    if remove:
        kwargs['OptionsToRemove'] = remove
    if template:
        kwargs['TemplateName'] = template
    if template_body:
        kwargs['TemplateSpecification'] = \
            {'TemplateSource':
                {'SourceContents': template_body}}
    if solution_stack_name:
        kwargs['SolutionStackName'] = solution_stack_name
    if platform_arn:
        kwargs['PlatformArn'] = platform_arn

    try:
        response = _make_api_call('update_environment',
                                  **kwargs)
    except aws.InvalidParameterValueError as e:
        if e.message == responses['env.invalidstate'].replace('{env-name}',
                                                              env_name):
            raise InvalidStateError(e)
        else:
            raise
    return response['ResponseMetadata']['RequestId']


def abort_environment_update(env_name):
    LOG.debug('Inside abort_environment_update')
    result = _make_api_call('abort_environment_update',
                            EnvironmentName=env_name)
    return result['ResponseMetadata']['RequestId']


def update_application_resource_lifecycle(app_name, resource_config):
    LOG.debug('Inside update_application_resource_lifecycle api wrapper')

    response = _make_api_call('update_application_resource_lifecycle',
                              ApplicationName=app_name,
                              ResourceLifecycleConfig=resource_config)

    return response


def update_env_application_version(env_name,
                                   version_label,
                                   group_name):
    LOG.debug('Inside update_env_application_version api wrapper')
    if group_name:
        response = _make_api_call('update_environment',
                                  EnvironmentName=env_name,
                                  VersionLabel=version_label,
                                  GroupName=group_name)
    else:
        response = _make_api_call('update_environment',
                                  EnvironmentName=env_name,
                                  VersionLabel=version_label)
    return response['ResponseMetadata']['RequestId']


def request_environment_info(env_name, info_type):
    result = _make_api_call('request_environment_info',
                            EnvironmentName=env_name,
                            InfoType=info_type)
    return result


def retrieve_environment_info(env_name, info_type):
    result = _make_api_call('retrieve_environment_info',
                            EnvironmentName=env_name,
                            InfoType=info_type)
    return result


def terminate_environment(env_name, force_terminate=False):
    result = _make_api_call('terminate_environment',
                            EnvironmentName=env_name,
                            ForceTerminate=force_terminate)
    return result['ResponseMetadata']['RequestId']


def create_configuration_template(app_name, env_name, template_name,
                                  description):
    kwargs = {
        'TemplateName': template_name,
        'ApplicationName': app_name,
        'Description': description,
        'TemplateSpecification':
            {'TemplateSource':
                {'EnvironmentName': env_name}},
    }

    try:
        result = _make_api_call('create_configuration_template', **kwargs)
    except InvalidParameterValueError as e:
        if e.message == responses['cfg.nameexists'].replace('{name}',
                                                            template_name):
            raise AlreadyExistsError(e.message)
        else:
            raise

    return result


def delete_configuration_template(app_name, template_name):
    _make_api_call('delete_configuration_template',
                   ApplicationName=app_name,
                   TemplateName=template_name)


def validate_template(app_name, template_name, platform=None):
    kwargs = {}
    if platform:
        if PlatformVersion.is_valid_arn(platform):
            kwargs['TemplateSpecification'] = \
                {'TemplateSource':
                     {'PlatformArn': platform}}
        else:
            kwargs['TemplateSpecification'] = \
                {'TemplateSource':
                    {'SolutionStackName': platform}}



    result = _make_api_call('validate_configuration_settings',
                            ApplicationName=app_name,
                            TemplateName=template_name,
                            **kwargs)
    return result


def describe_template(app_name, template_name):
    LOG.debug('Inside describe_template api wrapper')
    result = _make_api_call('describe_configuration_settings',
                            ApplicationName=app_name,
                            TemplateName=template_name)
    return result['ConfigurationSettings'][0]


def get_environment_health(env_name, attributes=None):
    if attributes is None:
        attributes = [
            "HealthStatus",
            "Status",
            "Color",
            "Causes",
            "ApplicationMetrics",
            "InstancesHealth",
            "RefreshedAt",
        ]
    result = _make_api_call('describe_environment_health',
                            EnvironmentName=env_name,
                            AttributeNames=attributes)
    return result


def get_instance_health(env_name, next_token=None, attributes=None):
    if attributes is None:
        attributes = [
            "HealthStatus",
            "Color",
            "Causes",
            "ApplicationMetrics",
            "RefreshedAt",
            "LaunchedAt",
            "System",
            "Deployment",
            "AvailabilityZone",
            "InstanceType",
        ]
    kwargs = {}
    if next_token:
        time.sleep(0.1)  # To avoid throttling we sleep for 100ms before requesting the next page
        kwargs['NextToken'] = next_token
    result = _make_api_call('describe_instances_health',
                            EnvironmentName=env_name,
                            AttributeNames=attributes,
                            **kwargs)
    return result


def compose_environments(application_name, version_labels_list, group_name=None):
    kwargs = {}
    if group_name is not None:
        kwargs['GroupName'] = group_name
    result = _make_api_call('compose_environments',
                            ApplicationName=application_name,
                            VersionLabels=version_labels_list,
                            **kwargs)
    request_id = result['ResponseMetadata']['RequestId']

    return request_id


def rebuild_environment(env_id=None, env_name=None):
    kwargs = {}
    if env_name is not None:
        kwargs['EnvironmentName'] = env_name
    if env_id is not None:
        kwargs['EnvironmentId'] = env_id

    result = _make_api_call('rebuild_environment',
                            **kwargs)

    request_id = result['ResponseMetadata']['RequestId']
    return request_id
