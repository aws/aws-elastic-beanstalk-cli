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

from cement.utils.misc import minimal_logger

from ..lib import elasticbeanstalk
from ..display.data_poller import DataPoller
from ..display.screen import Screen
from ..display.traditional import TraditionalHealthScreen, TraditionalHealthDataPoller
from ..display.help import HelpTable, ViewlessHelpTable
from ..display import term
from ..display.table import Column, Table
from ..display.specialtables import RequestTable, StatusTable
from ..objects.exceptions import NotSupportedError
from ..objects.solutionstack import SolutionStack
from ..resources.statics import namespaces, option_names

LOG = minimal_logger(__name__)


def display_interactive_health(app_name, env_name, refresh,
                               mono, default_view):
    env = elasticbeanstalk.describe_configuration_settings(app_name, env_name)
    option_settings = env.get('OptionSettings')
    health_type = elasticbeanstalk.get_option_setting(
        option_settings,
        namespaces.HEALTH_SYSTEM,
        option_names.SYSTEM_TYPE)

    if health_type == 'enhanced':
        poller = DataPoller
        # Create dynamic screen
        screen = Screen()
        create_health_tables(screen, env)
    elif env['Tier']['Name'] == 'WebServer':
        poller = TraditionalHealthDataPoller
        screen = TraditionalHealthScreen()
        create_traditional_health_tables(screen)
    else:
        raise NotSupportedError('The health dashboard is currently not supported for this environment.')

    # Start getting health data
    poller = poller(app_name, env_name)
    poller.start_background_polling()

    # Start
    try:
        screen.start_screen(poller, env, refresh,
                            mono=mono, default_table=default_view)
    finally:
        term.return_cursor_to_normal()


def create_health_tables(screen, env):
    screen.add_table(StatusTable('health', columns=[
        Column('instance-id', None, 'InstanceId', 'left'),
        Column('status', 10, 'HealthStatus', 'left', 'status_sort'),
        Column('cause', None, 'Cause', 'none'),
    ]))
    screen.add_table(RequestTable('requests', columns=[
        Column('instance-id', None, 'InstanceId', 'left'),
        Column('r/sec', 6, 'requests', 'left'),
        Column('%2xx', 6, 'Status2xx', 'right', 'Status2xx_sort'),
        Column('%3xx', 6, 'Status3xx', 'right', 'Status3xx_sort'),
        Column('%4xx', 6, 'Status4xx', 'right', 'Status4xx_sort'),
        Column('%5xx', 6, 'Status5xx', 'right', 'Status5xx_sort'),
        Column('p99 ', 9, 'P99', 'right', 'P99_sort'),
        Column('p90 ', 8, 'P90', 'right', 'P90_sort'),
        Column('p75', 7, 'P75', 'right', 'P75_sort'),
        Column('p50', 7, 'P50', 'right', 'P50_sort'),
        Column('p10', 7, 'P10', 'right', 'P10_sort'),
    ]))
    screen.add_table(Table('cpu', columns=[
        Column('instance-id', None, 'InstanceId', 'left'),
        Column('type', None, 'InstanceType', 'left'),
        Column('az', None, 'AvailabilityZone', 'left'),
        Column('running', 10, 'running', 'left', 'LaunchedAt'),
        Column('load 1', 7, 'load1', 'right'),
        Column('load 5', 7, 'load5', 'right'),
        Column('user%', 10, 'User', 'right'),
        Column('nice%', 6, 'Nice', 'right'),
        Column('system%', 8, 'System', 'right'),
        Column('idle%', 6, 'Idle', 'right'),
        Column('iowait%', 9, 'IOWait', 'right'),
    ]))
    if SolutionStack(env['SolutionStackName']).has_healthd_group_version_2_support():
        screen.add_table(Table('deployments', columns=[
            Column('instance-id', None, 'InstanceId', 'left'),
            Column('status', None, 'DeploymentStatus', 'left'),
            Column('id', None, 'DeploymentId', 'left'),
            Column('version', None, 'DeploymentVersion', 'left'),
            Column('ago', None, 'TimeSinceDeployment', 'left'),
        ]))
    screen.add_help_table(HelpTable())


def create_traditional_health_tables(screen):
    screen.add_table(Table('health', columns=[
        Column('instance-id', 19, 'id', 'left'),
        Column('EC2 Health', 15, 'health', 'left'),
        Column('ELB State', 15, 'state', 'left'),
        Column('ELB description', 40, 'description', 'none'),
    ]))
    screen.add_help_table(ViewlessHelpTable())
