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
import threading
import time

from cement.utils.misc import minimal_logger
from six import iteritems

from ..core import fileoperations, io
from ..lib import elasticbeanstalk, utils, cloudwatch
from ..lib.aws import MaxRetriesError
from ..resources.strings import strings, prompts
from ..objects.exceptions import ServiceError
from . import commonops

LOG = minimal_logger(__name__)


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


def stream_logs(env_name, sleep_time=2):
    log_group_name = 'awseb-' + env_name + '-activity'
    stream_names = []

    streamer = io.get_event_streamer()
    streamer.prompt = ' -- eb-activity log -- (Ctrl+C to exit)'
    jobs = []
    while True:
        new_names = cloudwatch.get_all_stream_names(log_group_name)
        for name in new_names:
            if name not in stream_names:
                stream_names.append(name)

                p = threading.Thread(
                    target=_stream_single_stream,
                    args=(log_group_name, name, streamer, sleep_time))
                p.daemon = True
                jobs.append(p)
                p.start()
            time.sleep(0.2)  # offset threads

        time.sleep(10)


def _stream_single_stream(log_group_name, stream_name, streamer, sleep_time=4):
    next_token = None
    while True:
        try:
            response = cloudwatch.get_log_events(log_group_name, stream_name,
                                                 next_token=next_token)

            if response and response.get('events'):
                for event in response.get('events'):
                    message = event.get('message')

                    streamer.stream_event('[{}] {}'.format(stream_name, message))

                # Set the next token
                next_token = response.get('nextForwardToken')

            else:
                time.sleep(sleep_time)
        except MaxRetriesError:
            LOG.debug('Received max retries')
            io.echo('Received Max retries. You are being heavily throttled.')
        except ServiceError as e:
            # Something went wrong getting the stream
            # It probably doesnt exist anymore.
            LOG.debug('Received service error {}'.format(e))
            return
        except Exception as e:
            # We want to swallow all exceptions or else they will be
            # printed as a stack trace to the Console
            # Exceptions are typically connections reset and
            # Various things
            LOG.debug('Exception raised: ' + str(e))
            # Loop will cause a retry