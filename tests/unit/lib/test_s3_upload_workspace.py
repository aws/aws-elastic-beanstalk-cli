import os
import shutil
import unittest
import mock

from ebcli.core import fileoperations
from ebcli.lib import s3


class TestUploadWorkspaceVersion(unittest.TestCase):
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
    @mock.patch('ebcli.lib.s3.os.path.getsize')
    @mock.patch('ebcli.lib.s3.simple_upload')
    def test_upload_workspace_version_with_relative_to_project_root_false(
            self,
            mock_simple_upload,
            mock_getsize,
            mock_make_api_call
    ):
        # Setup
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            'php-7.1'
        )
        mock_getsize.return_value = 7340031  # Small enough for simple upload
        mock_simple_upload.return_value = 'upload_result'
        
        # Create a test file
        with open('test_file.txt', 'w') as f:
            f.write('test content')
        
        # Call the function with relative_to_project_root=False
        result = s3.upload_workspace_version(
            'bucket', 
            'key', 
            'test_file.txt', 
            workspace_type='Application',
            relative_to_project_root=False
        )
        
        # Verify
        self.assertEqual('upload_result', result)
        self.assertEqual(os.getcwd(), os.path.join(self.root_dir, 'testDir'))  # Should not change directory
        mock_simple_upload.assert_called_once_with('bucket', 'key', 'test_file.txt')
        
    @mock.patch('ebcli.lib.s3.aws.make_api_call')
    @mock.patch('ebcli.lib.s3.os.path.getsize')
    @mock.patch('ebcli.lib.s3.simple_upload')
    @mock.patch('ebcli.lib.s3.fileoperations.ProjectRoot.traverse')
    def test_upload_workspace_version_with_relative_to_project_root_true(
            self,
            mock_traverse,
            mock_simple_upload,
            mock_getsize,
            mock_make_api_call
    ):
        # Setup
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            'php-7.1'
        )
        mock_getsize.return_value = 7340031  # Small enough for simple upload
        mock_simple_upload.return_value = 'upload_result'
        
        # Create a test file
        with open('test_file.txt', 'w') as f:
            f.write('test content')
        
        # Call the function with default relative_to_project_root=True
        result = s3.upload_workspace_version(
            'bucket', 
            'key', 
            'test_file.txt', 
            workspace_type='Application'
        )
        
        # Verify
        self.assertEqual('upload_result', result)
        mock_traverse.assert_called()
        mock_simple_upload.assert_called_once_with('bucket', 'key', 'test_file.txt')
