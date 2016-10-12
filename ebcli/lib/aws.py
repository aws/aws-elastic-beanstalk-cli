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

import os
import random
import time
import warnings

import botocore
import botocore.exceptions
import botocore.session
from botocore.config import Config
from botocore.loaders import Loader
from cement.utils.misc import minimal_logger

from ebcli import __version__
from .botopatch import apply_patches
from .utils import static_var
from ..core import fileoperations
from ..objects.exceptions import ServiceError, NotAuthorizedError, \
    CredentialsError, NoRegionError,  ValidationError, \
    InvalidProfileError, ConnectionError, AlreadyExistsError, NotFoundError, \
    NotAuthorizedInRegionError
from ..resources.strings import strings

LOG = minimal_logger(__name__)

BOTOCORE_DATA_FOLDER_NAME = 'botocoredata'

_api_clients = {}
_profile = None
_profile_env_var = 'AWS_EB_PROFILE'
_id = None
_key = None
_region_name = None
_verify_ssl = True
_endpoint_url = None
_debug = False

apply_patches()


def _flush():
    # Should be used for resetting tests only
    global _api_clients, _profile, _id, _key, _region_name, _verify_ssl
    _api_clients = {}
    _get_botocore_session.botocore_session = None
    _profile = None
    _id = None
    _key = None
    _region_name = None
    _verify_ssl = True


def set_session_creds(id, key):
    global _api_clients, _id, _key
    _id = id
    _key = key

    # invalidate all old clients
    _api_clients = {}


def set_profile(profile):
    global _profile, _api_clients
    _profile = profile

    # Invalidate session and old clients
    _get_botocore_session.botocore_session = None
    _api_clients = {}


def set_region(region_name):
    global _region_name
    _region_name = region_name

    # Invalidate session and old clients
    _get_botocore_session.botocore_session = None
    _api_clients = {}


def set_endpoint_url(endpoint_url):
    global _endpoint_url
    _endpoint_url = endpoint_url


def no_verify_ssl():
    global _verify_ssl
    _verify_ssl = False


def set_profile_override(profile):
    global _profile_env_var
    set_profile(profile)
    _profile_env_var = None


def set_debug():
    global _debug
    _debug = True


def _set_user_agent_for_session(session):
    session.user_agent_name = 'eb-cli'
    session.user_agent_version = __version__

def _get_data_loader():
    # Creates a botocore data loader that loads custom data files
    # FIRST, creating a precedence for custom files.
    data_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               BOTOCORE_DATA_FOLDER_NAME)

    return Loader(extra_search_paths=[data_folder, Loader.BUILTIN_DATA_PATH],
                  include_default_search_paths=False)

def _get_client(service_name):
    aws_access_key_id = _id
    aws_secret_key = _key
    if service_name in _api_clients:
        return _api_clients[service_name]

    session = _get_botocore_session()
    if service_name == 'elasticbeanstalk':
        endpoint_url = _endpoint_url
    else:
        endpoint_url = None
    try:
        LOG.debug('Creating new Botocore Client for ' + str(service_name))
        client = session.create_client(service_name,
                                       endpoint_url=endpoint_url,
                                       # region_name=_region_name,
                                       aws_access_key_id=aws_access_key_id,
                                       aws_secret_access_key=aws_secret_key,
                                       verify=_verify_ssl,
                                       config=Config(signature_version='s3v4'))

    except botocore.exceptions.ProfileNotFound as e:
        raise InvalidProfileError(e)
    LOG.debug('Successfully created session for ' + service_name)

    _api_clients[service_name] = client
    return client


@static_var('botocore_session', None)
def _get_botocore_session():
    if _get_botocore_session.botocore_session is None:
        LOG.debug('Creating new Botocore Session')
        LOG.debug('Botocore version: {0}'.format(botocore.__version__))
        session = botocore.session.get_session({
            'profile': (None, _profile_env_var, _profile, None),
        })
        session.set_config_variable('region', _region_name)
        session.register_component('data_loader', _get_data_loader())
        _set_user_agent_for_session(session)
        _get_botocore_session.botocore_session = session
        if _debug:
            session.set_debug_logger()

    return _get_botocore_session.botocore_session


def get_region_name():
    return _region_name


def get_credentials():
    access_key, secret_key = fileoperations.read_credentials_from_aws_config()
    return botocore.credentials.Credentials(
        access_key=access_key,
        secret_key=secret_key,
    )


def make_api_call(service_name, operation_name, **operation_options):
    try:
        client = _get_client(service_name)
    except botocore.exceptions.UnknownEndpointError as e:
        raise NoRegionError(e)
    except botocore.exceptions.PartialCredentialsError as e:
        LOG.debug('Credentials incomplete')
        raise CredentialsError('Your credentials are not complete. Error: {0}'
                               .format(e))
    except botocore.exceptions.NoRegionError:
        raise NoRegionError()

    if not _verify_ssl:
        warnings.filterwarnings("ignore")

    operation = getattr(client, operation_name)

    region = _region_name
    if not region:
        region = 'default'

    MAX_ATTEMPTS = 10
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
            response_data = operation(**operation_options)
            status = response_data['ResponseMetadata']['HTTPStatusCode']
            LOG.debug('API call finished, status = ' + str(status))
            if response_data:
                LOG.debug('Response: ' + str(response_data))

            return response_data

        except botocore.exceptions.ClientError as e:
            response_data = e.response
            LOG.debug('Response: ' + str(response_data))
            status = response_data['ResponseMetadata']['HTTPStatusCode']
            LOG.debug('API call finished, status = ' + str(status))
            try:
                message = str(response_data['Error']['Message'])
            except KeyError:
                message = ""
            if status == 400:
                # Convert to correct 400 error
                error = _get_400_error(response_data, message)
                if isinstance(error, ThrottlingError):
                    LOG.debug('Received throttling error')
                    if attempt > MAX_ATTEMPTS:
                        raise MaxRetriesError('Max retries exceeded for '
                                              'throttling error')
                else:
                    raise error
            elif status == 403:
                LOG.debug('Received a 403')
                if not message:
                    message = 'Are your permissions correct?'
                if _region_name == 'cn-north-1':
                    raise NotAuthorizedInRegionError('Operation Denied. ' + message +
                                                     '\n' +
                                                     strings['region.china.credentials'])
                else:
                    raise NotAuthorizedError('Operation Denied. ' + message)
            elif status == 404:
                LOG.debug('Received a 404')
                raise NotFoundError(message)
            elif status == 409:
                LOG.debug('Received a 409')
                raise AlreadyExistsError(message)
            elif status in (500, 503, 504):
                LOG.debug('Received 5XX error')
                if attempt > MAX_ATTEMPTS:
                    raise MaxRetriesError('Max retries exceeded for '
                                          'service error (5XX)')
            else:
                raise ServiceError('API Call unsuccessful. '
                                   'Status code returned ' + str(status))
        except botocore.exceptions.NoCredentialsError:
            LOG.debug('No credentials found')
            raise CredentialsError('Operation Denied. You appear to have no'
                                   ' credentials')
        except botocore.exceptions.PartialCredentialsError as e:
            LOG.debug('Credentials incomplete')
            raise CredentialsError(str(e))

        except (botocore.exceptions.ValidationError,
                botocore.exceptions.ParamValidationError) as e:
            raise ValidationError(str(e))

        except botocore.exceptions.BotoCoreError as e:
            LOG.error('Botocore Error')
            raise

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


def _get_400_error(response_data, message):
    code = response_data['Error']['Code']
    LOG.debug('Received a 400 Error')
    if code == 'InvalidParameterValue':
        return InvalidParameterValueError(message)
    elif code == 'InvalidQueryParameter':
        return InvalidQueryParameterError(message)
    elif code.startswith('Throttling'):
        return ThrottlingError(message)
    elif code.startswith('ResourceNotFound'):
        return NotFoundError(message)
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


