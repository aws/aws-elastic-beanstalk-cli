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
from cement.utils.misc import minimal_logger

from ebcli.core import fileoperations, io
from ebcli.lib import elasticbeanstalk, heuristics, aws, codebuild
from ebcli.objects.exceptions import CredentialsError, NotAuthorizedError
from ebcli.objects.sourcecontrol import SourceControl
from ebcli.resources.strings import strings
from ebcli.core.ebglobals import Constants

LOG = minimal_logger(__name__)


def setup(
        app_name,
        region,
        solution,
        workspace_type=Constants.WorkSpaceTypes.APPLICATION,
        platform_name=None,
        platform_version=None,
        instance_profile=None,
        dir_path=None,
        repository=None,
        branch=None):

    setup_directory(
        app_name,
        region,
        solution,
        workspace_type=workspace_type,
        platform_name=platform_name,
        platform_version=platform_version,
        instance_profile=instance_profile,
        dir_path=dir_path,
        repository=repository,
        branch=branch)

    if (
        solution is not None
        and 'tomcat' in solution.lower()
        and heuristics.has_tomcat_war_file()
    ):
        war_file = fileoperations.get_war_file_location()
        fileoperations.write_config_setting('deploy', 'artifact', war_file)

    setup_ignore_file()


def setup_directory(
        app_name,
        region,
        solution,
        workspace_type,
        platform_name,
        platform_version,
        instance_profile,
        dir_path=None,
        repository=None,
        branch=None):

    io.log_info('Setting up .elasticbeanstalk directory')
    fileoperations.create_config_file(
        app_name,
        region,
        solution,
        workspace_type,
        platform_name,
        platform_version,
        instance_profile,
        dir_path=dir_path,
        repository=repository,
        branch=branch)


def setup_ignore_file():
    io.log_info('Setting up ignore file for source control')
    sc = fileoperations.get_config_setting('global', 'sc')

    if not sc:
        source_control = SourceControl.get_source_control()
        source_control.set_up_ignore_file()
        sc_name = source_control.get_name()
        fileoperations.write_config_setting('global', 'sc', sc_name)


def get_codebuild_image_from_platform(platform):
    platform_image = None
    beanstalk_images = codebuild.list_curated_environment_images()
    for image in beanstalk_images:
        if platform in image['description']:
            platform_image = image

    LOG.debug("Searching for images for platform '{0}'. Found: {1}".format(platform, platform_image))

    return beanstalk_images if platform_image is None else platform_image
