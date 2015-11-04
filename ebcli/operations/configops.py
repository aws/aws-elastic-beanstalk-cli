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

import os

from ..lib import elasticbeanstalk
from ..core import io, fileoperations
from ..objects import configuration
from ..objects.exceptions import InvalidSyntaxError
from ..resources.strings import prompts, strings
from . import commonops


def update_environment_configuration(app_name, env_name, nohang,
                                     timeout=None):
    # get environment setting
    api_model = elasticbeanstalk.describe_configuration_settings(
        app_name, env_name
    )

    # Turn them into a yaml file and open
    file_location = save_env_file(api_model)
    open_file_for_editing(file_location)

    # Update and delete file
    try:
        usr_model = fileoperations.get_environment_from_file(env_name)
        changes, remove = configuration.collect_changes(api_model, usr_model)
        if api_model['SolutionStackName'] != usr_model['SolutionStackName']:
            solution_name = usr_model['SolutionStackName']
        else:
            solution_name = None
        fileoperations.delete_env_file(env_name)
    except InvalidSyntaxError:
        io.log_error(prompts['update.invalidsyntax'])
        return

    if not changes and not remove and not solution_name:
        # no changes made, exit
        io.log_warning('No changes made. Exiting.')
        return

    if fileoperations.env_yaml_exists():
        io.echo(strings['config.envyamlexists'])

    commonops.update_environment(env_name, changes, nohang,
                                 remove=remove, timeout=timeout,
                                 solution_stack_name=solution_name)


def save_env_file(api_model):
    usr_model = configuration.convert_api_to_usr_model(api_model)
    file_location = fileoperations.save_env_file(usr_model)
    return file_location


def open_file_for_editing(file_location):

    editor = fileoperations.get_editor()
    if editor:
        try:
            os.system(editor + ' ' + file_location)
        except OSError:
            io.log_error(prompts['fileopen.error1'].replace('{editor}',
                                                            editor))
    else:
        try:
            os.system(file_location)
        except OSError:
            io.log_error(prompts['fileopen.error2'])