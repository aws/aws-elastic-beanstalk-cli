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

from ..lib import elasticbeanstalk, elb
from ..core import io
from ..resources.strings import alerts
from ..objects.exceptions import NotFoundError
from . import commonops


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
            instance_states = elb.get_health_of_instances(load_balancer_name)
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

    # check platform version
    latest = commonops.get_latest_solution_stack(env.platform.version)
    if env.platform != latest:
        io.log_alert(alerts['platform.old'])