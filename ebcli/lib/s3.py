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
from ebcli.lib import aws
from cement.utils.misc import minimal_logger

LOG = minimal_logger(__name__)


def _make_api_call(operation_name, **operation_options):
    return aws.make_api_call('s3', operation_name, **operation_options)


def upload_application_version(bucket, app_name, file_name, file_path):
    with open(file_path, 'rb') as fp:
        return _make_api_call('PutObject',
                              bucket=bucket,
                              key=app_name + '/' + file_name,
                              body=fp)
