import shutil
import typing
from unittest import skipUnless

import pytest
import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
import unittest
import sys

if sys.platform.startswith("win"):
    import clr

    clr.AddReference("System.Reflection")
    clr.AddReference(r"C:\Windows\System32\inetsrv\Microsoft.Web.Administration.dll")
    clr.AddReference("System")
    clr.AddReference("System.Core")
    try:
        clr.AddReference("System.DirectoryServices.AccountManagement")
        from System.DirectoryServices.AccountManagement import (
            PrincipalContext,
            ContextType,
            ContextType,
            UserPrincipal,
            PrincipalSearcher,
        )
        from System.Collections.Generic import HashSet, Queue
        from System.Reflection import Assembly
        from Microsoft.Web.Administration import (
            ServerManager,
            Binding,
            Site,
            Application,
        )
        from System.Diagnostics import Process, ProcessStartInfo
        from System.Runtime.InteropServices import COMException
    except:
        # TODO: Make this raise on source machine; Pass this on dumb-terminals
        pass

    import json
    from ebcli.objects.exceptions import NotAnEC2Instance, NotFoundError

    # TODO: preserve current state of the IIS server prior to execution of any of the tests
    @skipUnless(os.getenv('EB_IIS_TESTS') == '1', "Run this test suite only if explicitly instructed to.")
    class TestEBMigrateIntegration(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            """Setup that runs once for the entire test class"""
            test_dir = Path(".") / "testDir"
            test_dir.mkdir(exist_ok=True)
            cls.state_file = test_dir / "iis_state_file.json"
            cls.backup_state()
            cls.original_dir = os.getcwd()
            os.chdir(test_dir)

            # Save existing firewall rules for HTTP/HTTPS ports
            cls.saved_firewall_rules = cls.get_existing_firewall_rules()

            # After backing up, wipe all sites
            server_manager = ServerManager()
            for site in list(server_manager.Sites):
                server_manager.Sites.Remove(site)
            server_manager.CommitChanges()

        @staticmethod
        def get_existing_firewall_rules():
            """Get existing firewall rules for HTTP/HTTPS ports"""
            try:
                result = subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        'Get-NetFirewallRule | Where-Object { $_.DisplayName -like "*EB-CLI-Test*" } | Select-Object -Property DisplayName | ConvertTo-Json',
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                if result.stdout.strip():
                    try:
                        return json.loads(result.stdout)
                    except json.JSONDecodeError:
                        return []
                return []
            except subprocess.CalledProcessError:
                return []

        def setUp(self):
            """Setup that runs before each test method"""
            # Clear any sites that might exist from previous tests
            self.server_manager = ServerManager()
            for site in list(self.server_manager.Sites):
                self.server_manager.Sites.Remove(site)
            self.server_manager.CommitChanges()

            # Only create Default Web Site for tests that need it
            self.default_site = self.server_manager.Sites.Add(
                "Default Web Site", "http", "*:80:", "c:\\inetpub\\wwwroot"
            )
            self.server_manager.CommitChanges()

        @staticmethod
        def get_existing_firewall_rules():
            """Get existing firewall rules for HTTP/HTTPS ports"""
            try:
                result = subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        'Get-NetFirewallRule | Where-Object { $_.DisplayName -like "*EB-CLI-Test*" } | Select-Object -Property DisplayName | ConvertTo-Json',
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                if result.stdout.strip():
                    try:
                        return json.loads(result.stdout)
                    except json.JSONDecodeError:
                        return []
                return []
            except subprocess.CalledProcessError:
                return []

        def create_test_firewall_rules(self, http_port, https_port):
            """Create test firewall rules for HTTP and HTTPS ports"""
            try:
                # Create HTTP rule (Allow)
                subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        f'New-NetFirewallRule -DisplayName "EB-CLI-Test-HTTP" -Direction Inbound -Action Allow -Protocol TCP -LocalPort {http_port} -Enabled True',
                    ],
                    check=True,
                )

                # Create HTTPS rule (Block)
                subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        f'New-NetFirewallRule -DisplayName "EB-CLI-Test-HTTPS" -Direction Inbound -Action Block -Protocol TCP -LocalPort {https_port} -Enabled True',
                    ],
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                pytest.skip(f"Failed to create firewall rules: {e}")

        def cleanup_test_firewall_rules(self):
            """Remove test firewall rules"""
            try:
                subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        'Remove-NetFirewallRule -DisplayName "EB-CLI-Test-HTTP" -ErrorAction SilentlyContinue',
                    ]
                )

                subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        'Remove-NetFirewallRule -DisplayName "EB-CLI-Test-HTTPS" -ErrorAction SilentlyContinue',
                    ]
                )
            except Exception:
                pass

        @patch("ebcli.lib.elasticbeanstalk.get_application_names")
        @patch("ebcli.lib.elasticbeanstalk.create_application_version")
        @patch("ebcli.controllers.migrate.get_unique_environment_name")
        @patch("ebcli.controllers.migrate.establish_platform")
        @patch("ebcli.controllers.migrate.test_environment_exists")
        @patch("ebcli.lib.ec2.get_instance_metadata")
        def test_migrate_single_default_web_site(
            self,
            mock_get_metadata,
            mock_test_environment_exists,
            mock_establish_platform,
            mock_get_unique_environment_name,
            mock_create_version,
            mock_get_apps,
        ):
            """
            Test basic migration of Default Web Site with default settings.
            """
            from ebcli.core.ebcore import EB

            # Setup mock responses
            mock_get_apps.return_value = []
            mock_create_version.return_value = "v1"
            mock_get_metadata.side_effect = NotAnEC2Instance
            mock_get_unique_environment_name.return_value = ["EBMigratedApp"]
            mock_establish_platform.return_value = "arn:aws:elasticbeanstalk:us-west-2::platform/.NET 6 running on 64bit Amazon Linux 2023/3.4.0"
            mock_test_environment_exists.side_effect = NotFoundError

            # Create and run EB CLI app
            app = EB(argv=["migrate", "--archive-only"])
            app.setup()
            app.run()

            # Verify source bundle was created
            migrations_dir = Path(".") / "migrations" / "latest"
            assert migrations_dir.exists()

            upload_target_dir = migrations_dir / "upload_target"
            assert upload_target_dir.exists()

            # Verify manifest was created and has correct structure
            manifest_path = upload_target_dir / "aws-windows-deployment-manifest.json"
            assert manifest_path.exists()

            with open(manifest_path) as f:
                manifest = json.load(f)
                assert manifest["manifestVersion"] == 1
                assert "msDeploy" in manifest["deployments"]

                # Verify Default Web Site deployment configuration
                ms_deploy_sections = manifest["deployments"]["msDeploy"]
                assert any(
                    section["name"] == "Default Web Site"
                    for section in ms_deploy_sections
                )

        @patch("ebcli.lib.elasticbeanstalk.get_application_names")
        @patch("ebcli.lib.elasticbeanstalk.create_application_version")
        @patch("ebcli.controllers.migrate.get_unique_environment_name")
        @patch("ebcli.controllers.migrate.establish_platform")
        @patch("ebcli.controllers.migrate.test_environment_exists")
        @patch("ebcli.lib.ec2.get_instance_metadata")
        def test_migrate_single_custom_site(
            self,
            mock_get_metadata,
            mock_test_environment_exists,
            mock_establish_platform,
            mock_get_unique_environment_name,
            mock_create_version,
            mock_get_apps,
        ):
            """
            Test migration of a custom site running on port 8080.
            """
            from ebcli.core.ebcore import EB

            # Remove Default Web Site and create custom site on port 8080
            server_manager = ServerManager()
            default_site = server_manager.Sites[
                "Default Web Site"
            ]  # Get fresh reference
            server_manager.Sites.Remove(default_site)
            custom_site = server_manager.Sites.Add(
                "Custom Site", "http", "*:8080:", "c:\\inetpub\\customsite"
            )
            server_manager.CommitChanges()

            # Setup mock responses
            mock_get_apps.return_value = []
            mock_create_version.return_value = "v1"
            mock_get_metadata.side_effect = NotAnEC2Instance
            mock_get_unique_environment_name.return_value = ["CustomSite"]
            mock_establish_platform.return_value = "arn:aws:elasticbeanstalk:us-west-2::platform/.NET 6 running on 64bit Amazon Linux 2023/3.4.0"
            mock_test_environment_exists.side_effect = NotFoundError

            # Create and run EB CLI app with specific site name
            app = EB(argv=["migrate", "--archive-only", "--sites", "Custom Site"])
            app.setup()
            app.run()

            # Verify source bundle was created
            migrations_dir = Path(".") / "migrations" / "latest"
            assert migrations_dir.exists()

            upload_target_dir = migrations_dir / "upload_target"
            assert upload_target_dir.exists()

            # Verify manifest was created and has correct structure
            manifest_path = upload_target_dir / "aws-windows-deployment-manifest.json"
            assert manifest_path.exists()

            with open(manifest_path) as f:
                manifest = json.load(f)
                assert manifest["manifestVersion"] == 1
                assert "custom" in manifest["deployments"]

                # Verify Custom Site deployment configuration
                custom_sections = manifest["deployments"]["custom"]
                assert any(
                    section["name"] == "Custom Site" for section in custom_sections
                )

                # Verify installation script exists
                install_script_path = None
                for section in custom_sections:
                    if section["name"] == "Custom Site":
                        install_script_path = section["scripts"]["install"]["file"]
                        break

                assert install_script_path is not None
                full_script_path = upload_target_dir / install_script_path
                assert full_script_path.exists()

                # Verify port 8080 is configured in the installation script
                with open(full_script_path) as script_file:
                    script_content = script_file.read()
                    assert "*:8080:" in script_content

        @classmethod
        def backup_state(cls):
            """Persist current IIS state including ARR proxy configuration"""
            server_manager = ServerManager()

            # Get ARR configuration sections
            config = server_manager.GetApplicationHostConfiguration()
            arr_sections = {
                "proxy": "system.webServer/proxy",
                "rewrite": "system.webServer/rewrite",
                "caching": "system.webServer/caching",
            }

            arr_config = {}
            for section_name, section_path in arr_sections.items():
                try:
                    section = config.GetSection(section_path)
                    if section:
                        arr_config[section_name] = {}
                        for attr in section.Attributes:
                            if not attr.IsInheritedFromDefaultValue:
                                # Handle TimeSpan values specially
                                if attr.Value.__class__.__name__.endswith("TimeSpan"):
                                    arr_config[section_name][
                                        attr.Name
                                    ] = attr.Value.TotalSeconds
                                else:
                                    arr_config[section_name][attr.Name] = attr.Value
                except Exception as e:
                    print(f"Warning: Could not backup ARR section {section_name}: {e}")

            state = {
                "arr_config": arr_config,
                "sites": [
                    {
                        "name": site.Name,
                        "bindings": [b.BindingInformation for b in site.Bindings],
                        "applications": [
                            {
                                "path": app.Path,
                                "pool": app.ApplicationPoolName,
                                "vdirs": [
                                    {
                                        "path": vdir.Path,
                                        "physical_path": vdir.PhysicalPath,
                                    }
                                    for vdir in app.VirtualDirectories
                                ],
                            }
                            for app in site.Applications
                        ],
                    }
                    for site in server_manager.Sites
                ],
            }

            with open(cls.state_file, "w") as f:
                json.dump(state, f, indent=2)

        @classmethod
        def restore_state(cls):
            """Restore IIS state including ARR configuration"""
            server_manager = ServerManager()

            if not cls.state_file.exists():
                return

            with open(cls.state_file, "r") as f:
                state = json.load(f)

            # Restore ARR configuration first
            if "arr_config" in state:
                config = server_manager.GetApplicationHostConfiguration()
                for section_name, attributes in state["arr_config"].items():
                    section_path = f"system.webServer/{section_name}"
                    try:
                        section = config.GetSection(section_path)
                        if section:
                            for attr_name, attr_value in attributes.items():
                                # If this is a timeout attribute, convert seconds back to TimeSpan
                                if attr_name == "timeout":
                                    from System import TimeSpan

                                    attr_value = TimeSpan.FromSeconds(attr_value)
                                section.SetAttributeValue(attr_name, attr_value)
                    except Exception as e:
                        print(
                            f"Warning: Could not restore ARR section {section_name}: {e}"
                        )

                # Remove all current sites except those in saved state
                saved_site_names = {site["name"] for site in state["sites"]}
                for site in list(server_manager.Sites):
                    if site.Name not in saved_site_names:
                        server_manager.Sites.Remove(site)

                # Restore sites from saved state
                for site_state in state["sites"]:
                    site = server_manager.Sites.Add(
                        site_state["name"], "http", "*:80:", "c:\\inetpub\\wwwroot"
                    )

                    # Clear default binding
                    site.Bindings.Clear()

                    # Restore bindings
                    for binding in site_state["bindings"]:
                        site.Bindings.Add(binding, "http")

                    # Restore applications and virtual directories
                    for app_state in site_state["applications"]:
                        if app_state["path"] != "/":  # Root app already exists
                            app = site.Applications.Add(
                                app_state["path"],
                                app_state["vdirs"][0]["physical_path"],
                            )
                            app.ApplicationPoolName = app_state["pool"]

                        # Add additional virtual directories
                        app = site.Applications[app_state["path"]]
                        for vdir_state in app_state["vdirs"][1:]:
                            app.VirtualDirectories.Add(
                                vdir_state["path"], vdir_state["physical_path"]
                            )

                server_manager.CommitChanges()

        @patch("ebcli.lib.elasticbeanstalk.get_application_names")
        @patch("ebcli.lib.elasticbeanstalk.create_application_version")
        @patch("ebcli.controllers.migrate.get_unique_environment_name")
        @patch("ebcli.controllers.migrate.establish_platform")
        @patch("ebcli.controllers.migrate.test_environment_exists")
        @patch("ebcli.lib.ec2.get_instance_metadata")
        def test_migrate_multiple_sites(
            self,
            mock_get_metadata,
            mock_test_environment_exists,
            mock_establish_platform,
            mock_get_unique_environment_name,
            mock_create_version,
            mock_get_apps,
        ):
            """
            Test migration of multiple custom sites running on different ports.
            """
            from ebcli.core.ebcore import EB

            # Remove Default Web Site and create multiple custom sites on different ports
            server_manager = ServerManager()
            default_site = server_manager.Sites[
                "Default Web Site"
            ]  # Get fresh reference
            server_manager.Sites.Remove(default_site)

            # Create first custom site on port 8080
            custom_site1 = server_manager.Sites.Add(
                "Custom Site 1", "http", "*:8080:", "c:\\inetpub\\customsite1"
            )

            # Create second custom site on port 8082
            custom_site2 = server_manager.Sites.Add(
                "Custom Site 2", "http", "*:8082:", "c:\\inetpub\\customsite2"
            )

            server_manager.CommitChanges()

            # Setup mock responses
            mock_get_apps.return_value = []
            mock_create_version.return_value = "v1"
            mock_get_metadata.side_effect = NotAnEC2Instance
            mock_get_unique_environment_name.return_value = ["MultiSiteEnv"]
            mock_establish_platform.return_value = "arn:aws:elasticbeanstalk:us-west-2::platform/.NET 6 running on 64bit Amazon Linux 2023/3.4.0"
            mock_test_environment_exists.side_effect = NotFoundError

            # Create and run EB CLI app with multiple site names
            app = EB(
                argv=[
                    "migrate",
                    "--archive-only",
                    "--sites",
                    "Custom Site 1,Custom Site 2",
                ]
            )
            app.setup()
            app.run()

            # Verify source bundle was created
            migrations_dir = Path(".") / "migrations" / "latest"
            assert migrations_dir.exists()

            upload_target_dir = migrations_dir / "upload_target"
            assert upload_target_dir.exists()

            # Verify manifest was created and has correct structure
            manifest_path = upload_target_dir / "aws-windows-deployment-manifest.json"
            assert manifest_path.exists()

            with open(manifest_path) as f:
                manifest = json.load(f)
                assert manifest["manifestVersion"] == 1
                assert "custom" in manifest["deployments"]

                # Verify both custom sites are in the deployment configuration
                custom_sections = manifest["deployments"]["custom"]

                # Check for Custom Site 1
                site1_section = next(
                    (
                        section
                        for section in custom_sections
                        if section["name"] == "Custom Site 1"
                    ),
                    None,
                )
                assert site1_section is not None

                # Check for Custom Site 2
                site2_section = next(
                    (
                        section
                        for section in custom_sections
                        if section["name"] == "Custom Site 2"
                    ),
                    None,
                )
                assert site2_section is not None

                # Verify installation scripts exist and contain correct port bindings
                # For Custom Site 1
                install_script_path1 = site1_section["scripts"]["install"]["file"]
                full_script_path1 = upload_target_dir / install_script_path1
                assert full_script_path1.exists()

                with open(full_script_path1) as script_file:
                    script_content = script_file.read()
                    assert "*:8080:" in script_content

                # For Custom Site 2
                install_script_path2 = site2_section["scripts"]["install"]["file"]
                full_script_path2 = upload_target_dir / install_script_path2
                assert full_script_path2.exists()

                with open(full_script_path2) as script_file:
                    script_content = script_file.read()
                    assert "*:8082:" in script_content

                # Verify that each site has its own installation script
                assert install_script_path1 != install_script_path2

                ms_deploy_section = manifest["deployments"]["msDeploy"]

                assert ms_deploy_section == []

        @patch("ebcli.lib.elasticbeanstalk.get_application_names")
        @patch("ebcli.lib.elasticbeanstalk.create_application_version")
        @patch("ebcli.controllers.migrate.get_unique_environment_name")
        @patch("ebcli.controllers.migrate.establish_platform")
        @patch("ebcli.controllers.migrate.test_environment_exists")
        @patch("ebcli.lib.ec2.get_instance_metadata")
        def test_migrate_site_with_multiple_applications(
            self,
            mock_get_metadata,
            mock_test_environment_exists,
            mock_establish_platform,
            mock_get_unique_environment_name,
            mock_create_version,
            mock_get_apps,
        ):
            """
            Test migration of Default Web Site with multiple applications.
            Ensures that the manifest contains correct references to Default Web Site
            and its additional application at "/application1".

            This test:
            1. Creates content in both application directories
            2. Runs the migration process
            3. Verifies the manifest structure
            4. Extracts and inspects the application bundles
            5. Checks for parameter files and archive.xml files
            """
            import zipfile
            import tempfile
            import shutil
            from ebcli.core.ebcore import EB

            # Setup Default Web Site with an additional application
            server_manager = ServerManager()
            default_site = server_manager.Sites[
                "Default Web Site"
            ]  # Get fresh reference

            # Get the physical path of the default web site
            default_physical_path = (
                default_site.Applications["/"].VirtualDirectories["/"].PhysicalPath
            )

            # Create content for the default web site
            with open(os.path.join(default_physical_path, "index.html"), "w") as f:
                f.write(
                    "<html><body><h1>Default Web Site Root</h1><p>This is the main application.</p></body></html>"
                )

            with open(os.path.join(default_physical_path, "web.config"), "w") as f:
                f.write(
                    """<?xml version="1.0" encoding="UTF-8"?>
    <configuration>
        <system.webServer>
            <defaultDocument>
                <files>
                    <add value="index.html" />
                </files>
            </defaultDocument>
        </system.webServer>
    </configuration>"""
                )

            # Create physical path for the additional application
            app_physical_path = "c:\\inetpub\\application1"
            os.makedirs(app_physical_path, exist_ok=True)

            # Create content for the additional application
            with open(os.path.join(app_physical_path, "index.html"), "w") as f:
                f.write(
                    "<html><body><h1>Application1</h1><p>This is the additional application.</p></body></html>"
                )

            with open(os.path.join(app_physical_path, "web.config"), "w") as f:
                f.write(
                    """<?xml version="1.0" encoding="UTF-8"?>
    <configuration>
        <system.webServer>
            <defaultDocument>
                <files>
                    <add value="index.html" />
                </files>
            </defaultDocument>
        </system.webServer>
    </configuration>"""
                )

            # Add an additional application to Default Web Site at "/application1"
            additional_app = default_site.Applications.Add(
                "/application1", app_physical_path
            )
            additional_app.ApplicationPoolName = "DefaultAppPool"
            server_manager.CommitChanges()

            # Setup mock responses
            mock_get_apps.return_value = []
            mock_create_version.return_value = "v1"
            mock_get_metadata.side_effect = NotAnEC2Instance
            mock_get_unique_environment_name.return_value = ["DefaultWebSiteWithApps"]
            mock_establish_platform.return_value = "arn:aws:elasticbeanstalk:us-west-2::platform/.NET 6 running on 64bit Amazon Linux 2023/3.4.0"
            mock_test_environment_exists.side_effect = NotFoundError

            # Create and run EB CLI app
            app = EB(argv=["migrate", "--archive-only"])
            app.setup()
            app.run()

            # Verify source bundle was created
            migrations_dir = Path(".") / "migrations" / "latest"
            assert migrations_dir.exists()

            upload_target_dir = migrations_dir / "upload_target"
            assert upload_target_dir.exists()

            # Verify manifest was created and has correct structure
            manifest_path = upload_target_dir / "aws-windows-deployment-manifest.json"
            assert manifest_path.exists()

            with open(manifest_path) as f:
                manifest = json.load(f)
                assert manifest["manifestVersion"] == 1
                assert "msDeploy" in manifest["deployments"]

                # Verify Default Web Site deployment configuration
                ms_deploy_sections = manifest["deployments"]["msDeploy"]

                # Check for root application (Default Web Site)
                default_site_section = next(
                    (
                        section
                        for section in ms_deploy_sections
                        if section["name"] == "Default Web Site"
                    ),
                    None,
                )
                assert default_site_section is not None
                assert default_site_section["parameters"]["iisPath"] == "/"
                assert (
                    default_site_section["parameters"]["iisWebSite"]
                    == "Default Web Site"
                )

                # Check for additional application (/application1)

                app1_section = [
                    section
                    for section in ms_deploy_sections
                    if section["name"] == "Default Web Site\\application1"
                ][0]

                assert app1_section["parameters"]["iisPath"] == "/application1"
                assert app1_section["parameters"]["iisWebSite"] == "Default Web Site"

                # Verify both application bundles exist
                default_site_bundle = (
                    upload_target_dir
                    / f"{default_site_section['parameters']['appBundle']}"
                )
                assert default_site_bundle.exists()

                app1_bundle = (
                    upload_target_dir / f"{app1_section['parameters']['appBundle']}"
                )
                assert app1_bundle.exists()

                # Extract and inspect the application bundles
                def extract_and_verify_bundle(bundle_path, expected_files):
                    temp_dir = tempfile.mkdtemp()
                    try:
                        with zipfile.ZipFile(bundle_path, "r") as zip_ref:
                            zip_ref.extractall(temp_dir)

                        # Check for expected files
                        for file_path in expected_files:
                            full_path = os.path.join(temp_dir, file_path)
                            assert os.path.exists(
                                full_path
                            ), f"Expected file {file_path} not found in bundle"

                        return temp_dir
                    except:
                        shutil.rmtree(temp_dir)
                        raise

                # Verify default site bundle contents
                default_site_temp_dir = extract_and_verify_bundle(
                    default_site_bundle,
                    ["archive.xml", "parameters.xml", "systemInfo.xml"],
                )

                # Verify application1 bundle contents
                app1_temp_dir = extract_and_verify_bundle(
                    app1_bundle, ["archive.xml", "parameters.xml", "systemInfo.xml"]
                )

                # Check for parameter files and verify their structure
                with open(
                    os.path.join(default_site_temp_dir, "parameters.xml"), "r"
                ) as f:
                    params_content = f.read()
                    assert "IIS Web Application Name" in params_content
                    assert "Default Web Site" in params_content

                with open(os.path.join(app1_temp_dir, "parameters.xml"), "r") as f:
                    params_content = f.read()
                    assert "IIS Web Application Name" in params_content
                    assert "Default Web Site\\application1" in params_content

                # Clean up temp directories
                shutil.rmtree(default_site_temp_dir)
                shutil.rmtree(app1_temp_dir)

        @patch("ebcli.lib.elasticbeanstalk.get_application_names")
        @patch("ebcli.lib.elasticbeanstalk.create_application_version")
        @patch("ebcli.controllers.migrate.get_unique_environment_name")
        @patch("ebcli.controllers.migrate.establish_platform")
        @patch("ebcli.controllers.migrate.test_environment_exists")
        @patch("ebcli.lib.ec2.get_instance_metadata")
        def test_migrate_site_with_multiple_applications_and_virtual_directories(
            self,
            mock_get_metadata,
            mock_test_environment_exists,
            mock_establish_platform,
            mock_get_unique_environment_name,
            mock_create_version,
            mock_get_apps,
        ):
            """
            Test migration of Default Web Site with multiple applications and virtual directories.

            This test:
            1. Creates Default Web Site with an additional application at "/application1"
            2. Adds virtual directories to both the Default Web Site ("/virtualdirectory1") and
               the application ("/virtualdirectory2")
            3. Runs the migration process
            4. Verifies the manifest contains correct references to all components
            """
            import zipfile
            import tempfile
            import shutil
            from ebcli.core.ebcore import EB

            # Setup Default Web Site with an additional application and virtual directories
            server_manager = ServerManager()
            default_site = server_manager.Sites[
                "Default Web Site"
            ]  # Get fresh reference

            # Get the physical path of the default web site
            default_physical_path = (
                default_site.Applications["/"].VirtualDirectories["/"].PhysicalPath
            )

            # Create content for the default web site
            with open(os.path.join(default_physical_path, "index.html"), "w") as f:
                f.write(
                    "<html><body><h1>Default Web Site Root</h1><p>This is the main application.</p></body></html>"
                )

            # Create physical path for the additional application
            app_physical_path = "c:\\inetpub\\application1"
            os.makedirs(app_physical_path, exist_ok=True)

            # Create content for the additional application
            with open(os.path.join(app_physical_path, "index.html"), "w") as f:
                f.write(
                    "<html><body><h1>Application1</h1><p>This is the additional application.</p></body></html>"
                )

            # Create physical paths for virtual directories
            vdir1_physical_path = "c:\\inetpub\\virtualdirectory1"
            vdir2_physical_path = "c:\\inetpub\\virtualdirectory2"
            os.makedirs(vdir1_physical_path, exist_ok=True)
            os.makedirs(vdir2_physical_path, exist_ok=True)

            # Create content for virtual directories
            with open(os.path.join(vdir1_physical_path, "index.html"), "w") as f:
                f.write(
                    "<html><body><h1>Virtual Directory 1</h1><p>This is virtual directory 1.</p></body></html>"
                )

            with open(os.path.join(vdir2_physical_path, "index.html"), "w") as f:
                f.write(
                    "<html><body><h1>Virtual Directory 2</h1><p>This is virtual directory 2.</p></body></html>"
                )

            # Add an additional application to Default Web Site at "/application1"
            additional_app = default_site.Applications.Add(
                "/application1", app_physical_path
            )
            additional_app.ApplicationPoolName = "DefaultAppPool"

            # Add virtual directory to Default Web Site
            default_site.Applications["/"].VirtualDirectories.Add(
                "/virtualdirectory1", vdir1_physical_path
            )

            # Add virtual directory to the additional application
            additional_app.VirtualDirectories.Add(
                "/virtualdirectory2", vdir2_physical_path
            )

            server_manager.CommitChanges()

            # Setup mock responses
            mock_get_apps.return_value = []
            mock_create_version.return_value = "v1"
            mock_get_metadata.side_effect = NotAnEC2Instance
            mock_get_unique_environment_name.return_value = ["DefaultWebSiteWithVDirs"]
            mock_establish_platform.return_value = "arn:aws:elasticbeanstalk:us-west-2::platform/.NET 6 running on 64bit Amazon Linux 2023/3.4.0"
            mock_test_environment_exists.side_effect = NotFoundError

            # Create and run EB CLI app
            app = EB(argv=["migrate", "--archive-only"])
            app.setup()
            app.run()

            # Verify source bundle was created
            migrations_dir = Path(".") / "migrations" / "latest"
            assert migrations_dir.exists()

            upload_target_dir = migrations_dir / "upload_target"
            assert upload_target_dir.exists()

            # Verify manifest was created and has correct structure
            manifest_path = upload_target_dir / "aws-windows-deployment-manifest.json"
            assert manifest_path.exists()

            with open(manifest_path) as f:
                manifest = json.load(f)
                assert manifest["manifestVersion"] == 1
                assert "msDeploy" in manifest["deployments"]
                assert "custom" in manifest["deployments"]

                # Verify Default Web Site deployment configuration
                ms_deploy_sections = manifest["deployments"]["msDeploy"]

                # Check for root application (Default Web Site) using list comprehension
                default_site_sections = [
                    section
                    for section in ms_deploy_sections
                    if section["name"] == "Default Web Site"
                ]
                assert len(default_site_sections) > 0
                default_site_section = default_site_sections[0]
                assert default_site_section["parameters"]["iisPath"] == "/"
                assert (
                    default_site_section["parameters"]["iisWebSite"]
                    == "Default Web Site"
                )

                # Check for additional application (/application1) using list comprehension
                app1_sections = [
                    section
                    for section in ms_deploy_sections
                    if section["name"] == "Default Web Site\\application1"
                ]
                assert len(app1_sections) > 0
                app1_section = app1_sections[0]
                assert app1_section["parameters"]["iisPath"] == "/application1"
                assert app1_section["parameters"]["iisWebSite"] == "Default Web Site"

                # Verify both application bundles exist
                default_site_bundle = (
                    upload_target_dir
                    / f"{default_site_section['parameters']['appBundle']}"
                )
                assert default_site_bundle.exists()

                app1_bundle = (
                    upload_target_dir / f"{app1_section['parameters']['appBundle']}"
                )
                assert app1_bundle.exists()

                # Verify virtual directory permission script exists using list comprehension
                custom_sections = manifest["deployments"]["custom"]
                vdir_permission_sections = [
                    section
                    for section in custom_sections
                    if section["name"] == "FixVirtualDirPermissions"
                ]
                assert len(vdir_permission_sections) > 0
                vdir_permission_section = vdir_permission_sections[0]

                # Verify the permission script file exists
                permission_script_path = vdir_permission_section["scripts"]["install"][
                    "file"
                ]
                full_script_path = upload_target_dir / permission_script_path
                assert full_script_path.exists()

                # Verify the permission script contains paths to both virtual directories
                with open(full_script_path) as script_file:
                    script_content = script_file.read()
                    assert vdir1_physical_path in script_content
                    assert vdir2_physical_path in script_content

                # Extract and inspect the application bundles to verify virtual directories are included
                def extract_and_verify_bundle(bundle_path, expected_files):
                    temp_dir = tempfile.mkdtemp()
                    try:
                        with zipfile.ZipFile(bundle_path, "r") as zip_ref:
                            zip_ref.extractall(temp_dir)

                        # Check for expected files
                        for file_path in expected_files:
                            full_path = os.path.join(temp_dir, file_path)
                            assert os.path.exists(
                                full_path
                            ), f"Expected file {file_path} not found in bundle"

                        return temp_dir
                    except:
                        shutil.rmtree(temp_dir)
                        raise

                # Verify default site bundle contains virtual directory configuration
                default_site_temp_dir = extract_and_verify_bundle(
                    default_site_bundle,
                    ["archive.xml", "parameters.xml", "systemInfo.xml"],
                )

                # Verify application1 bundle contains virtual directory configuration
                app1_temp_dir = extract_and_verify_bundle(
                    app1_bundle, ["archive.xml", "parameters.xml", "systemInfo.xml"]
                )

                # Clean up temp directories
                shutil.rmtree(default_site_temp_dir)
                shutil.rmtree(app1_temp_dir)

        @patch("ebcli.lib.elasticbeanstalk.get_application_names")
        @patch("ebcli.lib.elasticbeanstalk.create_application_version")
        @patch("ebcli.controllers.migrate.get_unique_environment_name")
        @patch("ebcli.controllers.migrate.establish_platform")
        @patch("ebcli.controllers.migrate.test_environment_exists")
        @patch("ebcli.lib.ec2.get_instance_metadata")
        @patch("ebcli.controllers.migrate.establish_instance_profile")
        @patch("ebcli.operations.createops.create_default_service_role")
        @patch("ebcli.controllers.migrate.get_unique_cname")
        @patch("ebcli.controllers.migrate.do_encrypt_ebs_volumes")
        @patch("ebcli.objects.requests.CreateEnvironmentRequest")
        @patch("ebcli.operations.createops.make_new_env")
        @patch(
            "ebcli.controllers.migrate.commonops.elasticbeanstalk.application_version_exists"
        )
        @patch(
            "ebcli.controllers.migrate.commonops.elasticbeanstalk.get_storage_location"
        )
        @patch("ebcli.controllers.migrate.commonops.s3.get_object_info")
        @patch("ebcli.controllers.migrate.commonops.s3.upload_application_version")
        def test_migrate_site_with_tags_passed_in_through_stdin(
            self,
            mock_upload_application_version,
            mock_get_object_info,
            mock_get_storage_location,
            mock_application_version_exists,
            mock_make_new_env,
            mock_create_env_request,
            mock_do_encrypt_ebs_volumes,
            mock_get_unique_cname,
            mock_create_service_role,
            mock_establish_instance_profile,
            mock_get_metadata,
            mock_test_environment_exists,
            mock_establish_platform,
            mock_get_unique_environment_name,
            mock_create_version,
            mock_get_apps,
        ):
            """
            Test migration of Default Web Site with tags parameter.

            This test:
            1. Ensures Default Web Site exists
            2. Invokes `eb migrate` with `--tags key1=val1,key2=val2`
            3. Verifies that create_app_version_and_environment is called with correct tags
            """
            from ebcli.core.ebcore import EB

            # Setup mock responses
            mock_create_env_request_object = MagicMock()
            mock_create_env_request.return_value = mock_create_env_request_object
            mock_get_apps.return_value = []
            mock_create_version.return_value = "v1"
            mock_establish_instance_profile.return_value = (
                "aws-elasticbeanstalk-ec2-role"
            )
            mock_create_service_role.return_value = "aws-elasticbeanstalk-service-role"
            mock_get_metadata.side_effect = NotAnEC2Instance
            mock_get_unique_environment_name.return_value = ["DefaultWebSiteWithTags"]
            mock_establish_platform.return_value = "arn:aws:elasticbeanstalk:us-west-2::platform/.NET 6 running on 64bit Amazon Linux 2023/3.4.0"
            mock_test_environment_exists.side_effect = NotFoundError
            mock_get_unique_cname.return_value = (
                "default-web-site-with-tags.elasticbeanstalk.com"
            )
            mock_application_version_exists.return_value = None
            mock_get_storage_location.return_value = "my-s3-bucket-location"
            mock_get_object_info.side_effect = NotFoundError

            # Define the tags we'll pass to the command
            tags = "key1=val1,key2=val2"
            expected_tags = [
                {"Key": "key1", "Value": "val1"},
                {"Key": "key2", "Value": "val2"},
            ]

            # Create and run EB CLI app with tags parameter
            app = EB(argv=["migrate", "--tags", tags])
            app.setup()
            app.run()

            # Verify CreateEnvironmentRequest was called with the correct tags
            call_kwargs = mock_create_env_request.call_args[1]
            assert call_kwargs["app_name"] == "DefaultWebSite"
            assert call_kwargs["env_name"] == ["DefaultWebSiteWithTags"]
            assert (
                call_kwargs["platform"]
                == "arn:aws:elasticbeanstalk:us-west-2::platform/.NET 6 running on 64bit Amazon Linux 2023/3.4.0"
            )
            assert call_kwargs["version_label"].startswith("app-")
            assert call_kwargs["instance_profile"] == "aws-elasticbeanstalk-ec2-role"
            assert call_kwargs["service_role"] == "aws-elasticbeanstalk-service-role"
            assert call_kwargs["key_name"] is None
            assert call_kwargs["tags"] == [
                {"Key": "key1", "Value": "val1"},
                {"Key": "key2", "Value": "val2"},
            ]
            assert call_kwargs["vpc"] == {}
            assert call_kwargs["elb_type"] == "application"
            assert call_kwargs["instance_types"] == "c5.2xlarge"
            assert call_kwargs["min_instances"] == "1"
            assert call_kwargs["max_instances"] == "4"
            assert call_kwargs["block_device_mappings"] == []
            assert call_kwargs["listener_configs"] == [
                {
                    "Namespace": "aws:elbv2:listener:default",
                    "OptionName": "Protocol",
                    "Value": "HTTP",
                },
                {
                    "Namespace": "aws:elbv2:listener:default",
                    "OptionName": "DefaultProcess",
                    "Value": "default",
                },
                {
                    "Namespace": "aws:elbv2:listener:default",
                    "OptionName": "ListenerEnabled",
                    "Value": "true",
                },
                {
                    "Namespace": "aws:elbv2:listener:default",
                    "OptionName": "Rules",
                    "Value": "rule1",
                },
                {
                    "Namespace": "aws:elbv2:listenerrule:rule1",
                    "OptionName": "Priority",
                    "Value": "1",
                },
                {
                    "Namespace": "aws:elbv2:listenerrule:rule1",
                    "OptionName": "Process",
                    "Value": "default",
                },
                {
                    "Namespace": "aws:elbv2:listenerrule:rule1",
                    "OptionName": "PathPatterns",
                    "Value": "*",
                },
                {
                    "Namespace": "aws:elasticbeanstalk:environment:process:default",
                    "OptionName": "Protocol",
                    "Value": "HTTP",
                },
                {
                    "Namespace": "aws:elasticbeanstalk:environment:process:default",
                    "OptionName": "Port",
                    "Value": "80",
                },
            ]
            assert (
                call_kwargs["cname"]
                == "default-web-site-with-tags.elasticbeanstalk.com"
            )
            assert call_kwargs["description"] == "Environment created by `eb migrate`"
            assert call_kwargs["load_balancer_security_group"] is None
            assert call_kwargs["ec2_security_group"] is None
            assert call_kwargs["root_volume"] == [
                {
                    "Namespace": "aws:autoscaling:launchconfiguration",
                    "OptionName": "RootVolumeSize",
                    "Value": "60",
                }
            ]

            mock_make_new_env.assert_called_once_with(
                mock_create_env_request_object, interactive=False, timeout=15
            )
            mock_do_encrypt_ebs_volumes.assert_not_called()
            call_args = mock_upload_application_version.call_args[0]
            assert call_args[0] == "my-s3-bucket-location"
            assert call_args[1].startswith("DefaultWebSite/app-")
            assert call_args[2] == os.path.join(
                os.getcwd(), "migrations", "latest", "upload_target.zip"
            )

            call_args, call_kwargs = mock_create_env_request.call_args
            assert (
                call_kwargs.get("tags") == expected_tags
            ), f"Tags parameter was not passed to CreateEnvironmentRequest, instead got: {call_kwargs.get('tags')}"

        @patch("ebcli.lib.elasticbeanstalk.get_application_names")
        @patch("ebcli.lib.elasticbeanstalk.create_application_version")
        @patch("ebcli.lib.ec2.establish_security_group")
        @patch("ebcli.controllers.migrate.construct_environment_vpc_config")
        @patch("ebcli.controllers.migrate.get_unique_environment_name")
        @patch("ebcli.controllers.migrate.establish_platform")
        @patch("ebcli.controllers.migrate.test_environment_exists")
        @patch("ebcli.controllers.migrate.establish_instance_profile")
        @patch("ebcli.operations.createops.create_default_service_role")
        @patch("ebcli.controllers.migrate.get_unique_cname")
        @patch("ebcli.controllers.migrate.do_encrypt_ebs_volumes")
        @patch("ebcli.objects.requests.CreateEnvironmentRequest")
        @patch("ebcli.operations.createops.make_new_env")
        @patch(
            "ebcli.controllers.migrate.commonops.elasticbeanstalk.application_version_exists"
        )
        @patch(
            "ebcli.controllers.migrate.commonops.elasticbeanstalk.get_storage_location"
        )
        @patch("ebcli.controllers.migrate.commonops.s3.get_object_info")
        @patch("ebcli.controllers.migrate.commonops.s3.upload_application_version")
        def test_migrate_site_with_default_tags_and_vpc_config(
            self,
            mock_upload_application_version,
            mock_get_object_info,
            mock_get_storage_location,
            mock_application_version_exists,
            mock_make_new_env,
            mock_create_env_request,
            mock_do_encrypt_ebs_volumes,
            mock_get_unique_cname,
            mock_create_service_role,
            mock_establish_instance_profile,
            mock_test_environment_exists,
            mock_establish_platform,
            mock_get_unique_environment_name,
            mock_construct_environment_vpc_config,
            mock_establish_security_group,
            mock_create_version,
            mock_get_apps,
        ):
            """
            Test migration of Default Web Site with tags parameter.

            This test:
            1. Ensures Default Web Site exists
            2. Invokes `eb migrate` with `--tags key1=val1,key2=val2`
            3. Verifies that create_app_version_and_environment is called with correct tags
            """
            from ebcli.core.ebcore import EB

            # Define the tags we'll pass to the command
            instance_tags = [
                {"Key": "instancetag1", "Value": "val1"},
                {"Key": "instancetag2", "Value": "val2"},
            ]

            # Setup mock responses
            mock_create_env_request_object = MagicMock()
            mock_create_env_request.return_value = mock_create_env_request_object
            mock_get_apps.return_value = []
            mock_create_version.return_value = "v1"
            mock_establish_instance_profile.return_value = (
                "aws-elasticbeanstalk-ec2-role"
            )
            mock_create_service_role.return_value = "aws-elasticbeanstalk-service-role"
            mock_construct_environment_vpc_config.return_value = (
                {"id": "vpc-id"},
                "us-west-2",
                "i-1234124adsf",
                instance_tags,
            )
            mock_establish_security_group.return_value = ("sg-lbsg", "sg-ec2sg")
            mock_get_unique_environment_name.return_value = ["DefaultWebSiteWithTags"]
            mock_establish_platform.return_value = "arn:aws:elasticbeanstalk:us-west-2::platform/.NET 6 running on 64bit Amazon Linux 2023/3.4.0"
            mock_test_environment_exists.side_effect = NotFoundError
            mock_get_unique_cname.return_value = (
                "default-web-site-with-tags.elasticbeanstalk.com"
            )
            mock_get_unique_cname.return_value = (
                "default-web-site-with-tags.elasticbeanstalk.com"
            )
            mock_application_version_exists.return_value = None
            mock_get_storage_location.return_value = "my-s3-bucket-location"
            mock_get_object_info.side_effect = NotFoundError

            # Create and run EB CLI app with tags parameter
            app = EB(argv=["migrate", "--encrypt-ebs-volume"])
            app.setup()
            app.run()

            # Verify CreateEnvironmentRequest was called with the correct parameters
            # Verify CreateEnvironmentRequest was called with the correct tags
            call_kwargs = mock_create_env_request.call_args[1]
            assert call_kwargs["app_name"] == "DefaultWebSite"
            assert call_kwargs["env_name"] == ["DefaultWebSiteWithTags"]
            assert (
                call_kwargs["platform"]
                == "arn:aws:elasticbeanstalk:us-west-2::platform/.NET 6 running on 64bit Amazon Linux 2023/3.4.0"
            )
            assert call_kwargs["version_label"].startswith("app-")
            assert call_kwargs["instance_profile"] == "aws-elasticbeanstalk-ec2-role"
            assert call_kwargs["service_role"] == "aws-elasticbeanstalk-service-role"
            assert call_kwargs["key_name"] is None
            assert call_kwargs["tags"] == instance_tags
            assert call_kwargs["vpc"] == {"id": "vpc-id"}
            assert call_kwargs["elb_type"] == "application"
            assert call_kwargs["instance_types"] == "c5.2xlarge"
            assert call_kwargs["min_instances"] == "1"
            assert call_kwargs["max_instances"] == "4"
            assert call_kwargs["block_device_mappings"] == []
            assert call_kwargs["listener_configs"] == [
                {
                    "Namespace": "aws:elbv2:listener:default",
                    "OptionName": "Protocol",
                    "Value": "HTTP",
                },
                {
                    "Namespace": "aws:elbv2:listener:default",
                    "OptionName": "DefaultProcess",
                    "Value": "default",
                },
                {
                    "Namespace": "aws:elbv2:listener:default",
                    "OptionName": "ListenerEnabled",
                    "Value": "true",
                },
                {
                    "Namespace": "aws:elbv2:listener:default",
                    "OptionName": "Rules",
                    "Value": "rule1",
                },
                {
                    "Namespace": "aws:elbv2:listenerrule:rule1",
                    "OptionName": "Priority",
                    "Value": "1",
                },
                {
                    "Namespace": "aws:elbv2:listenerrule:rule1",
                    "OptionName": "Process",
                    "Value": "default",
                },
                {
                    "Namespace": "aws:elbv2:listenerrule:rule1",
                    "OptionName": "PathPatterns",
                    "Value": "*",
                },
                {
                    "Namespace": "aws:elasticbeanstalk:environment:process:default",
                    "OptionName": "Protocol",
                    "Value": "HTTP",
                },
                {
                    "Namespace": "aws:elasticbeanstalk:environment:process:default",
                    "OptionName": "Port",
                    "Value": "80",
                },
            ]
            assert (
                call_kwargs["cname"]
                == "default-web-site-with-tags.elasticbeanstalk.com"
            )
            assert call_kwargs["description"] == "Environment created by `eb migrate`"
            assert call_kwargs["load_balancer_security_group"] is None
            assert call_kwargs["ec2_security_group"] is None
            assert call_kwargs["root_volume"] == [
                {
                    "Namespace": "aws:autoscaling:launchconfiguration",
                    "OptionName": "RootVolumeSize",
                    "Value": "60",
                }
            ]

            mock_make_new_env.assert_called_once_with(
                mock_create_env_request_object, interactive=False, timeout=15
            )
            mock_do_encrypt_ebs_volumes.assert_called_once_with()
            call_args = mock_upload_application_version.call_args[0]
            assert call_args[0] == "my-s3-bucket-location"
            assert call_args[1].startswith("DefaultWebSite/app-")
            assert call_args[2] == os.path.join(
                os.getcwd(), "migrations", "latest", "upload_target.zip"
            )

        @patch("ebcli.lib.elasticbeanstalk.get_application_names")
        @patch("ebcli.lib.elasticbeanstalk.create_application_version")
        @patch("ebcli.controllers.migrate.get_unique_environment_name")
        @patch("ebcli.controllers.migrate.establish_platform")
        @patch("ebcli.controllers.migrate.test_environment_exists")
        @patch("ebcli.lib.ec2.get_instance_metadata")
        def test_migrate_site_with_special_firewall_rules__not_copied_over_unless_referenced_in_bindings(
            self,
            mock_get_metadata,
            mock_test_environment_exists,
            mock_establish_platform,
            mock_get_unique_environment_name,
            mock_create_version,
            mock_get_apps,
        ):
            """
            Test migration with firewall configuration copying.

            This test verifies that when --copy-firewall-config is passed to eb migrate:
            1. It looks up firewall configuration on the current machine
            2. It generates a firewall config PS1 script
            3. It references the script in the manifest file
            """
            from ebcli.core.ebcore import EB

            try:
                http_port = 8080
                https_port = 8443
                self.create_test_firewall_rules(http_port, https_port)
                # Setup Default Web Site with an additional application
                server_manager = ServerManager()
                default_site = server_manager.Sites[
                    "Default Web Site"
                ]  # Get fresh reference

                # Get the physical path of the default web site
                default_physical_path = (
                    default_site.Applications["/"].VirtualDirectories["/"].PhysicalPath
                )

                # Create content for the default web site
                with open(os.path.join(default_physical_path, "index.html"), "w") as f:
                    f.write("<html><body><h1>Default Web Site Root</h1></body></html>")

                # Create physical path for the additional application
                app_physical_path = "c:\\inetpub\\application1"
                os.makedirs(app_physical_path, exist_ok=True)

                # Create content for the additional application
                with open(os.path.join(app_physical_path, "index.html"), "w") as f:
                    f.write("<html><body><h1>Application1</h1></body></html>")

                # Add an additional application to Default Web Site at "/application1"
                additional_app = default_site.Applications.Add(
                    "/application1", app_physical_path
                )
                additional_app.ApplicationPoolName = "DefaultAppPool"
                server_manager.CommitChanges()

                # Setup mock responses
                mock_create_env_request_object = MagicMock()
                mock_get_apps.return_value = []
                mock_create_version.return_value = "v1"
                mock_get_metadata.side_effect = NotAnEC2Instance
                mock_get_unique_environment_name.return_value = [
                    "DefaultWebSiteWithFirewall"
                ]
                mock_establish_platform.return_value = "arn:aws:elasticbeanstalk:us-west-2::platform/.NET 6 running on 64bit Amazon Linux 2023/3.4.0"
                mock_test_environment_exists.side_effect = NotFoundError

                # Create and run EB CLI app with copy-firewall-config flag
                app = EB(argv=["migrate", "--archive-only", "--copy-firewall-config"])
                app.setup()
                app.run()

                # Verify source bundle was created
                migrations_dir = Path(".") / "migrations" / "latest"
                assert migrations_dir.exists()

                upload_target_dir = migrations_dir / "upload_target"
                assert upload_target_dir.exists()

                # Verify manifest was created and has correct structure
                manifest_path = (
                    upload_target_dir / "aws-windows-deployment-manifest.json"
                )
                assert manifest_path.exists()

                # Verify firewall config script was generated
                firewall_script_path = (
                    upload_target_dir
                    / "ebmigrateScripts"
                    / "modify_firewall_config.ps1"
                )
                assert firewall_script_path.exists()

                # Verify the firewall script contains the expected commands
                with open(firewall_script_path) as f:
                    script_content = f.read()
                    assert (
                        'New-NetFirewallRule -DisplayName "EB-CLI-Test-HTTP"'
                        not in script_content
                    )
                    assert (
                        'New-NetFirewallRule -DisplayName "EB-CLI-Test-HTTPS"'
                        not in script_content
                    )

                # Verify manifest references the firewall script
                with open(manifest_path) as f:
                    manifest = json.load(f)
                    assert manifest["manifestVersion"] == 1
                    assert "custom" in manifest["deployments"]

                    # Check for ModifyFirewallConfig section using list comprehension
                    firewall_sections = [
                        section
                        for section in manifest["deployments"]["custom"]
                        if section["name"] == "ModifyFirewallConfig"
                    ]
                    assert len(firewall_sections) > 0

                    firewall_section = firewall_sections[0]
                    assert (
                        firewall_section["scripts"]["install"]["file"]
                        == "ebmigrateScripts\\modify_firewall_config.ps1"
                    )
                    assert (
                        firewall_section["scripts"]["restart"]["file"]
                        == "ebmigrateScripts\\noop.ps1"
                    )
                    assert (
                        firewall_section["scripts"]["uninstall"]["file"]
                        == "ebmigrateScripts\\noop.ps1"
                    )
            finally:
                self.cleanup_test_firewall_rules()

        @patch("ebcli.lib.elasticbeanstalk.get_application_names")
        @patch("ebcli.lib.elasticbeanstalk.create_application_version")
        @patch("ebcli.controllers.migrate.get_unique_environment_name")
        @patch("ebcli.controllers.migrate.establish_platform")
        @patch("ebcli.controllers.migrate.test_environment_exists")
        @patch("ebcli.lib.ec2.get_instance_metadata")
        def test_migrate_site_with_special_firewall_rules(
            self,
            mock_get_metadata,
            mock_test_environment_exists,
            mock_establish_platform,
            mock_get_unique_environment_name,
            mock_create_version,
            mock_get_apps,
        ):
            """
            Test migration with firewall configuration copying.

            This test verifies that when --copy-firewall-config is passed to eb migrate:
            1. It looks up firewall configuration on the current machine
            2. It generates a firewall config PS1 script
            3. It references the script in the manifest file
            """
            from ebcli.core.ebcore import EB

            try:
                http_port = 8080
                https_port = 8443
                self.create_test_firewall_rules(http_port, https_port)
                # Setup Default Web Site with an additional application
                server_manager = ServerManager()
                default_site = server_manager.Sites[
                    "Default Web Site"
                ]  # Get fresh reference
                default_site.Bindings.Add("*:8080:", "http")
                default_site.Bindings.Add("*:8443:", "https")

                # Get the physical path of the default web site
                default_physical_path = (
                    default_site.Applications["/"].VirtualDirectories["/"].PhysicalPath
                )

                # Create content for the default web site
                with open(os.path.join(default_physical_path, "index.html"), "w") as f:
                    f.write("<html><body><h1>Default Web Site Root</h1></body></html>")

                # Create physical path for the additional application
                app_physical_path = "c:\\inetpub\\application1"
                os.makedirs(app_physical_path, exist_ok=True)

                # Create content for the additional application
                with open(os.path.join(app_physical_path, "index.html"), "w") as f:
                    f.write("<html><body><h1>Application1</h1></body></html>")

                # Add an additional application to Default Web Site at "/application1"
                additional_app = default_site.Applications.Add(
                    "/application1", app_physical_path
                )
                additional_app.ApplicationPoolName = "DefaultAppPool"
                server_manager.CommitChanges()

                # Setup mock responses
                mock_get_apps.return_value = []
                mock_create_version.return_value = "v1"
                mock_get_metadata.side_effect = NotAnEC2Instance
                mock_get_unique_environment_name.return_value = [
                    "DefaultWebSiteWithFirewall"
                ]
                mock_establish_platform.return_value = "arn:aws:elasticbeanstalk:us-west-2::platform/.NET 6 running on 64bit Amazon Linux 2023/3.4.0"
                mock_test_environment_exists.side_effect = NotFoundError

                # Create and run EB CLI app with copy-firewall-config flag
                app = EB(argv=["migrate", "--archive-only", "--copy-firewall-config"])
                app.setup()
                app.run()

                # Verify source bundle was created
                migrations_dir = Path(".") / "migrations" / "latest"
                assert migrations_dir.exists()

                upload_target_dir = migrations_dir / "upload_target"
                assert upload_target_dir.exists()

                # Verify manifest was created and has correct structure
                manifest_path = (
                    upload_target_dir / "aws-windows-deployment-manifest.json"
                )
                assert manifest_path.exists()

                # Verify firewall config script was generated
                firewall_script_path = (
                    upload_target_dir
                    / "ebmigrateScripts"
                    / "modify_firewall_config.ps1"
                )
                assert firewall_script_path.exists()

                # Verify the firewall script contains the expected commands
                with open(firewall_script_path) as f:
                    script_content = f.read()
                    assert (
                        'New-NetFirewallRule -DisplayName "EB-CLI-Test-HTTP"'
                        in script_content
                    )
                    assert (
                        'New-NetFirewallRule -DisplayName "EB-CLI-Test-HTTPS"'
                        in script_content
                    )
                    assert "-Action Allow" in script_content
                    assert "-Action Block" in script_content
                    assert "-Protocol TCP" in script_content
                    assert f"-LocalPort {http_port}" in script_content
                    assert f"-LocalPort {https_port}" in script_content

                # Verify manifest references the firewall script
                with open(manifest_path) as f:
                    manifest = json.load(f)
                    assert manifest["manifestVersion"] == 1
                    assert "custom" in manifest["deployments"]

                    # Check for ModifyFirewallConfig section using list comprehension
                    firewall_sections = [
                        section
                        for section in manifest["deployments"]["custom"]
                        if section["name"] == "ModifyFirewallConfig"
                    ]
                    assert len(firewall_sections) > 0

                    firewall_section = firewall_sections[0]
                    assert (
                        firewall_section["scripts"]["install"]["file"]
                        == "ebmigrateScripts\\modify_firewall_config.ps1"
                    )
                    assert (
                        firewall_section["scripts"]["restart"]["file"]
                        == "ebmigrateScripts\\noop.ps1"
                    )
                    assert (
                        firewall_section["scripts"]["uninstall"]["file"]
                        == "ebmigrateScripts\\noop.ps1"
                    )
            finally:
                self.cleanup_test_firewall_rules()

        @patch("ebcli.lib.elasticbeanstalk.get_application_names")
        @patch("ebcli.lib.elasticbeanstalk.create_application_version")
        @patch("ebcli.controllers.migrate.get_unique_environment_name")
        @patch("ebcli.controllers.migrate.establish_platform")
        @patch("ebcli.controllers.migrate.test_environment_exists")
        @patch("ebcli.lib.ec2.get_instance_metadata")
        @patch(
            "ebcli.controllers.migrate.MigrateController.create_app_version_and_environment"
        )
        def test_migrate_multiple_sites_with_listener_configs(
            self,
            mock_create_app_version_and_environment,
            mock_get_metadata,
            mock_test_environment_exists,
            mock_establish_platform,
            mock_get_unique_environment_name,
            mock_create_version,
            mock_get_apps,
        ):
            """
            Test migration of multiple sites with listener configurations.

            This test verifies:
            1. Creation of three HTTP sites: Admin (8080), Reporting (8081), Payment (8082)
            2. Addition of HTTPS binding (8443) to Admin site
            3. Generation of listener configurations in listener_configs.json
            4. Proper process option settings for each site
            5. Correct listener rule configurations

            The test uses --copy-firewall-config flag but no --ssl-certificate-arn,
            so only HTTP listener configurations should be generated.
            """
            from ebcli.core.ebcore import EB

            # Save original ARR configuration
            server_manager = ServerManager()
            config = server_manager.GetApplicationHostConfiguration()
            original_arr_config = None
            original_arr_enabled = False

            http_ports = [8080, 8081, 8082]
            https_port = 8443
            try:
                self.get_and_save_original_arr_config(config)

                # Explicitly disable ARR
                try:
                    proxy_section = config.GetSection("system.webServer/proxy")
                    if proxy_section is not None:
                        proxy_section.SetAttributeValue("enabled", False)
                        server_manager.CommitChanges()
                        print("ARR proxy has been disabled for this test")
                    else:
                        print("ARR proxy section not found in configuration")
                except Exception as e:
                    print(f"Warning: Could not disable ARR: {e}")

                # Setup firewall rules for our test ports
                for port in http_ports:
                    self.create_test_firewall_rules(port, https_port)

                # Remove Default Web Site and create multiple custom sites
                server_manager = ServerManager()
                default_site = server_manager.Sites[
                    "Default Web Site"
                ]  # Get fresh reference
                server_manager.Sites.Remove(default_site)

                # Create Admin site on port 8080 with HTTPS on 8443
                admin_site = server_manager.Sites.Add(
                    "Admin", "http", "*:8080:", "c:\\inetpub\\admin"
                )
                # Add HTTPS binding to Admin site
                admin_site.Bindings.Add("*:8443:", "https")

                # Create Reporting site on port 8081
                reporting_site = server_manager.Sites.Add(
                    "Reporting", "http", "*:8081:", "c:\\inetpub\\reporting"
                )

                # Create Payment site on port 8082
                payment_site = server_manager.Sites.Add(
                    "Payment", "http", "*:8082:", "c:\\inetpub\\payment"
                )

                server_manager.CommitChanges()

                # Setup mock responses
                mock_get_apps.return_value = []
                mock_create_version.return_value = "v1"
                mock_get_metadata.side_effect = NotAnEC2Instance
                mock_get_unique_environment_name.return_value = ["MultiSiteListenerEnv"]
                mock_establish_platform.return_value = "arn:aws:elasticbeanstalk:us-west-2::platform/.NET 6 running on 64bit Amazon Linux 2023/3.4.0"
                mock_test_environment_exists.side_effect = NotFoundError

                # Create and run EB CLI app with copy-firewall-config flag but no SSL certificate
                app = EB(argv=["migrate", "--copy-firewall-config"])
                app.setup()
                app.run()

                # Verify source bundle was created
                migrations_dir = Path(".") / "migrations" / "latest"
                assert migrations_dir.exists()

                # Verify listener_configs.json was created
                listener_configs_path = migrations_dir / "listener_configs.json"
                assert listener_configs_path.exists()

                # Load and verify listener configurations
                with open(listener_configs_path) as f:
                    listener_configs = json.load(f)
                    listener_configs = [
                        OptionSetting(option_setting)
                        for option_setting in listener_configs["listener_configs"]
                    ]
                    expected_listener_configs = [
                        {
                            "Namespace": "aws:elbv2:listener:default",
                            "OptionName": "Protocol",
                            "Value": "HTTP",
                        },
                        {
                            "Namespace": "aws:elbv2:listener:default",
                            "OptionName": "DefaultProcess",
                            "Value": "8080",
                        },
                        {
                            "Namespace": "aws:elbv2:listener:default",
                            "OptionName": "ListenerEnabled",
                            "Value": "true",
                        },
                        {
                            "Namespace": "aws:elbv2:listener:default",
                            "OptionName": "Rules",
                            "Value": "rule1,rule3,rule4",
                        },
                        {
                            "Namespace": "aws:elbv2:listenerrule:rule1",
                            "OptionName": "Priority",
                            "Value": "1",
                        },
                        {
                            "Namespace": "aws:elbv2:listenerrule:rule1",
                            "OptionName": "Process",
                            "Value": "8080",
                        },
                        {
                            "Namespace": "aws:elbv2:listenerrule:rule1",
                            "OptionName": "PathPatterns",
                            "Value": "*",
                        },
                        {
                            "Namespace": "aws:elbv2:listenerrule:rule3",
                            "OptionName": "Priority",
                            "Value": "3",
                        },
                        {
                            "Namespace": "aws:elbv2:listenerrule:rule3",
                            "OptionName": "Process",
                            "Value": "8081",
                        },
                        {
                            "Namespace": "aws:elbv2:listenerrule:rule3",
                            "OptionName": "PathPatterns",
                            "Value": "*",
                        },
                        {
                            "Namespace": "aws:elbv2:listenerrule:rule4",
                            "OptionName": "Priority",
                            "Value": "4",
                        },
                        {
                            "Namespace": "aws:elbv2:listenerrule:rule4",
                            "OptionName": "Process",
                            "Value": "8082",
                        },
                        {
                            "Namespace": "aws:elbv2:listenerrule:rule4",
                            "OptionName": "PathPatterns",
                            "Value": "*",
                        },
                        {
                            "Namespace": "aws:elasticbeanstalk:environment:process:8080",
                            "OptionName": "Protocol",
                            "Value": "HTTP",
                        },
                        {
                            "Namespace": "aws:elasticbeanstalk:environment:process:8080",
                            "OptionName": "Port",
                            "Value": "8080",
                        },
                        {
                            "Namespace": "aws:elasticbeanstalk:environment:process:8081",
                            "OptionName": "Protocol",
                            "Value": "HTTP",
                        },
                        {
                            "Namespace": "aws:elasticbeanstalk:environment:process:8081",
                            "OptionName": "Port",
                            "Value": "8081",
                        },
                        {
                            "Namespace": "aws:elasticbeanstalk:environment:process:8082",
                            "OptionName": "Protocol",
                            "Value": "HTTP",
                        },
                        {
                            "Namespace": "aws:elasticbeanstalk:environment:process:8082",
                            "OptionName": "Port",
                            "Value": "8082",
                        },
                    ]
                    expected_listener_configs = [
                        OptionSetting(option_setting)
                        for option_setting in expected_listener_configs
                    ]
                    assert set(listener_configs) == set(expected_listener_configs)
            finally:
                self.cleanup_test_firewall_rules()
                self.revert_arr_config_changes(
                    original_arr_config, original_arr_enabled
                )

        @patch("ebcli.lib.elasticbeanstalk.get_application_names")
        @patch("ebcli.lib.elasticbeanstalk.create_application_version")
        @patch("ebcli.controllers.migrate.get_unique_environment_name")
        @patch("ebcli.controllers.migrate.establish_platform")
        @patch("ebcli.controllers.migrate.test_environment_exists")
        @patch("ebcli.lib.ec2.get_instance_metadata")
        @patch(
            "ebcli.controllers.migrate.MigrateController.create_app_version_and_environment"
        )
        @patch("ebcli.controllers.migrate._arr_enabled")
        def test_migrate_multiple_sites_with_arr_configuration(
            self,
            mock_arr_enabled,
            mock_create_app_version_and_environment,
            mock_get_metadata,
            mock_test_environment_exists,
            mock_establish_platform,
            mock_get_unique_environment_name,
            mock_create_version,
            mock_get_apps,
        ):
            """
            Test migration of multiple sites with ARR (Application Request Routing) configuration.

            This test verifies:
            1. Creation of three HTTP sites: Router (port 80), Reporting (port 8081), Admin (port 8082)
            2. Addition of HTTPS binding (port 8443) to Admin site
            3. Enabling of ARR (Application Request Routing) in IIS
            4. Generation of ARR configuration scripts in the deployment package
            5. Absence of listener configurations in listener_configs.json (since ARR is enabled)
            6. Proper manifest configuration for ARR-enabled sites

            The test uses --copy-firewall-config flag but since ARR is enabled,
            no listener configurations should be generated.
            """
            from ebcli.core.ebcore import EB

            # Save original ARR configuration
            server_manager = ServerManager()
            config = server_manager.GetApplicationHostConfiguration()
            original_arr_config = None
            original_arr_enabled = False

            # Mock ARR as enabled
            mock_arr_enabled.return_value = True

            try:
                self.get_and_save_original_arr_config(config)

                # Setup firewall rules for our test ports
                http_ports = [80, 8081, 8082]
                https_port = 8443
                for port in http_ports:
                    self.create_test_firewall_rules(port, https_port)

                # Remove Default Web Site and create multiple custom sites
                server_manager = ServerManager()
                default_site = server_manager.Sites[
                    "Default Web Site"
                ]  # Get fresh reference
                server_manager.Sites.Remove(default_site)

                # Create Router site on port 80
                router_site = server_manager.Sites.Add(
                    "Router", "http", "*:80:", "c:\\inetpub\\router"
                )
                # Add HTTPS binding to Admin site
                router_site.Bindings.Add("*:443:", "https")

                # Create Reporting site on port 8081
                reporting_site = server_manager.Sites.Add(
                    "Reporting", "http", "*:8081:", "c:\\inetpub\\reporting"
                )

                # Create Admin site on port 8082 with HTTPS on 8443
                admin_site = server_manager.Sites.Add(
                    "Admin", "http", "*:8082:", "c:\\inetpub\\admin"
                )

                server_manager.CommitChanges()

                # Setup mock responses
                mock_get_apps.return_value = []
                mock_create_version.return_value = "v1"
                mock_get_metadata.side_effect = NotAnEC2Instance
                mock_get_unique_environment_name.return_value = ["MultiSiteArrEnv"]
                mock_establish_platform.return_value = "arn:aws:elasticbeanstalk:us-west-2::platform/.NET 6 running on 64bit Amazon Linux 2023/3.4.0"
                mock_test_environment_exists.side_effect = NotFoundError

                # Create and run EB CLI app with copy-firewall-config flag
                app = EB(argv=["migrate"])
                app.setup()
                app.run()

                # Verify source bundle was created
                migrations_dir = Path(".") / "migrations" / "latest"
                assert migrations_dir.exists()

                upload_target_dir = migrations_dir / "upload_target"
                assert upload_target_dir.exists()

                # Verify listener_configs.json was NOT created (since ARR is enabled)
                listener_configs_path = migrations_dir / "listener_configs.json"
                assert not listener_configs_path.exists()

                # Verify manifest was created and has correct structure
                manifest_path = (
                    upload_target_dir / "aws-windows-deployment-manifest.json"
                )
                assert manifest_path.exists()

                with open(manifest_path) as f:
                    manifest = json.load(f)
                    assert manifest["manifestVersion"] == 1
                    assert "custom" in manifest["deployments"]

                    # Verify ARR configuration scripts exist
                    arr_msi_installer_path = (
                        upload_target_dir / "ebmigrateScripts" / "arr_msi_installer.ps1"
                    )
                    assert arr_msi_installer_path.exists()

                    arr_config_importer_path = (
                        upload_target_dir
                        / "ebmigrateScripts"
                        / "arr_configuration_importer_script.ps1"
                    )
                    assert arr_config_importer_path.exists()

                    windows_proxy_enabler_path = (
                        upload_target_dir
                        / "ebmigrateScripts"
                        / "windows_proxy_feature_enabler.ps1"
                    )
                    assert windows_proxy_enabler_path.exists()

                    # Verify ARR configuration sections in manifest
                    custom_sections = manifest["deployments"]["custom"]

                    # Check for WindowsProxyFeatureEnabler section
                    proxy_feature_sections = [
                        section
                        for section in custom_sections
                        if section["name"] == "WindowsProxyFeatureEnabler"
                    ]
                    assert len(proxy_feature_sections) > 0

                    # Check for ArrConfigurationImporterScript section
                    arr_config_sections = [
                        section
                        for section in custom_sections
                        if section["name"] == "ArrConfigurationImporterScript"
                    ]
                    assert len(arr_config_sections) > 0

                    # Verify site installation scripts exist for all three sites
                    router_install_script = None
                    reporting_install_script = None
                    admin_install_script = None

                    for section in custom_sections:
                        if section["name"] == "Router":
                            router_script_path = section["scripts"]["install"]["file"]
                            router_install_script = (
                                upload_target_dir / router_script_path
                            )
                        elif section["name"] == "Reporting":
                            reporting_script_path = section["scripts"]["install"][
                                "file"
                            ]
                            reporting_install_script = (
                                upload_target_dir / reporting_script_path
                            )
                        elif section["name"] == "Admin":
                            admin_script_path = section["scripts"]["install"]["file"]
                            admin_install_script = upload_target_dir / admin_script_path

                    assert (
                        router_install_script is not None
                        and router_install_script.exists()
                    )
                    assert (
                        reporting_install_script is not None
                        and reporting_install_script.exists()
                    )
                    assert (
                        admin_install_script is not None
                        and admin_install_script.exists()
                    )

                    # Verify ARR configuration in site installation scripts
                    with open(router_install_script) as f:
                        router_script = f.read()
                        assert "Invoke-ARRImportScript" in router_script
                        assert "*:80:" in router_script
                        assert "*:443:" in router_script

                    with open(reporting_install_script) as f:
                        reporting_script = f.read()
                        assert "*:8081:" in reporting_script

                    with open(admin_install_script) as f:
                        admin_script = f.read()
                        assert "*:8082:" in admin_script

                    # Verify firewall config script was generated
                    firewall_script_path = (
                        upload_target_dir
                        / "ebmigrateScripts"
                        / "modify_firewall_config.ps1"
                    )
                    assert not firewall_script_path.exists()

            finally:
                self.cleanup_test_firewall_rules()
                self.revert_arr_config_changes(
                    original_arr_config, original_arr_enabled
                )

        def tearDown(self):
            os.unlink(os.path.join("migrations", "latest"))
            shutil.rmtree(os.path.join("migrations"))

        @classmethod
        def tearDownClass(cls):
            """Cleanup that runs once after all tests in the class"""
            try:
                cls.restore_state()
            finally:
                if cls.state_file.exists():
                    cls.state_file.unlink()
                os.chdir(cls.original_dir)
                cls._delete_testDir_if_exists()

        @classmethod
        def _delete_testDir_if_exists(cls):
            if os.path.exists("testDir"):
                if sys.platform == "win32":
                    subprocess.run(["rd", "/s", "/q", "testDir"], shell=True)
                else:
                    shutil.rmtree("testDir")

        def revert_arr_config_changes(self, original_arr_config, original_arr_enabled):
            try:
                if original_arr_config is not None:
                    server_manager = ServerManager()
                    config = server_manager.GetApplicationHostConfiguration()
                    proxy_section = config.GetSection("system.webServer/proxy")

                    if proxy_section is not None:
                        # Restore enabled state
                        proxy_section.SetAttributeValue("enabled", original_arr_enabled)

                        # Restore other attributes
                        for attr_name, attr_value in original_arr_config.items():
                            # Handle TimeSpan values
                            if attr_name == "timeout":
                                from System import TimeSpan

                                attr_value = TimeSpan.FromSeconds(attr_value)
                            proxy_section.SetAttributeValue(attr_name, attr_value)

                        server_manager.CommitChanges()
                        print("Original ARR configuration has been restored")
            except Exception as e:
                print(f"Warning: Could not restore ARR configuration: {e}")

        def get_and_save_original_arr_config(self, config):
            # Get and save the original ARR proxy configuration
            try:
                proxy_section = config.GetSection("system.webServer/proxy")
                if proxy_section is not None:
                    original_arr_enabled = proxy_section.GetAttributeValue("enabled")
                    original_arr_config = {}
                    for attr in proxy_section.Attributes:
                        if not attr.IsInheritedFromDefaultValue:
                            # Handle TimeSpan values specially
                            if attr.Value.__class__.__name__.endswith("TimeSpan"):
                                original_arr_config[attr.Name] = attr.Value.TotalSeconds
                            else:
                                original_arr_config[attr.Name] = attr.Value
            except Exception as e:
                print(f"Warning: Could not backup ARR configuration: {e}")

    class OptionSetting:
        def __init__(self, option_setting_dict: typing.Dict[str, str]):
            self.namespace = option_setting_dict["Namespace"]
            self.value = option_setting_dict["Value"]
            self.option = option_setting_dict["OptionName"]

        def __hash__(self):
            return hash((self.namespace, self.value, self.option))

        def __eq__(self, other):
            return (
                self.namespace == other.namespace
                and self.value == other.value
                and self.option == other.option
            )

        def __lt__(self, other):
            return (
                self.namespace < other.namespace
                or self.value < other.value
                or self.option < other.option
            )

        def __repr__(self):
            return f"(Namespace: {self.namespace}, Value: {self.value}, OptionName: {self.option})"
