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


from cement.utils.misc import minimal_logger

from . import aws
from ..objects.exceptions import NotFoundError

LOG = minimal_logger(__name__)


def _make_api_call(operation_name, **operation_options):
    return aws.make_api_call('s3', operation_name, **operation_options)


def upload_application_version(bucket, key, file_path,
                               region=None):
    with open(file_path, 'rb') as fp:
        return _make_api_call('put-object',
                              bucket=bucket,
                              key=key,
                              body=fp,
                              region=region)


def get_object_info(bucket, object, region=None):
    result = _make_api_call('list-objects',
                   bucket=bucket,
                   prefix=object,
                   region=region)

    if 'Contents' not in result or len(result['Contents']) < 1:
        raise NotFoundError('Object not found.')

    objects = result['Contents']
    if len(objects) == 1:
        return objects[0]
    else:
        # There is more than one result, search for correct one
        object = next((o for o in objects if o['Key'] == object), None)
        if object is None:
            raise NotFoundError('Object not found.')
        else:
            return object

