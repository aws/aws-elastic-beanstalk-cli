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

from ebcli.core import io
from ebcli.display.appversion import term, VersionScreen, VersionDataPoller
from ebcli.display.table import Table, Column
from ebcli.display.help import HelpTable, ViewlessHelpTable
from ebcli.lib import elasticbeanstalk as elasticbeanstalk
from ebcli.objects.exceptions import ValidationError, NotFoundError
from ebcli.operations import commonops
from ebcli.resources.strings import prompts, strings

LOG = minimal_logger(__name__)


def delete_app_version_label(app_name, version_label):

    if version_label:
        # check if version_label exists under app_name
        app_versions = elasticbeanstalk.get_application_versions(app_name)['ApplicationVersions']
        #  if the given version label does not exist at all!
        if not any(version_label == app_version['VersionLabel'] for app_version in app_versions):
            raise ValidationError(strings['appversion.delete.notfound'].format(app_name, version_label))

        envs = elasticbeanstalk.get_app_environments(app_name)

        versions_in_use = [(e.version_label, e.name) for e in envs]

        # find all the environments that are using the app version
        used_envs = [version[1] for version in versions_in_use if version[0] == version_label]

        if used_envs:
            raise ValidationError(strings['appversion.delete.deployed'].format(version_label, ','.join(used_envs)))

        try:
            io.validate_action(prompts['appversion.delete.validate'].format(version_label), "y")
            elasticbeanstalk.delete_application_version(app_name, version_label)
            io.echo('Application Version deleted successfully.')
            delete_successful = True
        except ValidationError:
            io.echo('Application Version will not be deleted.')
            delete_successful = False

        return delete_successful
    else:
        raise NotFoundError(strings['appversion.delete.none'])


def display_versions(app_name, env_name, app_versions, timeout_in_minutes=5):
    """Displays version history in birth order in a table.
    Creates poller, screen, and table.
    Displays Deploy#, Version Label, Description, Date Created, Ago.
    Returns the current version deployment number.
    """
    poller = VersionDataPoller(app_name, env_name, app_versions)
    screen = VersionScreen(poller)
    _create_version_table(screen)
    data = poller.get_version_data()

    try:
        screen.start_version_screen(data, VersionScreen.APP_VERSIONS_TABLE_NAME)
        # TODO: this would be working if redeploying a version label is enabled
        # if hasattr(screen, 'request_id') and screen.request_id:
        #     io.echo(prompts['appversion.redeploy.inprogress'].format(screen.version_label))
        #     commonops.wait_for_success_events(screen.request_id,
        #                                       timeout_in_minutes,
        #                                       can_abort=True)
    finally:
        term.return_cursor_to_normal()


def _create_version_table(screen):
    """Creates and adds a versions table and a viewless help table to the screen."""
    screen.add_table(Table(VersionScreen.APP_VERSIONS_TABLE_NAME, columns=[
        Column('#', None, 'DeployNum', 'left'),
        Column('Version Label', None, 'VersionLabel', 'left'),
        Column('Date Created', None, 'DateCreated', 'left'),
        Column('Age', None, 'SinceCreated', 'left'),
        Column('Description', None, 'Description', 'left'),
    ]))
    screen.add_help_table(ViewlessHelpTable())