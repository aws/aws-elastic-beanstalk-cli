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
import six
from cement.utils.misc import minimal_logger

from ebcli import __version__
from ebcli.objects.exceptions import ServiceError, CredentialsError
from ebcli.core import fileoperations

LOG = minimal_logger(__name__)

_api_sessions = {}


def set_session_creds(id, key):
    global _api_sessions
    for k, service in six.iteritems(_api_sessions):
        service.session.set_credentials(id, key)



def _set_user_agent_for_session(session):
    session.user_agent_name = 'eb-cli'
    session.user_agent_version = __version__


def _get_service(service_name):
    global _api_sessions
    if service_name in _api_sessions:
        return _api_sessions[service_name]

    LOG.debug('Creating new Botocore Session')
    session = botocore.session.get_session()
    _set_user_agent_for_session(session)

    service = session.get_service(service_name)
    LOG.debug('Successfully created session for ' + service_name)

    _api_sessions[service_name] = service
    return service


def make_api_call(service_name, operation_name, region=None,
                  **operation_options):
    service = _get_service(service_name)

    operation = service.get_operation(operation_name)
    if not region:
        region = fileoperations.get_default_region()
    endpoint = service.get_endpoint(region)

    try:
        LOG.debug('Making api call: (' +
                  service_name + ', ' + operation_name +
                  ') to region: ' + region)
        http_response, response_data = operation.call(endpoint,
                                                      **operation_options)
        status = http_response.status_code
        LOG.debug('API call finished, status = ' + str(status))
        if response_data:
            LOG.debug('Response: ' + str(response_data))

        if status is not 200:
            if status == 400:
                # Convert to correct 400 error
                raise _get_400_error(response_data)
            elif status == 403:
                LOG.debug('Received a 403')
                raise CredentialsError('Operation Denied. Are your '
                                       'credentials correct?')
            else:
                LOG.error('API Call unsuccessful. '
                          'Status code returned ' + str(status))
            return None
    except botocore.exceptions.NoCredentialsError as e:
        LOG.error('No credentials found')
        raise CredentialsError('Operation Denied. You appear to have no'
                               ' credentials')
    except botocore.exceptions.BotoCoreError as e:
        LOG.error('Botocore Error')
        raise e

    except IOError as error:
        LOG.error('Error while contacting Elastic Beanstalk Service')
        LOG.debug('error: ' + str(error.message))
        raise ServiceError(error.message)

    return response_data


def _get_400_error(response_data):
    code = response_data['Errors'][0]['Code']
    message = response_data['Errors'][0]['Message']
    if code == 'InvalidParameterValue':
        return InvalidParameterValueError(message)
    elif code == 'InvalidQueryParameter':
        return InvalidQueryParameterError(message)
    elif code == 'Throttling':
        return ThrottlingError(message)
    else:
        # Not tracking this error
        return ServiceError(message)


class InvalidParameterValueError(Exception):
    pass


class InvalidQueryParameterError(Exception):
    pass


class ThrottlingError(Exception):
    pass


