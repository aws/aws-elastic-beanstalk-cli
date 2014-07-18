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

import botocore.session
import botocore.exceptions
from cement.utils.misc import minimal_logger

from ebcli import __version__
from ebcli.objects.exceptions import ServiceError
LOG = minimal_logger(__name__)


def _set_user_agent_for_session(session):
    session.user_agent_name = 'eb-cli'
    session.user_agent_version = __version__


def _get_session(service_name):
    LOG.debug('Creating new Botocore Session')
    session = botocore.session.get_session()
    _set_user_agent_for_session(session)

    service = session.get_service(service_name)
    LOG.debug('Successfully created session for ' + service_name)

    return service


def make_api_call(service_name, operation_name, **operation_options):
    global app
    service = _get_session(service_name)
    operation = service.get_operation(operation_name)
    endpoint = service.get_endpoint()

    try:
        LOG.debug('Making api call')
        http_response, response_data = operation.call(endpoint,
                                                      **operation_options)
        status = http_response.status_code
        LOG.debug('API call finished, response =', status)

        if status is not 200:
            if status is 403:
                LOG.error('Operation Denied. Are your '
                          'credentials correct?')
            else:
                LOG.error('API Call unsuccessful. '
                                 'Status code returned' + status)
            if response_data:
                LOG.debug('Response:', response_data)
            return None
    except botocore.exceptions.NoCredentialsError as e:
        LOG.error('No credentials file found')
        raise e

    except (Exception, IOError) as error:
        LOG.error('Error while contacting Elastic Beanstalk Service')
        LOG.debug('error: ' + error.message)
        raise ServiceError

    return response_data
