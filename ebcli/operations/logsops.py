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

from datetime import datetime
import os
import sys
import threading
import time

from cement.utils.misc import minimal_logger
from cement.core.exc import CaughtSignal
from six import iteritems

from ebcli.core import fileoperations, io
from ebcli.lib import elasticbeanstalk, utils, cloudwatch
from ebcli.lib.aws import MaxRetriesError
from ebcli.resources.strings import strings, prompts
from ebcli.resources.statics import namespaces, option_names
from ebcli.objects.exceptions import ServiceError, NotFoundError, NotAuthorizedError
from ebcli.operations import commonops

LOG = minimal_logger(__name__)
TAIL_LOG_SIZE = 100
DEFAULT_LOG_STREAMING_PATH = 'var/log/eb-activity.log'
BEANSTALK_LOG_PREFIX = '/aws/elasticbeanstalk'


def retrieve_beanstalk_logs(env_name, info_type, do_zip=False, instance_id=None):
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
        try:
            log_list = {instance_id: log_list[instance_id]}
        except KeyError:
            raise NotFoundError(strings['beanstalk-logs.badinstance'].replace('{instance_id}', instance_id))

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
            data.append(utils.decode_bytes(log_result))
        io.echo_with_pager(os.linesep.join(data))


def stream_cloudwatch_logs(env_name, sleep_time=2, log_group=None, instance_id=None):
    """
        This function will stream logs to the terminal for the log group given, if multiple streams are found we will
        spawn multiple threads with each stream switch between them to stream all streams at the same time.
        :param env_name: environment name
        :param sleep_time: sleep time to refresh the logs from cloudwatch
        :param log_group: cloudwatch log group
        :param instance_id: since all of our log streams are instance ids we require this if we want a single stream
    """
    if log_group is None:
        log_group = 'awseb-{0}-activity'.format(env_name)
        log_name = 'eb-activity.log'
    else:
        log_name = get_log_name(log_group)
    stream_names = []
    streamer = io.get_event_streamer()
    streamer.prompt = ' -- {0} -- (Ctrl+C to exit)'.format(log_name)
    jobs = []
    while True:
        try:
            new_names = cloudwatch.get_all_stream_names(log_group, instance_id)
        except:
            raise NotFoundError(strings['cloudwatch-stream.notsetup'])
        if len(new_names) == 0:
            raise NotFoundError(strings['cloudwatch-logs.nostreams'].replace('{log_group}', log_group))
        for name in new_names:
            if name not in stream_names:
                stream_names.append(name)

                p = threading.Thread(
                    target=stream_single_stream,
                    args=(log_group, name, streamer, sleep_time))
                p.daemon = True
                jobs.append(p)
                p.start()
            time.sleep(0.2)  # offset threads

        time.sleep(10)


def stream_single_stream(log_group_name, stream_name, streamer, sleep_time=4, formatter=None):
    next_token = None

    while True:
        try:
            messages = None
            messages, next_token = get_cloudwatch_messages(log_group_name, stream_name, formatter, next_token)
        except ServiceError as e:
            # Something went wrong getting the stream
            # It probably doesnt exist anymore.
            io.log_error(e)
            return
        except CaughtSignal:
            break
        except Exception as e:
            # Wait a bit before retrying
            time.sleep(0.5)
            # We want to swallow all exceptions or else they will be
            # printed as a stack trace to the Console
            # Exceptions are typically connections reset and
            # Various things
            LOG.debug('Exception raised: ' + str(e))
            # Loop will cause a retry

        if messages:
            for message in messages:
                streamer.stream_event(message)
            time.sleep(0.1)
        else:
            time.sleep(sleep_time)


def get_cloudwatch_messages(log_group_name, stream_name, formatter=None, next_token=None):
    messages = []
    response = None

    try:
        response = cloudwatch.get_log_events(log_group_name, stream_name, next_token=next_token)
    except MaxRetriesError as e:
        LOG.debug('Received max retries')
        io.echo(e.message())
        time.sleep(1)

    if response and response.get('events'):
        for event in response.get('events'):
            message = event.get('message').encode('utf8', 'replace')

            if formatter:
                timestamp = event.get('timestamp')
                formatted_message = formatter.format(stream_name, message, timestamp)
            else:
                formatted_message = '[{}] {}'.format(stream_name, message)

            messages.append(formatted_message)
        # Set the next token
        next_token = response.get('nextForwardToken')

    return messages, next_token


def _get_platform_builder_group_name(platform_name):
    return "/aws/elasticbeanstalk/platform/%s" % platform_name


def stream_platform_logs(platform_name, version, streamer=None, sleep_time=4, log_name=None, formatter=None):
    log_group_name = _get_platform_builder_group_name(platform_name)

    if streamer is None:
        streamer = io.get_event_streamer()

    if log_name is not None:
        streamer.prompt = ' -- Streaming logs for %s -- (Ctrl+C to exit)' % log_name

    stream_single_stream(log_group_name, version, streamer, sleep_time, formatter)


def paginate_cloudwatch_logs(platform_name, version, formatter=None):
    log_group_name = _get_platform_builder_group_name(platform_name)
    next_token = None

    while True:
        try:
            messages, next_token = get_cloudwatch_messages(log_group_name, version, formatter, next_token)
            if messages:
                io.echo_with_pager("\n".join(messages))
            else:
                break
        except ServiceError as e:
            # Something went wrong getting the stream
            # It probably doesnt exist anymore.
            io.log_error(e)
            break
        except Exception as e:
            # We want to swallow all exceptions or else they will be
            # printed as a stack trace to the Console
            # Exceptions are typically connections reset and
            # Various things
            LOG.debug('Exception raised: ' + str(e))
            # Loop will cause a retry


def retrieve_cloudwatch_logs(log_group, info_type, do_zip=False, instance_id=None):
    # Get the log streams, a.k.a. the instance ids in the log group
    """
        Retrieves cloudwatch logs for every stream under the log group unless the instance_id is specified. If tail
         logs is enabled we will only get the last 100 lines and return the result to a pager for the user to use. If
         bundle info type is chosen we will get all of the logs and save them to a dir under .elasticbeanstalk/logs/
        and if zip is enabled we will zip those logs for the user.
        :param log_group: cloudwatch log group
        :param info_type: can be 'tail' or 'bundle'
        :param do_zip: boolean to determine if we should zip the logs we retrieve
        :param instance_id: if we only want a single instance we can specify it here
    """
    log_streams = cloudwatch.describe_log_streams(log_group, log_stream_name_prefix=instance_id)
    instance_ids = []

    if len(log_streams['logStreams']) == 0:
        io.log_error(strings['logs.nostreams'])

    for stream in log_streams['logStreams']:
        instance_ids.append(stream['logStreamName'])

    # This is analogous to getting the full logs
    if info_type == 'bundle':
        # Create directory to store logs
        logs_folder_name = datetime.now().strftime("%y%m%d_%H%M%S")
        logs_location = fileoperations.get_logs_location(logs_folder_name)
        os.makedirs(logs_location)
        # Get logs for each instance
        for instance_id in instance_ids:
            full_logs = get_cloudwatch_stream_logs(log_group, instance_id)
            full_filepath = '{0}/{1}.log'.format(logs_location, instance_id)
            log_file = open(full_filepath, 'w+')
            log_file.write(full_logs)
            log_file.close()
            fileoperations.set_user_only_permissions(full_filepath)

        if do_zip:
            fileoperations.zip_up_folder(logs_location, logs_location + '.zip')
            fileoperations.delete_directory(logs_location)

            logs_location += '.zip'
            fileoperations.set_user_only_permissions(logs_location)
            io.echo(strings['logs.location'].replace('{location}', logs_location))
        else:
            io.echo(strings['logs.location'].replace('{location}', logs_location))
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
                # Oh well.. we tried.
                ## Probably on windows, or logs/latest is not a symlink
                pass

    else:
        # print logs
        all_logs = ""
        for instance_id in instance_ids:
            tail_logs = get_cloudwatch_stream_logs(log_group, instance_id, num_log_events=TAIL_LOG_SIZE)
            all_logs += '\n\n============= {0} - {1} ==============\n\n'.format(str(instance_id), get_log_name(log_group))
            all_logs += tail_logs
        io.echo_with_pager(all_logs)


def get_cloudwatch_stream_logs(log_group_name, stream_name, num_log_events=None):
    """
        Will get logs events from cloudwatch and append them to a single string to output with each line prefixed with
         the stream name.
        :param log_group_name: cloudwatch log group
        :param stream_name: cloudwatch stream name
        :param num_log_events: number of log events to retrieve; default is cloudwatch's max: 10k or 1MB of messages
        :return: single string will all log events concatenated together
    """
    full_log = ''
    try:
        response = cloudwatch.get_log_events(log_group_name, stream_name, limit=num_log_events)

        if response and response.get('events'):
            for event in response.get('events'):
                message = event.get('message')

                full_log += '[{}] {}\n'.format(stream_name, message)

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
    return full_log


def log_streaming_enabled(app_name, env_name):
    """
        Checks if log streaming is enabled for the given environment
        :param app_name: application name
        :param env_name: environment name
        :return: boolean if the given environment has log stremaing enabled
    """
    config_settings = elasticbeanstalk.describe_configuration_settings(app_name, env_name)
    stream_enabled = elasticbeanstalk.get_specific_configuration(config_settings, namespaces.CLOUDWATCH_LOGS,
                                                                 option_names.STREAM_LOGS)
    if stream_enabled is not None and stream_enabled == 'true':
        return True
    return False


def disable_cloudwatch_logs(env_name):
    """
        Disables cloudwatch log streaming for the given environment
        :param env_name: environment name
    """
    # Add option settings needed for log streaming
    option_settings = [
        elasticbeanstalk.create_option_setting(
            namespaces.CLOUDWATCH_LOGS,
            option_names.STREAM_LOGS,
            'false'),
    ]
    io.echo(strings['cloudwatch-logs.disable'])
    commonops.update_environment(env_name, changes=option_settings, nohang=False)


def enable_cloudwatch_logs(env_name):
    # Add option settings needed for log streaming
    """
        Enables cloudwatch log streaming for the given environment
        :param env_name: environment name
    """
    option_settings = [
        elasticbeanstalk.create_option_setting(
            namespaces.CLOUDWATCH_LOGS,
            option_names.STREAM_LOGS,
            'true'
        ),
    ]
    io.echo(strings['cloudwatch-logs.enable'])
    # echo link to cloudwatch console, BJS console link is different
    region = commonops.get_default_region()
    if region == 'cn-north-1':
        cw_link_regionalized = strings['cloudwatch-logs.bjslink']
    else:
        cw_link_regionalized = strings['cloudwatch-logs.link']
    io.echo(cw_link_regionalized.replace('{region}', region).replace('{env_name}', env_name))

    commonops.update_environment(env_name, changes=option_settings, nohang=False)


# TODO: Maybe not foce all log groups to be beanstalk specific
def beanstalk_log_group_builder(env_name, filepath=DEFAULT_LOG_STREAMING_PATH):
    """
        The log builder will take an optional filepath and attempt to build the log group specifically for groups created
         by the Elastic Beanstalk service.
        :param env_name: current environment being used
        :param filepath: path that is apart of the log_stream
        :return: the full log group for a beanstalk log group
    """
    if filepath is None:
        filepath = DEFAULT_LOG_STREAMING_PATH
    elif filepath.startswith('{0}/{1}'.format(BEANSTALK_LOG_PREFIX, env_name)):
        return filepath
    return '{0}/{1}/{2}'.format(BEANSTALK_LOG_PREFIX, env_name, filepath)


def get_log_name(log_group):
    """
        This will parse the log group to get the filename of the log. Benastalk creates log groups with the the filepath of
         the log, example: '/aws/elasticbeanstalk/env-name/var/log/eb-activity.log'.
        :param log_group: full or partial log group
        :return: the last string on the path, i.e. the filename
    """
    return log_group.split('/')[-1]
