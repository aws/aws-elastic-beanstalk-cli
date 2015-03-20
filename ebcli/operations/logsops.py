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

from datetime import datetime, timedelta
import os
import sys

from botocore.compat import six
from six import iteritems

from ..core import fileoperations, io
from ..lib import elasticbeanstalk, utils
from ..resources.strings import strings, prompts
from . import commonops


def logs(env_name, info_type, do_zip=False, instance_id=None):
    # Request info
    result = elasticbeanstalk.request_environment_info(env_name, info_type)

    # Wait for logs to finish
    request_id = result['ResponseMetadata']['RequestId']
    io.echo(prompts['logs.retrieving'])
    commonops.wait_for_success_events(request_id, timeout_in_minutes=2,
                                      sleep_time=1, stream_events=False)

    get_logs(env_name, info_type, do_zip=do_zip,
             instance_id=instance_id)


def get_logs(env_name, info_type, do_zip=False, instance_id=None):
    # Get logs
    result = elasticbeanstalk.retrieve_environment_info(env_name, info_type)

    """
    Results are ordered with latest last, we just want the latest
    """
    log_list = {}
    for log in result['EnvironmentInfo']:
        i_id = log['Ec2InstanceId']
        url = log['Message']
        log_list[i_id] = url

    if instance_id:
        log_list = {instance_id: log_list[instance_id]}

    if info_type == 'bundle':
        # save file, unzip, place in logs directory
        logs_folder_name = datetime.now().strftime("%y%m%d_%H%M%S")
        logs_location = fileoperations.get_logs_location(logs_folder_name)
        #get logs for each instance
        for i_id, url in iteritems(log_list):
            zip_location = utils.save_file_from_url(url, logs_location,
                                                    i_id + '.zip')
            instance_folder = os.path.join(logs_location, i_id)
            fileoperations.unzip_folder(zip_location, instance_folder)
            fileoperations.delete_file(zip_location)

        fileoperations.set_user_only_permissions(logs_location)
        if do_zip:
            fileoperations.zip_up_folder(logs_location, logs_location + '.zip')
            fileoperations.delete_directory(logs_location)

            logs_location += '.zip'
            fileoperations.set_user_only_permissions(logs_location)
            io.echo(strings['logs.location'].replace('{location}',
                                                     logs_location))
        else:
            io.echo(strings['logs.location'].replace('{location}',
                                                     logs_location))
            # create symlink to logs/latest
            latest_location = fileoperations.get_logs_location('latest')
            try:
                os.unlink(latest_location)
            except OSError:
                # doesn't exist. Ignore
                pass
            try:
                os.symlink(logs_location, latest_location)
                io.echo('Updated symlink at', latest_location)
            except OSError:
                #Oh well.. we tried.
                ## Probably on windows, or logs/latest is not a symlink
                pass

    else:
        # print logs
        data = []
        for i_id, url in iteritems(log_list):
            data.append('============= ' + str(i_id) + ' ==============')
            log_result = utils.get_data_from_url(url)
            if sys.version_info[0] >= 3:
                log_result = log_result.decode()
            data.append(log_result)
        io.echo_with_pager(os.linesep.join(data))