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

from ..lib import elasticbeanstalk
from ..resources.strings import prompts
from ..core import io, fileoperations
from ..objects.sourcecontrol import SourceControl
from . import commonops


def terminate(env_name, nohang=False, timeout=5):
    request_id = elasticbeanstalk.terminate_environment(env_name)

    # disassociate with branch if branch default
    default_env = commonops.get_current_branch_environment()
    if default_env == env_name:
        commonops.set_environment_for_current_branch(None)

    if not nohang:
       commonops.wait_for_success_events(request_id,
                                         timeout_in_minutes=timeout)


def delete_app(app_name, force, nohang=False, cleanup=True,
               timeout=15):
    app = elasticbeanstalk.describe_application(app_name)

    if 'Versions' not in app:
        app['Versions'] = []

    if not force:
        #Confirm
        envs = commonops.get_env_names(app_name)
        confirm_message = prompts['delete.confirm'].replace(
            '{app-name}', app_name)
        confirm_message = confirm_message.replace('{env-num}', str(len(envs)))
        confirm_message = confirm_message.replace(
            '{config-num}', str(len(app['ConfigurationTemplates'])))
        confirm_message = confirm_message.replace(
            '{version-num}', str(len(app['Versions'])))
        io.echo()
        io.echo(confirm_message)
        io.validate_action(prompts['delete.validate'], app_name)


    request_id = elasticbeanstalk.delete_application_and_envs(app_name)

    if cleanup:
        cleanup_ignore_file()
        fileoperations.clean_up()
    if not nohang:
        commonops.wait_for_success_events(request_id, sleep_time=1,
                                          timeout_in_minutes=timeout)


def cleanup_ignore_file():
    sc = fileoperations.get_config_setting('global', 'sc')

    if sc:
        source_control = SourceControl.get_source_control()
        source_control.clean_up_ignore_file()
        fileoperations.write_config_setting('global', 'sc', None)