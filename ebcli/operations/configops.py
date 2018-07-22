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

from ebcli.lib import elasticbeanstalk
from ebcli.core import io, fileoperations
from ebcli.objects.environmentsettings import EnvironmentSettings
from ebcli.objects.exceptions import InvalidSyntaxError
from ebcli.resources.strings import prompts, strings
from ebcli.operations import commonops


def update_environment_configuration(app_name, env_name, nohang,
                                     timeout=None):
    # get environment setting
    api_model = elasticbeanstalk.describe_configuration_settings(
        app_name, env_name
    )

    # Convert the raw api return to yaml format
    env_settings = EnvironmentSettings(api_model)
    usr_model = env_settings.convert_api_to_usr_model()

    # Save the yaml in a temp file
    file_location = fileoperations.save_env_file(usr_model)
    fileoperations.open_file_for_editing(file_location)

    platform_arn = None

    # Update and delete file
    try:
        usr_model = fileoperations.get_environment_from_file(env_name)
        changes, remove = env_settings.collect_changes(usr_model)
        if api_model['PlatformArn'] != usr_model['PlatformArn']:
            platform_arn = usr_model['PlatformArn']
        fileoperations.delete_env_file(env_name)
    except InvalidSyntaxError:
        io.log_error(prompts['update.invalidsyntax'])
        return

    if not changes and not remove and not platform_arn:
        # no changes made, exit
        io.log_warning('No changes made. Exiting.')
        return

    if fileoperations.env_yaml_exists():
        io.echo(strings['config.envyamlexists'])

    commonops.update_environment(env_name, changes, nohang,
                                 remove=remove, timeout=timeout,
                                 solution_stack_name=None,
                                 platform_arn=platform_arn)


def save_env_file(api_model):
    usr_model = configuration.convert_api_to_usr_model(api_model)
    file_location = fileoperations.save_env_file(usr_model)
    return file_location
