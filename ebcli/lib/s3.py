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

from __future__ import division
import os
from io import BytesIO
import math
import threading
from cement.utils.misc import minimal_logger

from . import aws
from ..objects.exceptions import NotFoundError, FileTooLargeError
from ..core import io
from .utils import static_var


LOG = minimal_logger(__name__)
CHUNK_SIZE = 5252880  # Minimum chunk size allowed by S3
THREAD_COUNT = 8  # Number of threads to use for multithreaded mode


def _make_api_call(operation_name, **operation_options):
    return aws.make_api_call('s3', operation_name, **operation_options)


def upload_file(bucket, key, file_path, region=None):
    with open(file_path, 'rb') as fp:
        return _make_api_call('put-object',
                              bucket=bucket,
                              key=key,
                              body=fp,
                              region=region)


def get_object_info(bucket, object_key, region=None):
    result = _make_api_call('list-objects',
                   bucket=bucket,
                   prefix=object_key,
                   region=region)

    if 'Contents' not in result or len(result['Contents']) < 1:
        raise NotFoundError('Object not found.')

    objects = result['Contents']
    if len(objects) == 1:
        return objects[0]
    else:
        # There is more than one result, search for correct one
        object_key = next((o for o in objects if o['Key'] == object_key), None)
        if object_key is None:
            raise NotFoundError('Object not found.')
        else:
            return object_key


def get_object(bucket, key, region=None):
    result = _make_api_call('get-object',
                            bucket=bucket,
                            key=key,
                            region=region)
    return result['Body'].read()


def upload_application_version(bucket, key, file_path, region=None):
    size = os.path.getsize(file_path)
    if size > 536870912:
        raise FileTooLargeError('Application version cannot be any '
                                'larger than 512MB')
    if size < 7340032:
        result = simple_upload(bucket, key, file_path, region=region)

    else:
        result = multithreaded_upload(bucket, key, file_path, region=region)
    return result


def simple_upload(bucket, key, file_path, region=None):
    io.echo('Uploading', key, 'to S3. This may take a while.')
    result = upload_file(bucket, key, file_path, region=region)
    io.echo('Upload Complete.')
    return result


def multithreaded_upload(bucket, key, file_path, region=None):
    """
    Upload a file in multiple parts using multiple threads.
    Takes advantage of S3's multipart upload.
    :param bucket: S3 bucket name
    :param key: keyname of file to be uploaded
    :param file_path: full path location of file to be uploaded
    :param region: region to use for S3
    :return: Result dictionary
    """

    size = os.path.getsize(file_path)
    total_parts = math.ceil(size / CHUNK_SIZE)  # Number of parts needed

    # Begin multi-part upload
    response = _make_api_call('create-multipart-upload',
                   bucket=bucket,
                   key=key,
                   region=region)
    upload_id = response['UploadId']

    # Upload parts
    try:
        etaglist = []  # list for part id's (etags)
        with open(file_path, 'r') as f:
            # Create threads to handle parts of upload
            lock = threading.Lock()
            jobs = []
            for i in range(THREAD_COUNT):
                p = threading.Thread(
                    target=_upload_chunk,
                    args=(f, lock, etaglist, total_parts,
                          bucket, key, upload_id),
                    )
                p.daemon = True
                jobs.append(p)
                p.start()

            _wait_for_threads(jobs)

        # S3 requires the etag list to be sorted
        etaglist = sorted(etaglist, key=lambda k: k['PartNumber'])

        result = _make_api_call('complete-multipart-upload',
                              bucket=bucket,
                              key=key,
                              upload_id=upload_id,
                              multipart_upload=dict(Parts=etaglist))

        return result

    except (Exception, KeyboardInterrupt) as e:
        _make_api_call('abort-multipart-upload',
                       bucket=bucket,
                       key=key,
                       upload_id=upload_id)
        raise


def _wait_for_threads(jobs):
    alive = True
    while alive:
        alive = False
        for j in jobs:
            """
            We want to wait forever for the thread to finish.
            j.join() however is a halting call. We need to pass in a
            time to j.join() so it is non halting. This way a user can use
            CTRL+C to terminate the command. 2**31 is the largest number we
            can pass into j.join()
            """
            j.join(2**31)
            if j.isAlive():
                alive = True


def _upload_chunk(f, lock, etaglist, total_parts, bucket, key, upload_id):
    while True:
        data, part = _read_next_section_from_file(f, lock)
        if data == '':
            return
        b = BytesIO()
        b.write(data)
        b.seek(0)
        response = _make_api_call('upload-part',
                                  bucket=bucket,
                                  key=key,
                                  upload_id=upload_id,
                                  body=b,
                                  part_number=part)

        etaglist.append({'PartNumber': part, 'ETag': response['ETag']})

        progress = (1/total_parts) * len(etaglist)
        io.update_upload_progress(progress)


@static_var('part_num', 0)
def _read_next_section_from_file(f, lock):
    with lock:
        data = f.read(CHUNK_SIZE)
        _read_next_section_from_file.part_num += 1
        return data, _read_next_section_from_file.part_num