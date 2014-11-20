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

import time
import random

import botocore_eb.session
import botocore_eb.exceptions
import six
from cement.utils.misc import minimal_logger

from ebcli import __version__
from ..objects.exceptions import ServiceError, NotAuthorizedError, \
    InvalidSyntaxError, CredentialsError, NoRegionError, \
    InvalidProfileError, ConnectionError, AlreadyExistsError

LOG = minimal_logger(__name__)

_api_sessions = {}
_profile = None
_profile_env_var = 'AWS_EB_PROFILE'
_id = None
_key = None


def set_session_creds(id, key):
    global _api_sessions, _id, _key
    _id = id
    _key = key
    for k, service in six.iteritems(_api_sessions):
        service.session.set_credentials(_id, _key)


def set_profile(profile):
    global _profile
    _profile = profile


def set_profile_override(profile):
    global _profile
    global _profile_env_var
    _profile = profile
    _profile_env_var = None


def _set_user_agent_for_session(session):
    session.user_agent_name = 'eb-cli'
    session.user_agent_version = __version__


def _get_service(service_name):
    global _api_sessions
    if service_name in _api_sessions:
        return _api_sessions[service_name]

    LOG.debug('Creating new Botocore Session')
    session = botocore_eb.session.Session(session_vars={
        'profile': (None, _profile_env_var, _profile)})
    _set_user_agent_for_session(session)

    try:
        service = session.get_service(service_name)
    except botocore_eb.exceptions.ProfileNotFound as e:
        raise InvalidProfileError(e)
    LOG.debug('Successfully created session for ' + service_name)

    if _id and _key:
        service.session.set_credentials(_id, _key)
    _api_sessions[service_name] = service
    return service


def get_default_region():
    service = _get_service('elasticbeanstalk')
    try:
        endpoint = service.get_endpoint()
        return endpoint.region_name
    except botocore_eb.exceptions.UnknownEndpointError as e:
        raise NoRegionError(e)
    except:
        return None


def make_api_call(service_name, operation_name, region=None, endpoint_url=None,
                  **operation_options):
    service = _get_service(service_name)

    operation = service.get_operation(operation_name)
    if endpoint_url:
        endpoint = service.get_endpoint(region_name=region,
                                        endpoint_url=endpoint_url)
    else:
        try:
            if not region:
                endpoint = service.get_endpoint()
                region = 'default'
            else:
                endpoint = service.get_endpoint(region)
        except botocore_eb.exceptions.UnknownEndpointError as e:
            raise NoRegionError(e)
        except botocore_eb.exceptions.PartialCredentialsError:
            LOG.debug('Credentials incomplete')
            raise CredentialsError('Your credentials are not valid')


    MAX_ATTEMPTS = 15
    attempt = 0
    while True:
        attempt += 1
        if attempt > 1:
            LOG.debug('Retrying -- attempt #' + str(attempt))
        delay = _get_delay(attempt)
        time.sleep(delay)
        try:
            LOG.debug('Making api call: (' +
                      service_name + ', ' + operation_name +
                      ') to region: ' + region + ' with args:' + str(operation_options))
            http_response, response_data = operation.call(endpoint,
                                                          **operation_options)
            status = http_response.status_code
            LOG.debug('API call finished, status = ' + str(status))
            if response_data:
                LOG.debug('Response: ' + str(response_data))

            if status == 200:
                return response_data

            if status is not 200:
                if status == 400:
                    # Convert to correct 400 error
                    error = _get_400_error(response_data)
                    if isinstance(error, ThrottlingError):
                        LOG.debug('Received throttling error')
                        if attempt > MAX_ATTEMPTS:
                            raise MaxRetriesError('Max retries exceeded for '
                                                  'throttling error')
                    else:
                        raise error
                elif status == 403:
                    LOG.debug('Received a 403')
                    raise NotAuthorizedError('Operation Denied. Are your '
                                           'permissions correct?')
                elif status == 409:
                    LOG.debug('Received a 409')
                    raise AlreadyExistsError(response_data['Error']['Message'])
                elif status in (500, 503, 504):
                    LOG.debug('Received 5XX error')
                    if attempt > MAX_ATTEMPTS:
                        raise MaxRetriesError('Max retries exceeded for '
                                              'service error (5XX)')
                else:
                    raise ServiceError('API Call unsuccessful. '
                              'Status code returned ' + str(status))
        except botocore_eb.exceptions.NoCredentialsError as e:
            LOG.debug('No credentials found')
            raise CredentialsError('Operation Denied. You appear to have no'
                                   ' credentials')
        except botocore_eb.exceptions.PartialCredentialsError as e:
            LOG.debug('Credentials incomplete')
            raise CredentialsError(str(e))

        except botocore_eb.exceptions.ValidationError as e:
            raise InvalidSyntaxError(e)

        except botocore_eb.exceptions.BotoCoreError as e:
            LOG.error('Botocore Error')
            raise e

        except IOError as error:
            if hasattr(error.args[0], 'reason') and str(error.args[0].reason) == \
                    '[Errno -2] Name or service not known':
                raise ConnectionError()

            LOG.error('Error while contacting Elastic Beanstalk Service')
            LOG.debug('error:' + str(error))
            raise ServiceError(error)


def _get_delay(attempt_number):
    if attempt_number == 1:
        return 0
    # Exponential backoff
    rand_int = random.randrange(0, 2**attempt_number)
    delay = rand_int * 0.05  # delay time is 50 ms
    LOG.debug('Sleeping for ' + str(delay) + ' seconds.')
    return delay


def _get_400_error(response_data):
    code = response_data['Error']['Code']
    message = response_data['Error']['Message']
    if code == 'InvalidParameterValue':
        return InvalidParameterValueError(message)
    elif code == 'InvalidQueryParameter':
        return InvalidQueryParameterError(message)
    elif code == 'Throttling':
        return ThrottlingError(message)
    else:
        # Not tracking this error
        return ServiceError(message, code=code)


class InvalidParameterValueError(ServiceError):
    pass


class InvalidQueryParameterError(ServiceError):
    pass


class ThrottlingError(ServiceError):
    pass


class MaxRetriesError(ServiceError):
    pass


