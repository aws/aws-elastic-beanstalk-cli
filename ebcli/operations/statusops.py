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

from ..lib import elasticbeanstalk, elb, elbv2
from ..core import io
from ..resources.strings import alerts
from ..resources.statics import elb_names
from ..objects.exceptions import NotFoundError
from . import commonops, gitops


SPACER = ' ' * 5
def status(app_name, env_name, verbose):
    env = elasticbeanstalk.get_environment(app_name, env_name)
    commonops.print_env_details(env, health=True)

    if verbose:
        # Print number of running instances
        env_dict = elasticbeanstalk.get_environment_resources(env_name)
        instances = [i['Id'] for i in
                     env_dict['EnvironmentResources']['Instances']]
        io.echo('  Running instances:', len(instances))
        #Get elb health
        try:
            load_balancer_name = [i['Name'] for i in
                                  env_dict['EnvironmentResources']['LoadBalancers']][0]
            if elb.version(load_balancer_name) == elb_names.APPLICATION_VERSION:
                target_groups = [x['PhysicalResourceId'] for x in env_dict['EnvironmentResources']['Resources']
                                 if elb_names.V2_RESOURCE_TYPE == x['Type'] ]
                io.echo('  Running processes:', len(target_groups))
                target_group_states = elbv2.get_target_group_healths(target_groups)

                for k in target_group_states: #k is tg arn
                    process_name = [x['LogicalResourceId'] for x in env_dict['EnvironmentResources']['Resources']
                                 if k == x['PhysicalResourceId'] ][0]
                    if elb_names.DEFAULT_PROCESS_LOGICAL_ID == process_name:
                        process_name = 'default'
                    io.echo(SPACER, process_name + ':')
                    current_target_group_instances = []
                    for target_group_description in target_group_states[k]['TargetHealthDescriptions']:
                        current_target_group_instances.append(target_group_description['Target']['Id'])
                        target_health = target_group_description['TargetHealth']

                        io.echo(SPACER * 2, target_group_description['Target']['Id'] + ': ' + target_health['State'])

                        if 'Description' in target_health and len(target_health['Description']) > 0:
                            io.echo(SPACER * 3,
                                    'Description: ' + target_health['Description'])
                        if 'Reason' in target_health and len(target_health['Reason']) > 0:
                            io.echo(SPACER * 3,
                                    'Reason: ' + target_health['Reason'])

                    for i in instances:
                        if i not in current_target_group_instances:
                            io.echo(SPACER * 2, i + ':', 'N/A (Not registered '
                                                    'with Target Group)')
            else:
                instance_states = elb.get_health_of_instances(load_balancer_name)
                for i in instance_states:
                    instance_id = i['InstanceId']
                    state = i['State']
                    descrip = i['Description']
                    if state == 'Unknown':
                        state += '(' + descrip + ')'
                    io.echo(SPACER, instance_id + ':', state)
                for i in instances:
                    if i not in [x['InstanceId'] for x in instance_states]:
                        io.echo(SPACER, i + ':', 'N/A (Not registered '
                                                'with Load Balancer)')

        except (IndexError, KeyError, NotFoundError) as e:
            #No load balancer. Dont show instance status
            pass

    latest = commonops.get_latest_solution_stack(env.platform.version)

    if env.platform != latest:
        io.log_alert(alerts['platform.old'])

    # print out code commit repos if they exist
    default_branch = gitops.get_default_branch()
    default_repo = gitops.get_default_repository()
    codecommit_setup = (default_repo and default_repo is not None) or (default_branch and default_branch is not None)
    if codecommit_setup:
        io.echo("Current CodeCommit settings:")
        io.echo("  Repository: " + str(default_repo))
        io.echo("  Branch: " + str(default_branch))