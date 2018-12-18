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
import six

from ebcli.lib import elasticbeanstalk, elb, elbv2
from ebcli.core import io
from ebcli.resources.strings import alerts
from ebcli.operations import gitops, solution_stack_ops


SPACER = ' ' * 5


def status(app_name, env_name, verbose):
    env = elasticbeanstalk.get_environment(app_name=app_name, env_name=env_name)
    env.print_env_details(
        io.echo,
        elasticbeanstalk.get_environments,
        elasticbeanstalk.get_environment_resources,
        health=True
    )
    _print_information_about_elb_and_instances(env_name) if verbose else None
    _alert_if_platform_is_older_than_the_latest(env)
    _print_codecommit_repositories()


def _alert_if_platform_is_older_than_the_latest(env):
    latest = solution_stack_ops.find_solution_stack_from_string(env.platform.name, find_newer=True)
    if env.platform != latest:
        io.log_alert(alerts['platform.old'])


def _print_codecommit_repositories():
    default_branch = gitops.get_default_branch()
    default_repo = gitops.get_default_repository()
    if default_repo and default_branch:
        io.echo("Current CodeCommit settings:")
        io.echo("  Repository: " + str(default_repo))
        io.echo("  Branch: " + str(default_branch))


def _print_information_about_elb_and_instances(env_name):
    env_dict = elasticbeanstalk.get_environment_resources(env_name)
    instances = [instance['Id'] for instance in env_dict['EnvironmentResources']['Instances']]
    io.echo('  Running instances:', len(instances))

    load_balancers = env_dict['EnvironmentResources']['LoadBalancers']
    if load_balancers:
        load_balancer_name = load_balancers[0]['Name']
        if elb.is_classic_load_balancer(load_balancer_name):
            _print_elb_health_stats(load_balancer_name, instances)
        elif load_balancer_name:
            _print_elbv2_health_stats(load_balancer_name, instances)


def _print_elbv2_health_stats(load_balancer_name, instances):
    target_groups = [
        t['TargetGroupArn']
        for t
        in elbv2.get_target_groups_for_load_balancer(load_balancer_name)
    ]
    target_group_states = elbv2.get_target_group_healths(target_groups)

    for target_group_arn, target_group_health in six.iteritems(target_group_states):
        current_target_group_instances = []
        for target_group_description in target_group_health['TargetHealthDescriptions']:
            current_target_group_instances.append(target_group_description['Target']['Id'])
            target_health = target_group_description['TargetHealth']

            io.echo(SPACER * 2, target_group_description['Target']['Id'] + ': ' + target_health['State'])

            if 'Description' in target_health and len(target_health['Description']) > 0:
                io.echo(SPACER * 3, 'Description: ' + target_health['Description'])
            if 'Reason' in target_health and len(target_health['Reason']) > 0:
                io.echo(SPACER * 3, 'Reason: ' + target_health['Reason'])

        for i in set(instances) - set(current_target_group_instances):
            io.echo(SPACER * 2, i + ':', 'N/A (Not registered with Target Group)')


def _print_elb_health_stats(load_balancer_name, instances):
    instance_states = elb.get_health_of_instances(load_balancer_name)
    for i in instance_states:
        instance_id = i['InstanceId']
        state = i['State']
        description = i['Description']
        if state == 'Unknown':
            state += '(' + description + ')'
        io.echo(SPACER, instance_id + ':', state)
    for i in set(instances) - set([x['InstanceId'] for x in instance_states]):
        io.echo(SPACER, i + ':', 'N/A (Not registered with Load Balancer)')
