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
import base64
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


class FakeRemoteConnection:
    """Records the PowerShell scripts that --remote mode runs on the source server."""

    def __init__(self, outputs=None):
        self.scripts = []
        self.outputs = list(outputs or [])

    def run(self, command, hide=True):
        match = re.fullmatch(
            r"powershell -NoProfile -NonInteractive -EncodedCommand (\S+)|"
            r"powershell -NonInteractive -EncodedCommand (\S+)",
            command,
        )
        assert match, command
        encoded = match.group(1) or match.group(2)
        self.scripts.append(base64.b64decode(encoded).decode("utf-16le"))
        stdout = self.outputs.pop(0) if self.outputs else ""
        return mock.MagicMock(stdout=stdout)

    def get(self, *args, **kwargs):
        pass


class TestRemoteSourceServerScriptQuoting(unittest.TestCase):
    def _assert_only_quoted(self, script):
        # SPECIAL contains an apostrophe, so it can only appear verbatim if it
        # was inserted without escaping
        self.assertNotIn(SPECIAL, script)

    def test_get_site_remote(self):
        connection = FakeRemoteConnection(
            [
                json.dumps(
                    {
                        "Name": SPECIAL,
                        "Attributes": [],
                        "Bindings": [],
                        "Applications": [],
                        "HSTS": {"Enabled": False, "MaxAge": None},
                    }
                )
            ]
        )
        migrate.get_site_remote(connection, SPECIAL)
        script = connection.scripts[0]
        self.assertIn(f"$siteName = {SPECIAL_QUOTED}\n", script)
        self.assertIn("Get-Item -LiteralPath $sitePSPath\n", script)
        self.assertIn("Get-WebBinding -Name $siteName\n", script)
        self.assertIn("Get-WebApplication -Site $siteName ", script)
        self.assertIn("site[@name=$siteXPath]", script)
        self._assert_only_quoted(script)

    def test_contains_iistart_htm_remote(self):
        connection = FakeRemoteConnection(["true"])
        self.assertTrue(migrate.contains_iistart_htm_remote(connection, SPECIAL))
        self.assertIn(
            f"Test-IISStartHtm -physicalPath {SPECIAL_QUOTED}\n", connection.scripts[0]
        )
        self._assert_only_quoted(connection.scripts[0])

    def test_create_migration_folders_remote(self):
        connection = FakeRemoteConnection()
        migrate.create_migration_folders_remote(
            connection, SPECIAL + "\\bundle", SPECIAL + "\\upload"
        )
        script = connection.scripts[0]
        self.assertIn(f"New-Item -Path '{SPECIAL_QUOTED[1:-1]}\\bundle' ", script)
        self.assertIn(f"New-Item -Path '{SPECIAL_QUOTED[1:-1]}\\upload' ", script)
        self._assert_only_quoted(script)

    def test_do_ms_deploy_sync_application_remote(self):
        connection = FakeRemoteConnection()
        migrate.do_ms_deploy_sync_application_remote(
            connection,
            "-verb:sync",
            SPECIAL + "\\dest",
            SPECIAL + "\\archive",
            SPECIAL + "\\upload",
            SPECIAL,
            "# msdeploy",
        )
        inner = SPECIAL_QUOTED[1:-1]
        create, _, archive = connection.scripts
        self.assertIn(f"-Path '{inner}\\dest' | Out-Null", create)
        self.assertIn(f"-Path '{inner}\\upload' | Out-Null", create)
        self.assertIn(
            f"$null | Out-File -LiteralPath '{inner}\\dest\\application.log'\n", create
        )
        self.assertIn(f"$null | Out-File -LiteralPath '{inner}\\dest\\error.log'\n", create)
        self.assertIn(
            f"-LiteralPath '{inner}\\dest\\application.log'\n", connection.scripts[1]
        )
        self.assertIn(
            f"$src='{inner}\\archive';$dst='{inner}\\upload\\{inner}.zip'\n", archive
        )
        for script in connection.scripts:
            self._assert_only_quoted(script)

    def test_construct_msdeploy_powershell_command(self):
        value = "a$(Write-Output MARKER)$name`b"
        command = migrate.construct_msdeploy_powershell_command(
            ["-verb:sync", "", f'-source:apphostconfig="{value}/"', "-x:'y'"]
        )
        self.assertIn(
            "$msdeployArgs = @(\n"
            "    '-verb:sync'\n"
            f"    '-source:apphostconfig=\"{value}/\"'\n"
            "    '-x:''y'''\n"
            ")\n",
            command,
        )

    def test_get_site_configs_remote(self):
        for physical_path, expected in [
            (SPECIAL, f"$path = '{SPECIAL_QUOTED[1:-1]}\\web.config'\n"),
            (
                "%SystemDrive%\\" + SPECIAL,
                f"$path = $env:SystemDrive + '\\{SPECIAL_QUOTED[1:-1]}\\web.config'\n",
            ),
        ]:
            connection = FakeRemoteConnection(["EXISTS", "<configuration/>"])
            virtual_directory = mock.MagicMock(Path="/", PhysicalPath=physical_path)
            application = mock.MagicMock(Path="/", VirtualDirectories=[virtual_directory])
            site = mock.MagicMock(
                Bindings=[Binding("*:80:", "http")], Applications=[application]
            )
            site.Name = "MySite"
            migrate.get_site_configs_remote(connection, [site])
            check, read = connection.scripts
            self.assertIn(expected, check)
            self.assertIn(
                f"Get-Content -LiteralPath '{SPECIAL_QUOTED[1:-1]}\\web.config' -Raw\n"
                if not physical_path.startswith("%")
                else f"Get-Content -LiteralPath '\\{SPECIAL_QUOTED[1:-1]}\\web.config' -Raw\n",
                read,
            )
            for script in connection.scripts:
                self._assert_only_quoted(script)

    def test_import_packaged_sites_from_remote(self):
        local_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, local_dir)
        connection = FakeRemoteConnection(["", "site" + SPECIAL.replace("'", ""), ""])
        migrate.import_packaged_sites_from_remote(connection, "C:\\runs\\1", local_dir)
        folder = "site" + SPECIAL.replace("'", "")
        self.assertEqual(3, len(connection.scripts))
        self.assertIn(
            "Get-ChildItem -LiteralPath 'C:\\runs\\1\\upload_target' -Filter *.zip",
            connection.scripts[0],
        )
        self.assertIn(
            "Get-ChildItem -LiteralPath 'C:\\runs\\1\\upload_target' -Directory",
            connection.scripts[1],
        )
        folder_path = migrate._powershell_single_quote(
            "C:\\runs\\1\\upload_target\\" + folder
        )
        self.assertIn(
            f"Get-ChildItem -LiteralPath {folder_path} -Filter *.zip",
            connection.scripts[2],
        )
        self.assertIn("$(Write-Output MARKER)", folder_path)


class TestMsDeployArguments(unittest.TestCase):
    ARCHIVE = "C:\\migrations\\upload_target\\My Site"

    def _site(self, name, path="/", pool="My Pool", hsts=False):
        application = mock.MagicMock(Path=path, ApplicationPoolName=pool)
        site = mock.MagicMock(HSTS=mock.MagicMock(Enabled=hsts))
        site.Name = name
        return site, application

    def _local(self, site, application, archive=ARCHIVE):
        return migrate.construct_ms_deploy_command_for_application(
            site, application, migrate.iis_application_name_value(site, application), archive
        )

    def _remote(self, site, application, archive=ARCHIVE):
        return migrate.ms_deploy_args_for_application(
            site,
            application,
            migrate.iis_application_name_value(site, application),
            archive,
            quote='"',
        )

    def test_local_arguments_for_normal_values(self):
        self.assertEqual(
            "-verb:sync "
            '-source:apphostconfig="My Site\\api" '
            "-dest:archiveDir='C:\\migrations\\upload_target\\My Site' "
            "-enableLink:AppPoolExtension "
            "-declareParam:name='Application Pool',defaultValue='My Pool',"
            "description='Application pool for application /api/',"
            "kind=DeploymentObjectAttribute,scope=appHostConfig,"
            "match='application/@applicationPool' "
            "-declareParam:name='IIS Web Application Name',defaultValue='My Site\\api' "
            '-skip:objectName=hsts,absolutePath="My Site" '
            "-enableRule:CopySecureContent",
            self._local(*self._site("My Site", "/api/")),
        )

    def test_remote_arguments_for_normal_values(self):
        self.assertEqual(
            [
                "-verb:sync",
                '-source:apphostconfig="My Site/"',
                '-dest:archiveDir="C:\\migrations\\upload_target\\My Site"',
                "-enableLink:AppPoolExtension",
                '-declareParam:name="Application Pool",defaultValue="My Pool",'
                'description="Application pool for application /",'
                "kind=DeploymentObjectAttribute,scope=appHostConfig,"
                'match="application/@applicationPool"',
                '-declareParam:name="IIS Web Application Name",defaultValue="My Site"',
                "",
                "-enableRule:CopySecureContent",
            ],
            self._remote(*self._site("My Site", hsts=True)),
        )

    def test_value_cannot_start_a_new_argument(self):
        args = self._remote(*self._site("a -postSync:runCommand=calc"))
        self.assertIn('-source:apphostconfig="a -postSync:runCommand=calc/"', args)
        self.assertFalse(any(arg.startswith("-postSync") for arg in args))

    def test_quote_characters_are_rejected(self):
        for quote in ("'", '"'):
            for site, application, archive in [
                self._site(f"a{quote}b") + (self.ARCHIVE,),
                self._site("a", path=f"/x{quote}y") + (self.ARCHIVE,),
                self._site("a", pool=f"p{quote}q") + (self.ARCHIVE,),
                self._site("a") + (f"C:\\x{quote}y",),
            ]:
                for build in (self._local, self._remote):
                    with self.assertRaises(migrate.NotSupportedError):
                        build(site, application, archive)
