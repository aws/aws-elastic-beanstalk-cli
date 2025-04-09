import unittest
import mock

from ebcli.objects.buildconfiguration import BuildConfiguration
from ebcli.operations import deployops


class TestDeployWithSourceBundle(unittest.TestCase):
    app_name = 'ebcli-app'
    app_version_name = 'ebcli-app-version'
    env_name = 'ebcli-env'
    description = 'ebcli testing app'
    s3_bucket = 'app_bucket'
    s3_key = 'app_bucket_key'
    request_id = 'foo-foo-foo-foo'

    image = 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.3'
    compute_type = 'BUILD_GENERAL1_SMALL'
    service_role = 'eb-test'
    timeout = 60
    build_config = BuildConfiguration(image=image, compute_type=compute_type,
                                      service_role=service_role, timeout=timeout)

    @mock.patch('ebcli.operations.deployops.elasticbeanstalk')
    @mock.patch('ebcli.operations.deployops.commonops')
    @mock.patch('ebcli.operations.deployops.aws')
    @mock.patch('ebcli.operations.deployops.fileoperations')
    @mock.patch('ebcli.operations.deployops.io')
    def test_deploy_with_source_bundle(
            self,
            mock_io,
            mock_fileops,
            mock_aws,
            mock_commonops,
            mock_beanstalk
    ):
        # Setup
        mock_aws.get_region_name.return_value = 'us-east-1'
        mock_fileops.build_spec_exists.return_value = False
        mock_commonops.handle_upload_target.return_value = self.app_version_name
        mock_beanstalk.update_env_application_version.return_value = self.request_id
        source_bundle_path = '/path/to/application.zip'
        label = 'my-label'

        # Call the function with source_bundle parameter
        deployops.deploy(
            self.app_name,
            self.env_name,
            None,
            label,
            self.description,
            source_bundle=source_bundle_path
        )

        # Verify the correct calls were made
        mock_commonops.handle_upload_target.assert_called_with(
            self.app_name,
            None,
            None,
            label,
            source_bundle_path,
            label,
            self.description,
            False,
            None,
            relative_to_project_root=False
        )
        mock_beanstalk.update_env_application_version.assert_called_with(
            self.env_name,
            self.app_version_name,
            None
        )
        mock_commonops.wait_for_success_events.assert_called_with(
            self.request_id,
            can_abort=True,
            env_name='ebcli-env',
            timeout_in_minutes=5
        )
        
    @mock.patch('ebcli.operations.deployops.elasticbeanstalk')
    @mock.patch('ebcli.operations.deployops.commonops')
    @mock.patch('ebcli.operations.deployops.aws')
    @mock.patch('ebcli.operations.deployops.fileoperations')
    @mock.patch('ebcli.operations.deployops.buildspecops')
    @mock.patch('ebcli.operations.deployops.io')
    def test_deploy_with_source_bundle_and_build_config(
            self, 
            mock_io, 
            mock_buildspecops, 
            mock_fileops, 
            mock_aws, 
            mock_commonops, 
            mock_beanstalk
    ):
        # Setup
        mock_aws.get_region_name.return_value = 'us-east-1'
        mock_fileops.build_spec_exists.return_value = True
        build_config = self.build_config
        mock_fileops.get_build_configuration.return_value = build_config
        mock_commonops.handle_upload_target.return_value = self.app_version_name
        mock_beanstalk.update_env_application_version.return_value = self.request_id
        source_bundle_path = '/path/to/application.zip'
        label = 'my-label'

        # Call the function with source_bundle parameter
        deployops.deploy(
            self.app_name,
            self.env_name,
            None,
            label,
            self.description,
            source_bundle=source_bundle_path
        )

        # Verify the correct calls were made
        mock_commonops.handle_upload_target.assert_called_with(
            self.app_name,
            None,
            None,
            label,
            source_bundle_path,
            label,
            self.description,
            False,
            None,
            relative_to_project_root=False
        )
        mock_beanstalk.update_env_application_version.assert_called_with(
            self.env_name,
            self.app_version_name,
            None
        )
        # Verify buildspecops.stream_build_configuration_app_version_creation is NOT called with source_bundle
        mock_buildspecops.stream_build_configuration_app_version_creation.assert_not_called()
