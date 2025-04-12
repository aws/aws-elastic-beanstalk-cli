# Copyright 2025 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import shutil
import unittest

import mock

from ebcli.core.ebcore import EB
from ebcli.core import fileoperations
from ebcli.operations import commonops
from ebcli.objects.exceptions import InvalidOptionsError, NotFoundError

from .. import mock_responses


class TestDeploy(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.getcwd()
        if os.path.exists("testDir"):
            shutil.rmtree("testDir")
        os.mkdir("testDir")
        os.chdir("testDir")

        # Create a basic .elasticbeanstalk/config.yml file
        fileoperations.create_config_file("my-application", "us-west-2", "php-7.2")
        commonops.set_environment_for_current_branch("environment-1")

        # Create a sample application file
        with open("app.py", "w") as f:
            f.write('print("Hello, Elastic Beanstalk!")')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree("testDir")

    def setup_git_repo(self):
        """Set up a basic Git repository for testing - only call this in tests that need Git"""
        os.system("git init")
        os.system('git config user.email "test@example.com"')
        os.system('git config user.name "Test User"')

        # Create initial branch (will be 'main' or 'master' depending on git version)
        branch_name = self._get_default_branch_name()

        # Make sure the branch name in .elasticbeanstalk/config.yml matches the git branch
        self._update_config_with_branch_name(branch_name)

        # Add and commit a file
        os.system("git add app.py")
        os.system('git commit -m "Initial commit"')

    def _get_default_branch_name(self):
        """Get the default branch name from the git repository"""
        # Execute git command to get the current branch name
        import subprocess

        try:
            result = subprocess.check_output(
                ["git", "branch", "--show-current"],
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            ).strip()
            if result:
                return result
            # Older git versions might not support --show-current
            result = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            ).strip()
            return result
        except (subprocess.CalledProcessError, OSError):
            # Default to 'main' if we can't determine the branch name
            return "main"

    def _update_config_with_branch_name(self, branch_name):
        fileoperations.write_config_setting(
            "branch-defaults", branch_name, {"environment": "environment-1"}
        )

    @mock.patch(
        "ebcli.operations.deployops.elasticbeanstalk.update_env_application_version"
    )
    @mock.patch("ebcli.operations.commonops.wait_for_success_events")
    @mock.patch(
        "ebcli.operations.commonops.elasticbeanstalk.application_version_exists"
    )
    @mock.patch("ebcli.operations.commonops.elasticbeanstalk.get_storage_location")
    @mock.patch("ebcli.operations.commonops.s3.get_object_info")
    @mock.patch("ebcli.operations.commonops.s3.upload_application_version")
    @mock.patch(
        "ebcli.operations.commonops.elasticbeanstalk.create_application_version"
    )
    @mock.patch("ebcli.controllers.deploy._check_env_lifecycle_state")
    def test_deploy_basic(
        self,
        _check_env_lifecycle_state_mock,
        create_application_version_mock,
        upload_application_version_mock,
        get_object_info_mock,
        get_storage_location_mock,
        application_version_exists_mock,
        wait_for_success_events_mock,
        update_env_mock,
    ):
        """Test basic deployment with no additional options"""
        # Set up mocks
        update_env_mock.return_value = "request-id"
        application_version_exists_mock.return_value = None
        get_storage_location_mock.return_value = "my-s3-bucket-location"
        get_object_info_mock.side_effect = NotFoundError

        # Run command
        app = EB(argv=["deploy"])
        app.setup()
        app.run()

        # Verify
        update_env_call_args = update_env_mock.call_args[0]
        assert update_env_call_args[0] == "environment-1"
        # app-250412_014106958315 or something like that
        assert update_env_call_args[1].startswith("app-")
        assert update_env_call_args[2] is None
        upload_application_version_mock.assert_called_once_with(
            "my-s3-bucket-location",
            f"my-application/{update_env_call_args[1]}.zip",
            os.path.join(
                os.getcwd(),
                ".elasticbeanstalk",
                "app_versions",
                f"{update_env_call_args[1]}.zip",
            ),
        )
        get_object_info_mock.assert_called_once_with(
            "my-s3-bucket-location",
            f"my-application/{update_env_call_args[1]}.zip",
        )
        get_storage_location_mock.assert_called_once_with()
        create_application_version_mock.assert_called_once_with(
            "my-application",
            update_env_call_args[1],
            "EB-CLI deploy",
            "my-s3-bucket-location",
            f"my-application/{update_env_call_args[1]}.zip",
            False,
            None,
            None,
            None,
        )
        wait_for_success_events_mock.assert_called_once_with(
            "request-id",
            timeout_in_minutes=None,
            can_abort=True,
            env_name="environment-1",
        )

    @mock.patch(
        "ebcli.operations.deployops.elasticbeanstalk.update_env_application_version"
    )
    @mock.patch("ebcli.operations.commonops.wait_for_success_events")
    @mock.patch(
        "ebcli.operations.commonops.elasticbeanstalk.application_version_exists"
    )
    @mock.patch("ebcli.operations.commonops.elasticbeanstalk.get_storage_location")
    @mock.patch("ebcli.operations.commonops.s3.get_object_info")
    @mock.patch("ebcli.operations.commonops.s3.upload_application_version")
    @mock.patch(
        "ebcli.operations.commonops.elasticbeanstalk.create_application_version"
    )
    @mock.patch("ebcli.controllers.deploy._check_env_lifecycle_state")
    def test_deploy_combined_options(
        self,
        _check_env_lifecycle_state_mock,
        create_application_version_mock,
        upload_application_version_mock,
        get_object_info_mock,
        get_storage_location_mock,
        application_version_exists_mock,
        wait_for_success_events_mock,
        update_env_mock,
    ):
        """Test deploying with multiple options combined (environment, label, message, nohang)"""
        # Set up mocks
        update_env_mock.return_value = "request-id"
        application_version_exists_mock.return_value = None
        get_storage_location_mock.return_value = "my-s3-bucket-location"
        get_object_info_mock.side_effect = NotFoundError

        # Run command with all options combined
        app = EB(
            argv=[
                "deploy",
                "environment-2",
                "--label",
                "custom-label",
                "--message",
                "Test deployment message",
                "--nohang",
            ]
        )
        app.setup()
        app.run()

        # Verify
        # Should use the specified environment
        update_env_mock.assert_called_once_with("environment-2", "custom-label", None)

        # Should use the custom label
        upload_application_version_mock.assert_called_once_with(
            "my-s3-bucket-location",
            "my-application/custom-label.zip",
            os.path.join(
                os.getcwd(), ".elasticbeanstalk", "app_versions", "custom-label.zip"
            ),
        )

        get_object_info_mock.assert_called_once_with(
            "my-s3-bucket-location",
            "my-application/custom-label.zip",
        )

        get_storage_location_mock.assert_called_once_with()

        # Should use the custom message
        create_application_version_mock.assert_called_once_with(
            "my-application",
            "custom-label",
            "Test deployment message",
            "my-s3-bucket-location",
            "my-application/custom-label.zip",
            False,
            None,
            None,
            None,
        )

        # Should use nohang (timeout=0)
        wait_for_success_events_mock.assert_called_once_with(
            "request-id", timeout_in_minutes=0, can_abort=True, env_name="environment-2"
        )

    @mock.patch(
        "ebcli.operations.deployops.elasticbeanstalk.update_env_application_version"
    )
    @mock.patch("ebcli.operations.commonops.wait_for_success_events")
    @mock.patch(
        "ebcli.operations.commonops.elasticbeanstalk.application_version_exists"
    )
    @mock.patch("ebcli.operations.commonops.elasticbeanstalk.get_storage_location")
    @mock.patch("ebcli.operations.commonops.s3.get_object_info")
    @mock.patch("ebcli.operations.commonops.s3.upload_application_version")
    @mock.patch(
        "ebcli.operations.commonops.elasticbeanstalk.create_application_version"
    )
    @mock.patch("ebcli.controllers.deploy._check_env_lifecycle_state")
    def test_deploy_with_label(
        self,
        _check_env_lifecycle_state_mock,
        create_application_version_mock,
        upload_application_version_mock,
        get_object_info_mock,
        get_storage_location_mock,
        application_version_exists_mock,
        wait_for_success_events_mock,
        update_env_mock,
    ):
        """Test deploying with a custom version label"""
        # Set up mocks
        update_env_mock.return_value = "request-id"
        application_version_exists_mock.return_value = None
        get_storage_location_mock.return_value = "my-s3-bucket-location"
        get_object_info_mock.side_effect = NotFoundError

        # Run command
        app = EB(argv=["deploy", "--label", "custom-label"])
        app.setup()
        app.run()

        # Verify
        update_env_mock.assert_called_once_with("environment-1", "custom-label", None)
        upload_application_version_mock.assert_called_once_with(
            "my-s3-bucket-location",
            "my-application/custom-label.zip",
            os.path.join(
                os.getcwd(), ".elasticbeanstalk", "app_versions", "custom-label.zip"
            ),
        )
        get_object_info_mock.assert_called_once_with(
            "my-s3-bucket-location",
            "my-application/custom-label.zip",
        )
        get_storage_location_mock.assert_called_once_with()
        create_application_version_mock.assert_called_once_with(
            "my-application",
            "custom-label",
            "EB-CLI deploy",
            "my-s3-bucket-location",
            "my-application/custom-label.zip",
            False,
            None,
            None,
            None,
        )
        wait_for_success_events_mock.assert_called_once_with(
            "request-id",
            timeout_in_minutes=None,
            can_abort=True,
            env_name="environment-1",
        )

    @mock.patch(
        "ebcli.operations.deployops.elasticbeanstalk.update_env_application_version"
    )
    @mock.patch("ebcli.operations.commonops.wait_for_success_events")
    @mock.patch(
        "ebcli.operations.commonops.elasticbeanstalk.application_version_exists"
    )
    @mock.patch("ebcli.operations.commonops.elasticbeanstalk.get_storage_location")
    @mock.patch("ebcli.operations.commonops.s3.get_object_info")
    @mock.patch("ebcli.operations.commonops.s3.upload_application_version")
    @mock.patch(
        "ebcli.operations.commonops.elasticbeanstalk.create_application_version"
    )
    @mock.patch("ebcli.controllers.deploy._check_env_lifecycle_state")
    def test_deploy_with_message(
        self,
        _check_env_lifecycle_state_mock,
        create_application_version_mock,
        upload_application_version_mock,
        get_object_info_mock,
        get_storage_location_mock,
        application_version_exists_mock,
        wait_for_success_events_mock,
        update_env_mock,
    ):
        """Test deploying with a custom version message"""
        # Set up mocks
        update_env_mock.return_value = "request-id"
        application_version_exists_mock.return_value = None
        get_storage_location_mock.return_value = "my-s3-bucket-location"
        get_object_info_mock.side_effect = NotFoundError

        # Run command
        app = EB(argv=["deploy", "--message", "Test deployment message"])
        app.setup()
        app.run()

        # Verify
        update_env_call_args = update_env_mock.call_args[0]
        assert update_env_call_args[0] == "environment-1"
        assert update_env_call_args[1].startswith("app-")
        assert update_env_call_args[2] is None

        upload_application_version_mock.assert_called_once_with(
            "my-s3-bucket-location",
            f"my-application/{update_env_call_args[1]}.zip",
            os.path.join(
                os.getcwd(),
                ".elasticbeanstalk",
                "app_versions",
                f"{update_env_call_args[1]}.zip",
            ),
        )
        get_object_info_mock.assert_called_once_with(
            "my-s3-bucket-location",
            f"my-application/{update_env_call_args[1]}.zip",
        )
        get_storage_location_mock.assert_called_once_with()
        create_application_version_mock.assert_called_once_with(
            "my-application",
            update_env_call_args[1],
            "Test deployment message",
            "my-s3-bucket-location",
            f"my-application/{update_env_call_args[1]}.zip",
            False,
            None,
            None,
            None,
        )
        wait_for_success_events_mock.assert_called_once_with(
            "request-id",
            timeout_in_minutes=None,
            can_abort=True,
            env_name="environment-1",
        )

    @mock.patch(
        "ebcli.operations.deployops.elasticbeanstalk.update_env_application_version"
    )
    @mock.patch("ebcli.operations.commonops.wait_for_success_events")
    @mock.patch(
        "ebcli.operations.commonops.elasticbeanstalk.application_version_exists"
    )
    @mock.patch("ebcli.operations.commonops.elasticbeanstalk.get_storage_location")
    @mock.patch("ebcli.operations.commonops.s3.get_object_info")
    @mock.patch("ebcli.operations.commonops.s3.upload_application_version")
    @mock.patch(
        "ebcli.operations.commonops.elasticbeanstalk.create_application_version"
    )
    @mock.patch("ebcli.controllers.deploy._check_env_lifecycle_state")
    def test_deploy_with_nohang(
        self,
        _check_env_lifecycle_state_mock,
        create_application_version_mock,
        upload_application_version_mock,
        get_object_info_mock,
        get_storage_location_mock,
        application_version_exists_mock,
        wait_for_success_events_mock,
        update_env_mock,
    ):
        """Test deploying with the nohang option"""
        # Set up mocks
        update_env_mock.return_value = "request-id"
        application_version_exists_mock.return_value = None
        get_storage_location_mock.return_value = "my-s3-bucket-location"
        get_object_info_mock.side_effect = NotFoundError

        # Run command
        app = EB(argv=["deploy", "--nohang"])
        app.setup()
        app.run()

        # Verify
        update_env_call_args = update_env_mock.call_args[0]
        assert update_env_call_args[0] == "environment-1"
        assert update_env_call_args[1].startswith("app-")
        assert update_env_call_args[2] is None

        upload_application_version_mock.assert_called_once_with(
            "my-s3-bucket-location",
            f"my-application/{update_env_call_args[1]}.zip",
            os.path.join(
                os.getcwd(),
                ".elasticbeanstalk",
                "app_versions",
                f"{update_env_call_args[1]}.zip",
            ),
        )
        get_object_info_mock.assert_called_once_with(
            "my-s3-bucket-location",
            f"my-application/{update_env_call_args[1]}.zip",
        )
        get_storage_location_mock.assert_called_once_with()
        create_application_version_mock.assert_called_once()

        # Should not wait for success events (timeout=0)
        wait_for_success_events_mock.assert_called_once_with(
            "request-id", timeout_in_minutes=0, can_abort=True, env_name="environment-1"
        )

    @mock.patch(
        "ebcli.operations.deployops.elasticbeanstalk.update_env_application_version"
    )
    @mock.patch("ebcli.operations.commonops.wait_for_success_events")
    @mock.patch(
        "ebcli.operations.commonops.elasticbeanstalk.application_version_exists"
    )
    @mock.patch("ebcli.operations.commonops.elasticbeanstalk.get_storage_location")
    @mock.patch("ebcli.operations.commonops.s3.get_object_info")
    @mock.patch("ebcli.operations.commonops.s3.upload_application_version")
    @mock.patch(
        "ebcli.operations.commonops.elasticbeanstalk.create_application_version"
    )
    @mock.patch("ebcli.controllers.deploy._check_env_lifecycle_state")
    def test_deploy_with_timeout(
        self,
        _check_env_lifecycle_state_mock,
        create_application_version_mock,
        upload_application_version_mock,
        get_object_info_mock,
        get_storage_location_mock,
        application_version_exists_mock,
        wait_for_success_events_mock,
        update_env_mock,
    ):
        """Test deploying with a custom timeout"""
        # Set up mocks
        update_env_mock.return_value = "request-id"
        application_version_exists_mock.return_value = None
        get_storage_location_mock.return_value = "my-s3-bucket-location"
        get_object_info_mock.side_effect = NotFoundError

        # Run command
        app = EB(argv=["deploy", "--timeout", "10"])
        app.setup()
        app.run()

        # Verify
        update_env_call_args = update_env_mock.call_args[0]
        assert update_env_call_args[0] == "environment-1"
        assert update_env_call_args[1].startswith("app-")
        assert update_env_call_args[2] is None

        upload_application_version_mock.assert_called_once_with(
            "my-s3-bucket-location",
            f"my-application/{update_env_call_args[1]}.zip",
            os.path.join(
                os.getcwd(),
                ".elasticbeanstalk",
                "app_versions",
                f"{update_env_call_args[1]}.zip",
            ),
        )
        get_object_info_mock.assert_called_once_with(
            "my-s3-bucket-location",
            f"my-application/{update_env_call_args[1]}.zip",
        )
        get_storage_location_mock.assert_called_once_with()
        create_application_version_mock.assert_called_once()
        wait_for_success_events_mock.assert_called_once_with(
            "request-id",
            timeout_in_minutes=10,
            can_abort=True,
            env_name="environment-1",
        )

    @mock.patch(
        "ebcli.operations.deployops.elasticbeanstalk.update_env_application_version"
    )
    @mock.patch("ebcli.operations.commonops.wait_for_success_events")
    @mock.patch(
        "ebcli.operations.commonops.elasticbeanstalk.application_version_exists"
    )
    @mock.patch("ebcli.operations.commonops.elasticbeanstalk.get_storage_location")
    @mock.patch("ebcli.operations.commonops.s3.get_object_info")
    @mock.patch("ebcli.operations.commonops.s3.upload_application_version")
    @mock.patch(
        "ebcli.operations.commonops.elasticbeanstalk.create_application_version"
    )
    @mock.patch("ebcli.controllers.deploy._check_env_lifecycle_state")
    @mock.patch("ebcli.operations.gitops.git_management_enabled")
    @mock.patch("ebcli.operations.commonops.wait_for_processed_app_versions")
    def test_deploy_with_staged(
        self,
        wait_for_processed_app_versions_mock,
        git_management_enabled_mock,
        _check_env_lifecycle_state_mock,
        create_application_version_mock,
        upload_application_version_mock,
        get_object_info_mock,
        get_storage_location_mock,
        application_version_exists_mock,
        wait_for_success_events_mock,
        update_env_mock,
    ):
        """Test deploying with the staged option"""
        # Set up Git repository for this test - required for --staged option
        self.setup_git_repo()

        # Make a change to stage
        with open("app.py", "a") as f:
            f.write('\nprint("Staged change")')
        os.system("git add app.py")

        # Set up mocks
        git_management_enabled_mock.return_value = (
            False  # Ensure we don't use CodeCommit
        )
        update_env_mock.return_value = "request-id"
        application_version_exists_mock.return_value = None
        get_storage_location_mock.return_value = "my-s3-bucket-location"
        get_object_info_mock.side_effect = NotFoundError

        # Run command
        app = EB(argv=["deploy", "--staged"])
        app.setup()
        app.run()

        # Verify
        update_env_call_args = update_env_mock.call_args[0]
        assert update_env_call_args[0] == "environment-1"
        assert update_env_call_args[1].startswith("app-")
        assert (
            "-stage-" in update_env_call_args[1]
        )  # Staged version should have -stage- in the name
        assert update_env_call_args[2] is None

        upload_application_version_mock.assert_called_once_with(
            "my-s3-bucket-location",
            f"my-application/{update_env_call_args[1]}.zip",
            os.path.join(
                os.getcwd(),
                ".elasticbeanstalk",
                "app_versions",
                f"{update_env_call_args[1]}.zip",
            ),
        )
        get_object_info_mock.assert_called_once_with(
            "my-s3-bucket-location",
            f"my-application/{update_env_call_args[1]}.zip",
        )
        get_storage_location_mock.assert_called_once_with()
        create_application_version_mock.assert_called_once()
        wait_for_success_events_mock.assert_called_once_with(
            "request-id",
            timeout_in_minutes=None,
            can_abort=True,
            env_name="environment-1",
        )

    @mock.patch("ebcli.operations.deployops.commonops.create_app_version_from_source")
    @mock.patch(
        "ebcli.operations.deployops.elasticbeanstalk.update_env_application_version"
    )
    @mock.patch("ebcli.operations.commonops.wait_for_success_events")
    @mock.patch("ebcli.controllers.deploy._check_env_lifecycle_state")
    @mock.patch("ebcli.operations.deployops.commonops.wait_for_processed_app_versions")
    def test_deploy_with_source(
        self,
        wait_for_processed_app_versions_mock,
        _check_env_lifecycle_state_mock,
        wait_for_success_events_mock,
        update_env_mock,
        create_app_version_from_source_mock,
    ):
        """Test deploying with a specific source"""
        # Set up mocks
        create_app_version_from_source_mock.return_value = "version-label"
        update_env_mock.return_value = "request-id"

        # Run command
        app = EB(argv=["deploy", "--source", "codecommit/my-repo/my-branch"])
        app.setup()
        app.run()

        # Verify
        create_app_version_from_source_mock.assert_called_once_with(
            "my-application",
            "codecommit/my-repo/my-branch",
            process=False,
            label=None,
            message=None,
            build_config=None,
        )
        update_env_mock.assert_called_once_with("environment-1", "version-label", None)
        wait_for_success_events_mock.assert_called_once_with(
            "request-id",
            timeout_in_minutes=None,
            can_abort=True,
            env_name="environment-1",
        )
        wait_for_processed_app_versions_mock.assert_called_once_with(
            "my-application",
            ["version-label"],
            timeout=5,
        )

    @mock.patch(
        "ebcli.operations.deployops.elasticbeanstalk.update_env_application_version"
    )
    @mock.patch("ebcli.operations.commonops.create_app_version")
    @mock.patch("ebcli.operations.commonops.wait_for_success_events")
    @mock.patch("ebcli.operations.commonops.wait_for_processed_app_versions")
    @mock.patch("ebcli.controllers.deploy._check_env_lifecycle_state")
    def test_deploy_with_process(
        self,
        _check_env_lifecycle_state_mock,
        wait_for_processed_app_versions_mock,
        wait_for_success_events_mock,
        create_app_version_mock,
        update_env_mock,
    ):
        """Test deploying with the process option"""
        # Set up mocks
        create_app_version_mock.return_value = "version-label"
        update_env_mock.return_value = "request-id"
        wait_for_processed_app_versions_mock.return_value = True

        # Run command
        app = EB(argv=["deploy", "--process"])
        app.setup()
        app.run()

        # Verify
        create_app_version_mock.assert_called_once()
        wait_for_processed_app_versions_mock.assert_called_once_with(
            "my-application", ["version-label"], timeout=5
        )
        update_env_mock.assert_called_once_with("environment-1", "version-label", None)
        # Should process app versions
        self.assertTrue(app.pargs.process)

    @mock.patch("ebcli.controllers.deploy._check_env_lifecycle_state")
    def test_deploy_with_version_and_label(self, _check_env_lifecycle_state_mock):
        """Test deploying with incompatible options (version and label)"""
        # Run command and expect an exception
        app = EB(
            argv=["deploy", "--version", "existing-version", "--label", "new-label"]
        )
        app.setup()

        with self.assertRaises(InvalidOptionsError):
            app.run()

    @mock.patch("ebcli.operations.deployops.fileoperations.build_spec_exists")
    @mock.patch("ebcli.operations.deployops.fileoperations.get_build_configuration")
    @mock.patch(
        "ebcli.operations.deployops.elasticbeanstalk.update_env_application_version"
    )
    @mock.patch("ebcli.operations.commonops.create_app_version")
    @mock.patch(
        "ebcli.operations.buildspecops.stream_build_configuration_app_version_creation"
    )
    @mock.patch("ebcli.operations.commonops.wait_for_success_events")
    @mock.patch("ebcli.controllers.deploy._check_env_lifecycle_state")
    def test_deploy_with_buildspec(
        self,
        _check_env_lifecycle_state_mock,
        wait_for_success_events_mock,
        stream_build_mock,
        create_app_version_mock,
        update_env_mock,
        get_build_config_mock,
        build_spec_exists_mock,
    ):
        """Test deploying with a buildspec.yml file"""
        # Set up mocks
        build_spec_exists_mock.return_value = True
        build_config = mock.MagicMock()
        get_build_config_mock.return_value = build_config
        create_app_version_mock.return_value = "version-label"
        update_env_mock.return_value = "request-id"

        # Run command
        app = EB(argv=["deploy"])
        app.setup()
        app.run()

        # Verify
        build_spec_exists_mock.assert_called_once()
        get_build_config_mock.assert_called_once()
        create_app_version_mock.assert_called_once_with(
            "my-application",
            process=False,
            label=None,
            message=None,
            staged=False,
            build_config=build_config,
        )
        stream_build_mock.assert_called_once_with(
            "my-application", "version-label", build_config
        )
        update_env_mock.assert_called_once_with("environment-1", "version-label", None)
        wait_for_success_events_mock.assert_called_once()

    @mock.patch(
        "ebcli.operations.deployops.elasticbeanstalk.update_env_application_version"
    )
    @mock.patch("ebcli.operations.commonops.create_codecommit_app_version")
    @mock.patch("ebcli.operations.commonops.wait_for_success_events")
    @mock.patch("ebcli.controllers.deploy._check_env_lifecycle_state")
    @mock.patch("ebcli.operations.gitops.git_management_enabled")
    @mock.patch("ebcli.operations.commonops.wait_for_processed_app_versions")
    def test_deploy_with_codecommit(
        self,
        wait_for_processed_app_versions_mock,
        git_management_enabled_mock,
        _check_env_lifecycle_state_mock,
        wait_for_success_events_mock,
        create_codecommit_app_version_mock,
        update_env_mock,
    ):
        """Test deploying with CodeCommit integration"""
        # Set up Git repository for this test
        self.setup_git_repo()

        # Set up mocks
        git_management_enabled_mock.return_value = True  # Enable CodeCommit
        create_codecommit_app_version_mock.return_value = "version-label"
        update_env_mock.return_value = "request-id"
        wait_for_processed_app_versions_mock.return_value = True

        # Run command
        app = EB(argv=["deploy"])
        app.setup()
        app.run()

        # Verify
        create_codecommit_app_version_mock.assert_called_once_with(
            "my-application", process=False, label=None, message=None, build_config=None
        )
        update_env_mock.assert_called_once_with("environment-1", "version-label", None)
        wait_for_success_events_mock.assert_called_once_with(
            "request-id",
            timeout_in_minutes=None,
            can_abort=True,
            env_name="environment-1",
        )
        wait_for_processed_app_versions_mock.assert_called_once_with(
            "my-application", ["version-label"], timeout=5
        )

    @mock.patch(
        "ebcli.operations.deployops.elasticbeanstalk.update_env_application_version"
    )
    @mock.patch("ebcli.operations.commonops.create_app_version")
    @mock.patch("ebcli.operations.commonops.wait_for_success_events")
    @mock.patch("ebcli.controllers.deploy._check_env_lifecycle_state")
    @mock.patch("ebcli.core.fileoperations.env_yaml_exists")
    @mock.patch("ebcli.operations.commonops.wait_for_processed_app_versions")
    def test_deploy_with_env_yaml(
        self,
        wait_for_processed_app_versions_mock,
        env_yaml_exists_mock,
        _check_env_lifecycle_state_mock,
        wait_for_success_events_mock,
        create_app_version_mock,
        update_env_mock,
    ):
        """Test deploying with env.yaml file present"""
        # Set up mocks
        env_yaml_exists_mock.return_value = True
        create_app_version_mock.return_value = "version-label"
        update_env_mock.return_value = "request-id"
        wait_for_processed_app_versions_mock.return_value = True

        # Run command
        app = EB(argv=["deploy"])
        app.setup()
        app.run()

        # Verify
        create_app_version_mock.assert_called_once()
        wait_for_processed_app_versions_mock.assert_called_once_with(
            "my-application", ["version-label"], timeout=5
        )
        update_env_mock.assert_called_once_with("environment-1", "version-label", None)
        wait_for_success_events_mock.assert_called_once()
