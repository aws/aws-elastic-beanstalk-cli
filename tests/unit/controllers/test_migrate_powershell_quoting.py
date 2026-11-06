# -*- coding: utf-8 -*-

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
import json
import re
import os
import shutil
import tempfile
import unittest
from collections import namedtuple

import mock

from ebcli.controllers import migrate


Binding = namedtuple("Binding", ["BindingInformation", "Protocol"])

# Contains a subexpression, a variable, a backtick, an ASCII apostrophe and a
# curly quote, all of which are live inside double-quoted PowerShell strings or
# terminate single-quoted ones.
SPECIAL = "a$(Write-Output MARKER)$name`b'c\u2019d"
SPECIAL_QUOTED = "'a$(Write-Output MARKER)$name`b''c\u2019\u2019d'"


class TestPowershellSingleQuote(unittest.TestCase):
    def test_all_single_quote_characters_are_doubled(self):
        for q in ("'", "\u2018", "\u2019", "\u201a", "\u201b"):
            self.assertEqual(
                "'x" + q + q + "y'", migrate._powershell_single_quote("x" + q + "y")
            )


class TestGeneratedScriptQuoting(unittest.TestCase):
    def setUp(self):
        self.upload_target_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.upload_target_dir, "ebmigrateScripts"))

    def tearDown(self):
        shutil.rmtree(self.upload_target_dir)

    def _read(self, name):
        with open(
            os.path.join(self.upload_target_dir, "ebmigrateScripts", name), "rb"
        ) as f:
            content = f.read()
        # Windows PowerShell 5.1 reads BOM-less files as ANSI, not UTF-8
        self.assertTrue(content.startswith(b"\xef\xbb\xbf"))
        # Text-mode writes use \r\n on Windows
        return content[3:].decode("utf-8").replace("\r\n", "\n")

    def _assert_installer_script(self, script):
        self.assertIn(f"$destination = {SPECIAL_QUOTED}\n", script)
        self.assertIn(
            f"$sourceZip = 'C:\\staging\\{SPECIAL_QUOTED[1:-1]}.zip'\n", script
        )
        self.assertIn(f"$websiteName = {SPECIAL_QUOTED}\n", script)
        self.assertIn(f"$appPoolName = {SPECIAL_QUOTED}\n", script)
        self.assertIn(f"{SPECIAL_QUOTED} = 'http'\n", script)
        self.assertIn(f"$acl = Get-Acl {SPECIAL_QUOTED}\n", script)
        self.assertIn(f"Set-Acl {SPECIAL_QUOTED} $acl\n", script)
        self.assertNotIn('"' + SPECIAL, script)
        self.assertNotIn("{site_name}", script)
        self.assertNotIn("{physical_path}", script)
        self.assertNotIn("{source_zip_path}", script)

    @mock.patch("ebcli.controllers.migrate._arr_enabled", return_value=False)
    def test_site_installer_script(self, _):
        migrate.write_custom_site_installer_script(
            self.upload_target_dir,
            SPECIAL,
            [Binding(SPECIAL, "HTTP")],
            SPECIAL,
            "install.ps1",
        )
        self._assert_installer_script(self._read("install.ps1"))

    @mock.patch("ebcli.controllers.migrate._arr_enabled_remote", return_value=False)
    def test_site_installer_script_remote(self, _):
        migrate.write_custom_site_installer_script_remote(
            mock.MagicMock(),
            self.upload_target_dir,
            SPECIAL,
            [Binding(SPECIAL, "HTTP")],
            SPECIAL,
            "install.ps1",
        )
        self._assert_installer_script(self._read("install.ps1"))

    @mock.patch("ebcli.controllers.migrate._arr_enabled", return_value=False)
    def test_site_installer_script_normal_values(self, _):
        migrate.write_custom_site_installer_script(
            self.upload_target_dir,
            "My Site",
            [Binding("*:8080:", "http"), Binding("*:443:example.com", "https")],
            "C:\\inetpub\\my site",
            "install.ps1",
        )
        script = self._read("install.ps1")
        self.assertIn("$destination = 'C:\\inetpub\\my site'\n", script)
        self.assertIn("$sourceZip = 'C:\\staging\\My Site.zip'\n", script)
        self.assertIn("$websiteName = 'My Site'\n", script)
        self.assertIn("'*:8080:' = 'http'\n'*:443:example.com' = 'https'\n", script)

    @mock.patch("ebcli.controllers.migrate._arr_enabled", return_value=False)
    def test_site_installer_value_containing_placeholder_is_not_expanded(self, _):
        migrate.write_custom_site_installer_script(
            self.upload_target_dir,
            "x{physical_path}",
            [Binding("*:80:", "http")],
            "C:\\p",
            "install.ps1",
        )
        self.assertIn("$websiteName = 'x{physical_path}'\n", self._read("install.ps1"))

    def test_site_removal_script(self):
        migrate.write_custom_site_removal_script(
            self.upload_target_dir, SPECIAL, "remove.ps1"
        )
        self.assertIn(f"$websiteName = {SPECIAL_QUOTED}\n", self._read("remove.ps1"))

    def test_site_restarter_script(self):
        migrate.write_custom_site_restarter_script(
            self.upload_target_dir, SPECIAL, "restart.ps1"
        )
        self.assertIn(f"$websiteName = {SPECIAL_QUOTED}\n", self._read("restart.ps1"))

    def test_default_web_site_port_reassignment_script(self):
        migrate.write_default_web_site_port_reassignment_script(
            self.upload_target_dir,
            Binding(f"{SPECIAL}:8080:{SPECIAL}", "http"),
            "reassign.ps1",
        )
        self.assertIn(
            "$bindingToUpdate.bindingInformation = "
            f"'{SPECIAL_QUOTED[1:-1]}:8080:{SPECIAL_QUOTED[1:-1]}'\n",
            self._read("reassign.ps1"),
        )

    def test_virtualdir_path_permission_script(self):
        migrate.create_virtualdir_path_permission_script(
            [SPECIAL], self.upload_target_dir
        )
        self.assertIn(
            f"$paths = @(\n    {SPECIAL_QUOTED}\n)",
            self._read("add_virtual_dir_read_access.ps1"),
        )

    @mock.patch("ebcli.controllers.migrate.get_firewall_rules")
    def test_copy_firewall_config_script(self, get_firewall_rules_mock):
        get_firewall_rules_mock.return_value = [
            {
                "Name": SPECIAL,
                "ServiceName": "",
                "Protocol": "TCP",
                "LocalPorts": "80,8000-8100",
                "Action": "Allow",
                "Enabled": False,
            }
        ]
        with open(
            os.path.join(self.upload_target_dir, "aws-windows-deployment-manifest.json"),
            "w",
        ) as f:
            json.dump({"deployments": {"custom": []}}, f)

        migrate.write_copy_firewall_config_script(
            self.upload_target_dir, [mock.MagicMock(Bindings=[Binding("*:80:", "http")])]
        )
        self.assertIn(
            f"New-NetFirewallRule -DisplayName {SPECIAL_QUOTED} "
            "-Direction Inbound -Action Allow -Protocol TCP "
            "-LocalPort '80','8000-8100' -Enabled False",
            self._read("modify_firewall_config.ps1"),
        )


class TestScriptFileNames(unittest.TestCase):
    # aws.deploytools runs custom scripts as & "<path>", so file names derived
    # from site names must not contain anything expanded inside double quotes
    SAFE_FILE_NAME = re.compile(r"\A(install|remove|restart)_site_[A-Za-z0-9_.-]+\.ps1\Z")

    def setUp(self):
        self.upload_target_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.upload_target_dir, "ebmigrateScripts"))
        # The migration computes paths relative to the working directory, which
        # fails on Windows when the temp directory is on another drive
        self.original_cwd = os.getcwd()
        os.chdir(self.upload_target_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.upload_target_dir)

    def test_normal_site_names_are_unchanged(self):
        for name, expected in [
            ("MySite", "MySite"),
            ("example.com", "example.com"),
            ("my-site_2", "my-site_2"),
        ]:
            self.assertEqual(expected, migrate._script_file_site_name(name))

    def test_unsafe_site_names_are_made_safe_without_colliding(self):
        self.assertNotEqual(
            migrate._script_file_site_name("My Site"),
            migrate._script_file_site_name("MySite"),
        )
        unsafe = ["My Site", "a$b", "a`b", 'a"b', "a\u201cb", "a\u201db", "a\u201eb", "a'b"]
        names = [migrate._script_file_site_name(n) for n in unsafe]
        for name in names:
            self.assertRegex(f"install_site_{name}.ps1", self.SAFE_FILE_NAME)
        self.assertEqual(len(unsafe), len(set(names)))

    def _site(self, name):
        virtual_directory = mock.MagicMock(Path="/", PhysicalPath="C:\\sites\\x")
        application = mock.MagicMock(
            Path="/", ApplicationPoolName="pool", VirtualDirectories=[virtual_directory]
        )
        site = mock.MagicMock(Bindings=[Binding("*:8080:", "http")])
        site.Name = name
        return site, application

    def _assert_script_files_are_safe(self, manifest_contents):
        scripts = manifest_contents["deployments"]["custom"][0]["scripts"]
        for script in scripts.values():
            file_name = script["file"].split("\\")[-1]
            self.assertRegex(file_name, self.SAFE_FILE_NAME)
            self.assertTrue(
                os.path.exists(
                    os.path.join(self.upload_target_dir, "ebmigrateScripts", file_name)
                )
            )

    @mock.patch("ebcli.controllers.migrate._arr_enabled", return_value=False)
    @mock.patch("ebcli.controllers.migrate.do_ms_deploy_sync_application")
    @mock.patch("ebcli.controllers.migrate.construct_ms_deploy_command_for_application")
    def test_ms_deploy_sync_application(self, *_):
        for name in ["a$(Write-Output MARKER)b", "x\u201dy"]:
            site, application = self._site(name)
            manifest_contents = {"deployments": {"msDeploy": [], "custom": []}}
            migrate.ms_deploy_sync_application(
                site, application, "dest", self.upload_target_dir, manifest_contents
            )
            self._assert_script_files_are_safe(manifest_contents)

    @mock.patch("ebcli.controllers.migrate._arr_enabled_remote", return_value=False)
    @mock.patch("ebcli.controllers.migrate.contains_iistart_htm_remote", return_value=False)
    @mock.patch("ebcli.controllers.migrate.do_ms_deploy_sync_application_remote")
    @mock.patch(
        "ebcli.controllers.migrate.construct_ms_deploy_command_for_application",
        return_value="-verb:sync",
    )
    def test_ms_deploy_sync_application_remote(self, *_):
        for name in ["a$(Write-Output MARKER)b", "x\u201dy"]:
            site, application = self._site(name)
            manifest_contents = {"deployments": {"msDeploy": [], "custom": []}}
            migrate.ms_deploy_sync_application_remote(
                mock.MagicMock(),
                site,
                application,
                "dest",
                "dest_remote",
                self.upload_target_dir,
                "C:\\upload",
                manifest_contents,
            )
            self._assert_script_files_are_safe(manifest_contents)
