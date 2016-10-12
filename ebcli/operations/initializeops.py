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

from ..core import fileoperations, io
from ..lib import elasticbeanstalk, heuristics, aws
from ..objects.exceptions import CredentialsError, NotAuthorizedError
from ..objects.sourcecontrol import SourceControl
from ..operations import commonops
from ..resources.strings import strings


def credentials_are_valid():
    try:
        elasticbeanstalk.get_available_solution_stacks()
        return True
    except CredentialsError:
        return False
    except NotAuthorizedError as e:
        io.log_error('The current user does not have the correct permissions. '
                     'Reason: {0}'.format(e.message))
        return False


def setup(app_name, region, solution, dir_path=None, repository=None, branch=None):
    setup_directory(app_name, region, solution, dir_path=dir_path, repository=repository, branch=branch)

    # Handle tomcat special case
    if 'tomcat' in solution.lower() and \
                heuristics.has_tomcat_war_file():
        war_file = fileoperations.get_war_file_location()
        fileoperations.write_config_setting('deploy', 'artifact', war_file)

    setup_ignore_file()


def setup_credentials(access_id=None, secret_key=None):
    io.log_info('Setting up ~/aws/ directory with config file')

    if access_id is None or secret_key is None:
        io.echo(strings['cred.prompt'])

    if access_id is None:
        access_id = io.prompt('aws-access-id',
                              default='ENTER_AWS_ACCESS_ID_HERE')
    if secret_key is None:
        secret_key = io.prompt('aws-secret-key', default='ENTER_SECRET_HERE')

    fileoperations.save_to_aws_config(access_id, secret_key)

    fileoperations.touch_config_folder()
    fileoperations.write_config_setting('global', 'profile', 'eb-cli')

    aws.set_session_creds(access_id, secret_key)


def setup_directory(app_name, region, solution, dir_path=None, repository=None, branch=None):
    io.log_info('Setting up .elasticbeanstalk directory')
    fileoperations.create_config_file(app_name, region, solution, dir_path=dir_path, repository=repository, branch=branch)


def setup_ignore_file():
    io.log_info('Setting up ignore file for source control')
    sc = fileoperations.get_config_setting('global', 'sc')

    if not sc:
        source_control = SourceControl.get_source_control()
        source_control.set_up_ignore_file()
        sc_name = source_control.get_name()
        fileoperations.write_config_setting('global', 'sc', sc_name)