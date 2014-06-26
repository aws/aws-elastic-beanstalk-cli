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

import dateutil
import datetime

import botocore.session

from ebcli.core.ebcore import app


def get_beanstalk_session():
    app.log.info('Creating new Botocore session')
    session = botocore.session.get_session()
    app.log.debug('Successfully created session')

    beanstalk = session.get_service('elasticbeanstalk')
    return beanstalk


def _make_api_call(operation_name, **operation_options):
    beanstalk = get_beanstalk_session()
    operation = beanstalk.get_operation(operation_name)
    endpoint = beanstalk.get_endpoint(app.args.endpoint)

    try:
        app.log.debug('Making api call')
        http_response, response_data = operation.call(endpoint,
                                                      **operation_options)
        status = http_response.status_code
        app.log.debug('API call finished, response =', status)

        if http_response.status_code is not 200:
            app.log.error('API Call unsuccessful. '
                          'Status code returned', status)
            if response_data:
                app.log.debug('Response:', response_data)
            return None

    except (Exception, IOError) as error:
        app.log.error('Error while contacting Elastic Beanstalk Service')
        app.log.debug(error)
        return None

    return response_data


def describe_applications():
    app.log.info('Inside describe_applications api wrapper')
    return _make_api_call('describe-applications')


def create_application(app_name, descrip):
    app.log.info('Inside create_application api wrapper')
    return _make_api_call('create-application',
                          application_name=app_name,
                          description=descrip)


def create_application_version(app_name, vers_label, descrip):
    app.log.info('Inside create_application_version api wrapper')
    return _make_api_call('create-application-version',
                          application_name=app_name,
                          version_label=vers_label,
                          description=descrip)


def create_environment(app_name, env_name, descrip, solution_stck, tier0):
    app.log.info('Inside create_environment api wrapper')
    return _make_api_call('create-environment',
                          application_name=app_name,
                          environment_name=env_name,
                          description=descrip,
                          solution_stack=solution_stck,
                          tier=tier0)


def get_available_solution_stacks():
    return _make_api_call('list-available-solution-stacks')


def get_environment_details(app_name):
    return _make_api_call('describe-environments',
                          application_name=app_name)


def get_new_events(app_name, last_event_time=''):
    if last_event_time is not '':
        time = dateutil.parser.parse(last_event_time)
        new_time = time + datetime.timedelta(0, 0, 1000)
        timestamp = new_time.isoformat()[0:-9] + 'Z'
    else:
        timestamp = ''
    return _make_api_call('describe-events',
                          application_name=app_name,
                          start_time=timestamp)








