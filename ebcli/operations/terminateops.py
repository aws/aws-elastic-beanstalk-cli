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
from collections import defaultdict

from botocore.compat import six

from ..lib import elasticbeanstalk, s3
from ..resources.strings import prompts
from ..core import io, fileoperations
from ..objects.sourcecontrol import SourceControl
from ..objects.exceptions import NotAuthorizedError
from . import commonops


def terminate(
        env_name,
        force_terminate=False,
        nohang=False,
        timeout=15
):
    request_id = elasticbeanstalk.terminate_environment(
        env_name,
        force_terminate=force_terminate
    )

    dissociate_environment_from_branch(env_name)

    if not nohang:
        commonops.wait_for_success_events(
            request_id,
            timeout_in_minutes=timeout
        )


def dissociate_environment_from_branch(env_name):
    default_env = commonops.get_current_branch_environment()
    if default_env == env_name:
        commonops.set_environment_for_current_branch(None)


def delete_app(
        app_name,
        force,
        nohang=False,
        cleanup=True,
        timeout=15
):
    if not force:
        ask_for_customer_confirmation_to_delete_all_application_resources(app_name)

    cleanup_application_versions(app_name)

    request_id = elasticbeanstalk.delete_application_and_envs(app_name)

    if cleanup:
        cleanup_ignore_file()
        fileoperations.clean_up()

    if not nohang:
        commonops.wait_for_success_events(
            request_id,
            sleep_time=5,
            timeout_in_minutes=timeout
        )


def ask_for_customer_confirmation_to_delete_all_application_resources(app_name):
    application = elasticbeanstalk.describe_application(app_name)

    application['Versions'] = application.get('Versions', [])

    environments = elasticbeanstalk.get_environment_names(app_name)
    confirm_message = prompts['delete.confirm'].format(
        app_name=app_name,
        env_num=len(environments),
        config_num=len(application['ConfigurationTemplates']),
        version_num=len(application['Versions'])
    )
    io.echo(confirm_message)
    io.validate_action(prompts['delete.validate'], app_name)


def cleanup_application_versions(app_name):
    io.echo('Removing application versions from s3.')
    versions = elasticbeanstalk.get_application_versions(app_name)['ApplicationVersions']
    buckets = defaultdict(list)
    for version in versions:
        bundle = version.get('SourceBundle', {})
        bucket = bundle.get('S3Bucket')
        key = bundle.get('S3Key')
        if bucket and key:
            buckets[bucket].append(key)

    for bucket, keys in six.iteritems(buckets):
        try:
            s3.delete_objects(bucket, keys)
        except NotAuthorizedError:
            io.log_warning(
                'Error deleting application versions from bucket "{0}"'.format(bucket)
            )


def cleanup_ignore_file():
    sc = fileoperations.get_config_setting('global', 'sc')

    if sc:
        source_control = SourceControl.get_source_control()
        source_control.clean_up_ignore_file()
        fileoperations.write_config_setting('global', 'sc', None)
