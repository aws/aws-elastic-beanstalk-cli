# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
from copy import deepcopy
import datetime
import os
import shutil
import threading

from dateutil import tz
import mock
import unittest

from ebcli.core import fileoperations
from ebcli.lib import s3

from .. import mock_responses


class TestS3(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.getcwd()
        if os.path.exists('testDir'):
            shutil.rmtree('testDir')
        os.mkdir('testDir')
        os.chdir('testDir')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    def test_upload_file(
            self,
            make_api_call_mock
    ):
        with open('s3_object.py', 'w') as s3_object:
            s3_object.write("print('Hello, world!')")

        mock_open = mock.mock_open()
        with mock.patch('ebcli.lib.s3.open', mock_open, create=True):
            s3.upload_file('bucket', 'key', 's3_object.py')

        make_api_call_mock.assert_called_once_with(
            's3',
            'put_object',
            Body=mock_open(),
            Bucket='bucket',
            Key='key'
        )

    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    def test_get_object_info__list_objects_called__multiple_objects_returned__required_object_found(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.LIST_OBJECTS_RESPONSE

        self.assertEqual(
            {
                'Key': 'my-application/app-171205_194441.zip',
                'LastModified': datetime.datetime(2017, 12, 5, 19, 44, 42, tzinfo=tz.tzutc()),
                'ETag': '"4ee0f32888afdgsdfg34523552345f8494f7"',
                'Size': 10724,
                'StorageClass': 'STANDARD',
                'Owner': {
                    'ID': '15a1b0d3e1e432234123412341423144d71093667b756f3435c1dcad2247c7124'
                }
            },
            s3.get_object_info('bucket', 'my-application/app-171205_194441.zip')
        )

        make_api_call_mock.assert_called_once_with(
            's3',
            'list_objects',
            Bucket='bucket',
            Prefix='my-application/app-171205_194441.zip'
        )

    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    def test_get_object_info__list_objects_called__exactly_one_object(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = {
            'Contents': [
                {
                    'Key': 'my-application/app-171205_194441.zip',
                    'LastModified': datetime.datetime(2017, 12, 5, 19, 44, 42, tzinfo=tz.tzutc()),
                    'ETag': '"4ee0f32888afdgsdfg34523552345f8494f7"',
                    'Size': 10724,
                    'StorageClass': 'STANDARD',
                    'Owner': {
                        'ID': '15a1b0d3e1e432234123412341423144d71093667b756f3435c1dcad2247c7124'
                    }
                }
            ]
        }

        self.assertEqual(
            {
                'Key': 'my-application/app-171205_194441.zip',
                'LastModified': datetime.datetime(2017, 12, 5, 19, 44, 42, tzinfo=tz.tzutc()),
                'ETag': '"4ee0f32888afdgsdfg34523552345f8494f7"',
                'Size': 10724,
                'StorageClass': 'STANDARD',
                'Owner': {
                    'ID': '15a1b0d3e1e432234123412341423144d71093667b756f3435c1dcad2247c7124'
                }
            },
            s3.get_object_info('bucket', 'my-application/app-171205_194441.zip')
        )
        make_api_call_mock.assert_called_once_with(
            's3',
            'list_objects',
            Bucket='bucket',
            Prefix='my-application/app-171205_194441.zip'
        )

    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    def test_get_object_info__list_objects_called__exactly_one_object(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.LIST_OBJECTS_RESPONSE

        with self.assertRaises(s3.NotFoundError) as context_manager:
            s3.get_object_info('bucket', 'absent-application/app-171205_194441.zip')

        self.assertEqual('Object not found.', str(context_manager.exception))
        make_api_call_mock.assert_called_once_with(
            's3',
            'list_objects',
            Bucket='bucket',
            Prefix='absent-application/app-171205_194441.zip'
        )

    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    def test_get_object(
            self,
            make_api_call_mock
    ):
        body_mock = mock.MagicMock()
        body_mock.read = mock.MagicMock(return_value='body')
        result = {
            'Body': body_mock
        }
        make_api_call_mock.return_value = result

        self.assertEqual(
            'body',
            s3.get_object('bucket', 'key')
        )
        make_api_call_mock.assert_called_once_with(
            's3',
            'get_object',
            Bucket='bucket',
            Key='key'
        )

    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    def test_delete_object(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DELETE_OBJECTS_RESPONSE

        self.assertEqual(
            {
                'Deleted': [
                    {
                        'DeleteMarker': True,
                        'DeleteMarkerVersionId': 'marker_1',
                        'Key': 'key_1',
                        'VersionId': 'version_id_1'
                    },
                    {
                        'DeleteMarker': True,
                        'DeleteMarkerVersionId': 'marker_2',
                        'Key': 'key_2',
                        'VersionId': 'version_id_2'
                    }
                ]
            },
            s3.delete_objects('bucket', ['key_1', 'key_2'])
        )
        make_api_call_mock.assert_called_once_with(
            's3',
            'delete_objects',
            Bucket='bucket',
            Delete={
                'Objects': [
                    {
                        'Key': 'key_1'
                    },
                    {
                        'Key': 'key_2'
                    }
                ]
            }
        )

    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    def test_upload_workspace_version__cannot_find_file(
            self,
            make_api_call_mock
    ):
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            'php-7.1'
        )

        with self.assertRaises(s3.NotFoundError) as context_manager:
            s3.upload_workspace_version('bucket', 'file', 'non-existent-file.py')

        self.assertEqual(
            'Application Version does not exist locally (non-existent-file.py). Try uploading the Application Version again.',
            str(context_manager.exception)
        )
        make_api_call_mock.assert_not_called()

    def test_upload_workspace_version__cannot_find_file__platform_workspace(self):
        cwd = os.getcwd()
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            None,
            workspace_type='platform',
            platform_name='my-custom-platform',
            platform_version='1.0.4',
        )

        with self.assertRaises(s3.NotFoundError) as context_manager:
            s3.upload_workspace_version('bucket', 'file', 'non-existent-file.py', workspace_type='Platform')

        self.assertEqual(
            'Platform Version does not exist locally (non-existent-file.py). Try uploading the Application Version again.',
            str(context_manager.exception)
        )
        self.assertEqual(cwd, os.getcwd())

    def test_upload_workspace_version__file_is_too_large(self):
        cwd = os.getcwd()
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            None,
            workspace_type='platform',
            platform_name='my-custom-platform',
            platform_version='1.0.4',
        )

        with mock.patch('ebcli.lib.s3.os.path.getsize') as getsize_mock:
            getsize_mock.return_value = 536870913
            with self.assertRaises(s3.FileTooLargeError) as context_manager:
                s3.upload_workspace_version('bucket', 'file', 'non-existent-file.py', workspace_type='Platform')

        self.assertEqual(
            'Archive cannot be any larger than 512MB',
            str(context_manager.exception)
        )
        self.assertEqual(cwd, os.getcwd())

    @mock.patch('ebcli.lib.s3.simple_upload')
    def test_upload_workspace_version__file_is_small_enough_that_multithreaded_upload_is_unnecessary(
            self,
            simple_upload_mock,
    ):
        cwd = os.getcwd()
        result_mock = mock.MagicMock()
        simple_upload_mock.return_value = result_mock
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            None,
            workspace_type='platform',
            platform_name='my-custom-platform',
            platform_version='1.0.4',
        )

        with mock.patch('ebcli.lib.s3.os.path.getsize') as getsize_mock:
            getsize_mock.return_value = 7340031
            self.assertEqual(
                result_mock,
                s3.upload_workspace_version('bucket', 'file', 'non-existent-file.py', workspace_type='Platform')
            )

        self.assertEqual(cwd, os.getcwd())
        simple_upload_mock.assert_called_once_with('bucket', 'file', 'non-existent-file.py')

    @mock.patch('ebcli.lib.s3.multithreaded_upload')
    def test_upload_workspace_version__file_requires_multithreaded_upload(
            self,
            multithreaded_upload_mock,
    ):
        cwd = os.getcwd()
        result_mock = mock.MagicMock()
        multithreaded_upload_mock.return_value = result_mock
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            None,
            workspace_type='platform',
            platform_name='my-custom-platform',
            platform_version='1.0.4',
        )

        with mock.patch('ebcli.lib.s3.os.path.getsize') as getsize_mock:
            getsize_mock.return_value = 536870911
            self.assertEqual(
                result_mock,
                s3.upload_workspace_version('bucket', 'file', 'non-existent-file.py', workspace_type='Platform')
            )

        self.assertEqual(cwd, os.getcwd())
        multithreaded_upload_mock.assert_called_once_with('bucket', 'file', 'non-existent-file.py')

    @mock.patch('ebcli.lib.s3.upload_workspace_version')
    def test_upload_application_version(
            self,
            upload_workspace_version_mock
    ):
        s3.upload_application_version('bucket', 'key', 'file/path.py')

        upload_workspace_version_mock.assert_called_once_with('bucket', 'key', 'file/path.py', 'Application')

    @mock.patch('ebcli.lib.s3.upload_workspace_version')
    def test_upload_platform_version(
            self,
            upload_workspace_version_mock
    ):
        s3.upload_platform_version('bucket', 'key', 'file/path.py')

        upload_workspace_version_mock.assert_called_once_with('bucket', 'key', 'file/path.py', 'Platform')

    @mock.patch('ebcli.lib.s3.upload_file')
    def test_simple_upload(
            self,
            upload_file_mock
    ):
        upload_file_mock.return_value = 'result'
        self.assertEqual(
            'result',
            s3.simple_upload('bucket', 'key', 'file/path.py')
        )
        upload_file_mock.assert_called_once_with('bucket', 'key', 'file/path.py')

    def test_wait_for_threads(self):
        def noop():
            pass

        threads = []
        for i in range(0, 3):
            t = threading.Thread(noop())
            t.start()
            threads.append(t)
        s3._wait_for_threads(threads)
        s3._wait_for_threads([])

    @mock.patch('ebcli.lib.s3._get_multipart_upload_id')
    @mock.patch('ebcli.lib.s3.io.update_upload_progress')
    @mock.patch('ebcli.lib.s3._wait_for_threads')
    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    @mock.patch('ebcli.lib.s3._all_parts_were_uploaded')
    @mock.patch('ebcli.lib.s3.threading.Thread')
    def test_multithreaded_upload__all_parts_were_uploaded(
            self,
            Thread_mock,
            _all_parts_were_uploaded_mock,
            make_api_call_mock,
            _wait_for_threads_mock,
            update_upload_progress_mock,
            _get_multipart_upload_id_mock
    ):
        with open('tempfile.txt', 'w') as file:
            file.write('a' * 1000000)

        thread_mocks = [
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
        ]
        Thread_mock.side_effect = thread_mocks
        _get_multipart_upload_id_mock.return_value = 'upload_id'
        _all_parts_were_uploaded_mock.return_value = True

        self.assertTrue(
            s3.multithreaded_upload('bucket', 'key', 'tempfile.txt')
        )
        _get_multipart_upload_id_mock.assert_called_once_with('bucket', 'key')
        update_upload_progress_mock.assert_has_calls([mock.call(0)])
        _wait_for_threads_mock.assert_called_once_with(thread_mocks)
        make_api_call_mock.assert_called_once_with(
            's3', 'complete_multipart_upload', Bucket='bucket', Key='key', MultipartUpload={'Parts': []}, UploadId='upload_id'
        )

    @mock.patch('ebcli.lib.s3._get_multipart_upload_id')
    @mock.patch('ebcli.lib.s3.io.update_upload_progress')
    @mock.patch('ebcli.lib.s3._wait_for_threads')
    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    @mock.patch('ebcli.lib.s3._all_parts_were_uploaded')
    @mock.patch('ebcli.lib.s3.threading.Thread')
    def test_multithreaded_upload__some_parts_were_not_uploaded(
            self,
            Thread_mock,
            _all_parts_were_uploaded_mock,
            make_api_call_mock,
            _wait_for_threads_mock,
            update_upload_progress_mock,
            _get_multipart_upload_id_mock
    ):
        with open('tempfile.txt', 'w') as file:
            file.write('a' * 1000000)

        thread_mocks = [
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
        ]
        Thread_mock.side_effect = thread_mocks
        _get_multipart_upload_id_mock.return_value = 'upload_id'
        _all_parts_were_uploaded_mock.return_value = False

        with self.assertRaises(s3.UploadError) as context_manager:
            s3.multithreaded_upload('bucket', 'key', 'tempfile.txt')
        self.assertEqual(
            'An error occured while uploading Application Version. Use the --debug option for more information if the problem persists.',
            str(context_manager.exception)
        )

        _get_multipart_upload_id_mock.assert_called_once_with('bucket', 'key')
        update_upload_progress_mock.assert_has_calls([mock.call(0)])
        _wait_for_threads_mock.assert_called_once_with(thread_mocks)
        make_api_call_mock.assert_not_called()

    @mock.patch('ebcli.lib.s3._get_multipart_upload_id')
    @mock.patch('ebcli.lib.s3.io.update_upload_progress')
    @mock.patch('ebcli.lib.s3._wait_for_threads')
    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    @mock.patch('ebcli.lib.s3._all_parts_were_uploaded')
    @mock.patch('ebcli.lib.s3.threading.Thread')
    def test_multithreaded_upload__exception_raised(
            self,
            Thread_mock,
            _all_parts_were_uploaded_mock,
            make_api_call_mock,
            _wait_for_threads_mock,
            update_upload_progress_mock,
            _get_multipart_upload_id_mock
    ):
        with open('tempfile.txt', 'w') as file:
            file.write('a' * 10000)

        thread_mocks = [
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
        ]
        Thread_mock.side_effect = thread_mocks
        _get_multipart_upload_id_mock.return_value = 'upload_id'
        _all_parts_were_uploaded_mock.return_value = True
        make_api_call_mock.side_effect = Exception

        with self.assertRaises(Exception):
            s3.multithreaded_upload('bucket', 'key', 'tempfile.txt')

        _get_multipart_upload_id_mock.assert_called_once_with('bucket', 'key')
        update_upload_progress_mock.assert_has_calls([mock.call(0)])
        _wait_for_threads_mock.assert_called_once_with(thread_mocks)

    @mock.patch('ebcli.lib.s3.io.update_upload_progress')
    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    @mock.patch('ebcli.lib.s3._read_next_section_from_file')
    @mock.patch('ebcli.lib.s3._get_part_etag')
    @mock.patch('ebcli.lib.s3.BytesIO')
    def test_upload_chunk(
            self,
            BytesIO_mock,
            _get_part_etag_mock,
            _read_next_section_from_file_mock,
            make_api_call_mock,
            update_upload_progress_mock
    ):
        bytes_io_instance_mock = mock.MagicMock()
        BytesIO_mock.return_value = bytes_io_instance_mock
        _read_next_section_from_file_mock.return_value = ('data', 'part')
        with open('tempfile.txt', 'w') as file:
            file.write('a' * 10000)

        _get_part_etag_mock.side_effect = [
            None,
            {'ETag': 'Tag 1'},
            s3.EndOfTestError
        ]
        make_api_call_mock.return_value = 'response 1'
        lock = threading.Lock()
        file_mock = mock.MagicMock()
        etaglist = []
        total_parts = 8

        s3._upload_chunk(file_mock, lock, etaglist, total_parts, 'bucket', 'key', 'upload_id')

        update_upload_progress_mock.assert_called_once_with(0.125)
        make_api_call_mock.assert_called_once_with(
            's3',
            'upload_part',
            Body=bytes_io_instance_mock, Bucket='bucket', Key='key', PartNumber='part', UploadId='upload_id'
        )
        _read_next_section_from_file_mock.assert_has_calls(
            [
                mock.call(file_mock, lock),
                mock.call(file_mock, lock),
            ]
        )

    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    def test_get_part_etag__required_attribute_not_in_response(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = {}

        self.assertIsNone(s3._get_part_etag('bucket', 'key', 1, 'upload-id'))

        make_api_call_mock.assert_called_once_with(
            's3',
            'list_parts',
            Bucket='bucket',
            Key='key',
            UploadId='upload-id'
        )

    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    def test_get_part_etag__required_attribute_present__etag_found(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = {
            'Parts': [
                {
                    'ETag': 'etag',
                    'PartNumber': 1,
                }
            ]
        }

        self.assertEqual('etag', s3._get_part_etag('bucket', 'key', 1, 'upload-id'))

        make_api_call_mock.assert_called_once_with(
            's3',
            'list_parts',
            Bucket='bucket',
            Key='key',
            UploadId='upload-id'
        )

    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    def test_get_part_etag__required_attribute_present__etag_not_found(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = {
            'Parts': [
                {
                    'ETag': 'etag',
                    'PartNumber': 2,
                }
            ]
        }

        self.assertIsNone(s3._get_part_etag('bucket', 'key', 1, 'upload-id'))

        make_api_call_mock.assert_called_once_with(
            's3',
            'list_parts',
            Bucket='bucket',
            Key='key',
            UploadId='upload-id'
        )

    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    def test_get_multipart_upload_id__upload_id_found(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = {
            'Uploads': [
                {
                    'Key': 'key',
                    'UploadId': 1,
                }
            ]
        }

        self.assertEqual(1, s3._get_multipart_upload_id('bucket', 'key'))

        make_api_call_mock.assert_called_once_with(
            's3',
            'list_multipart_uploads',
            Bucket='bucket',
            Prefix='key'
        )

    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    def test_get_multipart_upload_id__upload_id_absent_in_response_of_list_multipart_uploads__multipart_upload_created(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.side_effect = [
            {
                'Uploads': [
                    {
                        'Key': 'key',
                    }
                ]
            },
            {
                'UploadId': 1
            }

        ]

        self.assertEqual(1, s3._get_multipart_upload_id('bucket', 'key'))

        make_api_call_mock.assert_has_calls(
            [
                mock.call(
                    's3',
                    'list_multipart_uploads',
                    Bucket='bucket',
                    Prefix='key'
                ),
                mock.call(
                    's3',
                    'create_multipart_upload',
                    Bucket='bucket',
                    Key='key'
                )
            ]
        )

    def test_read_next_section_from_file(self):
        lock = threading.Lock()
        file_mock = mock.MagicMock()

        mock_open = mock.mock_open()

        self.assertEqual(0, s3._read_next_section_from_file.part_num)
        with mock.patch('ebcli.lib.s3.open', mock_open, create=True):
            s3._read_next_section_from_file(file_mock, lock)
            s3._read_next_section_from_file(file_mock, lock)
        self.assertEqual(2, s3._read_next_section_from_file.part_num)

        setattr(s3._read_next_section_from_file, 'part_num', 0)
