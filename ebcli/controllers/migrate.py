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
import datetime
import shutil
import os
import string
import sys
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
import zipfile
from typing import Dict, List, Any, Union, Optional, Tuple, Set
import collections
import json
import argparse
from fabric import Connection
import base64

if sys.platform.startswith("win"):
    import winreg
    import clr
    import win32com.client

    clr.AddReference("System.Reflection")
    clr.AddReference(r"C:\Windows\System32\inetsrv\Microsoft.Web.Administration.dll")
    clr.AddReference("System")
    clr.AddReference("System.Core")
    clr.AddReference("System.DirectoryServices.AccountManagement")
    from System.DirectoryServices.AccountManagement import (
        PrincipalContext,
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
        ObjectState,
    )
    from System.Diagnostics import Process, ProcessStartInfo
    from System.Runtime.InteropServices import COMException

from cement.utils.misc import minimal_logger

LOG = minimal_logger(__name__)

from ebcli.core.abstractcontroller import AbstractBaseController
from ebcli.core import io, fileoperations
from ebcli.lib import utils, ec2, elasticbeanstalk, aws
from ebcli.objects import requests
from ebcli.objects.platform import PlatformVersion
from ebcli.objects.exceptions import (
    NotFoundError,
    NotAnEC2Instance,
    NotSupportedError,
)
from ebcli.resources.strings import prompts, flag_text
from ebcli.operations import commonops, createops, platformops, statusops
from ebcli.operations.tagops import tagops
from ebcli.resources.statics import namespaces


class MigrateExploreController(AbstractBaseController):
    class Meta:
        argument_formatter = argparse.RawTextHelpFormatter
        label = "explore"
        description = flag_text["migrate.explore"]
        usage = "eb migrate explore"
        stacked_on = "migrate"
        stacked_type = "nested"

    def do_command(self):
        if not sys.platform.startswith("win"):
            raise NotSupportedError("'eb migrate explore' is only supported on Windows")
        verbose = self.app.pargs.verbose

        if verbose:
            list_sites_verbosely()
        else:
            io.echo("\n".join([s.Name for s in ServerManager().Sites]))


class MigrateCleanupController(AbstractBaseController):
    class Meta:
        argument_formatter = argparse.RawTextHelpFormatter
        label = "cleanup"
        description = flag_text["migrate.cleanup"]
        usage = "eb migrate cleanup"
        stacked_on = "migrate"
        stacked_type = "nested"
        arguments = [
            (["--force"], dict(action="store_true", help=flag_text["migrate.force"])),
        ]

    def do_command(self):
        if not sys.platform.startswith("win"):
            raise NotSupportedError("'eb migrate cleanup' is only supported on Windows")
        force = self.app.pargs.force
        cleanup_previous_migration_artifacts(force, self.app.pargs.verbose)


# TODO: error when a physical path is in incidental to the migration execution path
class MigrateController(AbstractBaseController):
    class Meta:
        argument_formatter = argparse.RawTextHelpFormatter
        label = "migrate"
        description = "This command migrates an IIS site or application from a source Windows machine to an environment hosted on AWS Elastic Beanstalk."
        usage = "eb migrate [options ...]"
        arguments = [
            (["-s", "--sites"], dict(help=flag_text["migrate.sites"])),
            (
                ["-e", "--environment-name"],
                dict(help=flag_text["migrate.environment_name"]),
            ),
            (
                ["-a", "--application-name"],
                dict(help=flag_text["migrate.application_name"]),
            ),
            (["-p", "--platform"], dict(help=flag_text["migrate.platform"])),
            (["-i", "--instance-type"], dict(help=flag_text["migrate.instance_type"])),
            (["-c", "--cname"], dict(help=flag_text["migrate.cname"])),
            (
                ["-ip", "--instance-profile"],
                dict(help=flag_text["migrate.instance_profile"]),
            ),
            (["-sr", "--service-role"], dict(help=flag_text["migrate.service_role"])),
            (
                ["-es", "--ebs-snapshots"],
                dict(nargs="*", help=flag_text["migrate.ebs_snapshots"]),
            ),
            (
                ["-st", "--stream-to-cloudwatch"],
                dict(action="store_true", help=argparse.SUPPRESS),
            ),
            (
                ["-hc", "--use-host-ebs-configuration"],
                dict(action="store_true", help=argparse.SUPPRESS),
            ),
            (["-k", "--keyname"], dict(help=flag_text["migrate.keyname"])),
            (
                ["-in", "--interactive"],
                dict(action="store_true", help=flag_text["migrate.interactive"]),
            ),
            (["-t", "--tags"], dict(help=flag_text["migrate.tags"])),
            (["-d", "--copy-deps"], dict(action="store_true", help=argparse.SUPPRESS)),
            (
                ["-ao", "--archive-only"],
                dict(action="store_true", help=flag_text["migrate.archive_only"]),
            ),
            (
                ["-op", "--on-prem-mode"],
                dict(action="store_true", help=argparse.SUPPRESS),
            ),
            (
                ["-cf", "--copy-firewall-config"],
                dict(
                    action="store_true", help=flag_text["migrate.copy_firewall_config"]
                ),
            ),
            (
                ["--encrypt-ebs-volumes"],
                dict(
                    action="store_true", help=flag_text["migrate.encrypt_ebs_volumes"]
                ),
            ),
            (
                ["--ssl-certificates"],
                dict(help=flag_text["migrate.ssl_certificate_arns"]),
            ),
            (["--archive"], dict(help=flag_text["migrate.archive"])),
            (["-vpc", "--vpc-config"], dict(help=flag_text["migrate.vpc_config"])),

            (
                ["--remote"],
                dict(action="store_true", help="Enable remote execution mode for IIS site discovery"),
            ),
            (
                ["--target-ip"],
                dict(help="IP address of the remote machine for IIS site discovery"),
            ),
            (
                ["--username"],
                dict(help="Username for authentication on the remote machine"),
            ),
            (
                ["--password"],
                dict(help="Password for authentication on the remote machine"),
            ),
            # TODO: support userdata copy using robocopy
        ]

    def generate_ms_deploy_source_bundle(
        self,
        site: "Site",
        destination: str,
        verbose: bool,
        additional_virtual_dir_physical_paths: List[str] = [],
    ) -> None:
        """
        Generate deployment bundle and manifest for an IIS site and its components.

        Creates a structured directory containing deployment artifacts for an IIS site,
        including all its applications and virtual directories. Maintains a deployment
        manifest that describes how to deploy these components.

        Args:
            site: IIS Site object to package
            destination: Base directory for deployment artifacts
            verbose: If True, provides detailed output during generation
            additional_virtual_dir_physical_paths: List to collect physical paths of
                virtual directories for permission configuration

        Directory Structure:
            destination/
            ├── upload_target/
            │   ├── source1.zip                    # Application bundles
            │   ├── source2.zip
            │   ├── aws-windows-deployment-manifest.json
            │   └── ebmigrateScripts/             # Helper PowerShell scripts
            │       ├── site_installer.ps1
            │       ├── permission_handler.ps1
            │       └── other helper scripts
            └── upload_target.zip                  # Final package

        Process Flow:
            1. Creates upload_target and ebmigrateScripts directories
            2. Creates or updates deployment manifest
            3. For each application in site:
               - Checks for password protection
               - Generates MS Deploy package
               - Collects non-root virtual directory paths
            4. Updates manifest with final configuration

        Manifest Structure:
            {
                "manifestVersion": 1,
                "deployments": {
                    "msDeploy": [],    # Default Web Site deployments
                    "custom": []       # Custom site deployments
                }
            }

        Notes:
            - Creates directories with exist_ok=True
            - Collects virtual directory paths for later permission setup
            - Updates existing manifest if found, creates new if not
            - Uses indented JSON format for manifest readability
        """
        if verbose:
            io.echo(f"Generating source bundle for {site.Name}")
        upload_target_dir = os.path.join(destination, "upload_target")
        os.makedirs(upload_target_dir, exist_ok=True)
        os.makedirs(os.path.join(upload_target_dir, "ebmigrateScripts"), exist_ok=True)

        manifest_file_path = os.path.join(
            upload_target_dir, "aws-windows-deployment-manifest.json"
        )
        relative_normalized_manifest_path = absolute_to_relative_normalized_path(
            manifest_file_path
        )
        if os.path.exists(manifest_file_path):
            if verbose:
                io.echo(f"  Updating {relative_normalized_manifest_path}")
            with open(manifest_file_path) as file:
                manifest_contents = json.load(file)
        else:
            manifest_contents = {
                "manifestVersion": 1,
                "deployments": {"msDeploy": [], "custom": []},
            }
        for application in site.Applications:
            warn_about_password_protection(site, application)
            ms_deploy_sync_application(
                site, application, destination, upload_target_dir, manifest_contents
            )
            for vdir in application.VirtualDirectories:
                if vdir.Path != "/":
                    additional_virtual_dir_physical_paths.append(vdir.PhysicalPath)
        if verbose:
            io.echo(
                f"Updating manifest file for archive at {relative_normalized_manifest_path}"
            )
        with open(manifest_file_path, "w") as file:
            json.dump(manifest_contents, file, indent=4)

    def generate_ms_deploy_source_bundle_remote(
            self,
            remote_connection,
            site,
            destination,
            destination_remote,
            verbose,
            additional_virtual_dir_physical_paths=[]
    ):
        # destination
        # |- upload_target
        # |  |-- source1.zip
        # |  |-- source2.zip
        # |  |-- ...
        # |  |-- manifest.json
        # |  |-- <other util ps1 files>
        # |
        # |-- upload_target.zip
        if verbose:
            io.echo(f"Generating source bundle for {site.Name}")
        upload_target_dir = os.path.join(destination, 'upload_target')
        os.makedirs(upload_target_dir, exist_ok=True)
        os.makedirs(os.path.join(upload_target_dir, 'ebmigrateScripts'), exist_ok=True)

        bundle_dir_remote = windows_path_join(destination_remote, 'bundle')
        upload_target_dir_remote = windows_path_join(destination_remote, 'upload_target')
        manifest_file_path = os.path.join(upload_target_dir, "aws-windows-deployment-manifest.json")

        create_migration_folders_remote(remote_connection, bundle_dir_remote, upload_target_dir_remote)

        relative_normalized_manifest_path = absolute_to_relative_normalized_path(manifest_file_path)
        if os.path.exists(manifest_file_path):
            if verbose:
                io.echo(f"  Updating {relative_normalized_manifest_path}")
            with open(manifest_file_path) as file:
                manifest_contents = json.load(file)
        else:
            manifest_contents = {
                'manifestVersion': 1,
                'deployments': {
                    'msDeploy': [],
                    'custom': []
                }
            }

        for application in site.Applications:
            warn_about_password_protection(site, application)
            ms_deploy_sync_application_remote(
                remote_connection,
                site,
                application,
                destination,
                destination_remote,
                upload_target_dir,
                upload_target_dir_remote,
                manifest_contents
            )
            for vdir in application.VirtualDirectories:
                if vdir.Path != '/':
                    additional_virtual_dir_physical_paths.append(vdir.PhysicalPath)
        if verbose:
            io.echo(f"Updating manifest file for archive at {relative_normalized_manifest_path}")
        with open(manifest_file_path, 'w') as file:
            json.dump(manifest_contents, file, indent=4)

    def do_command(self):
        remote = self.app.pargs.remote
        if not remote and not sys.platform.startswith("win"):
            raise NotSupportedError("'eb migrate' is only supported on Windows")

        verbose = self.app.pargs.verbose

        site_names = self.app.pargs.sites
        env_name = self.app.pargs.environment_name
        app_name = self.app.pargs.application_name
        platform = self.app.pargs.platform
        instance_type = self.app.pargs.instance_type
        instance_profile = self.app.pargs.instance_profile
        service_role = self.app.pargs.service_role
        ebs_snapshots = self.app.pargs.ebs_snapshots
        keyname = self.app.pargs.keyname
        interactive = self.app.pargs.interactive
        cname = self.app.pargs.cname
        region = self.app.pargs.region
        archive_only = self.app.pargs.archive_only
        on_prem_mode = self.app.pargs.on_prem_mode
        tags = self.app.pargs.tags
        tags = tagops.get_and_validate_tags(tags)
        copy_firewall_config = self.app.pargs.copy_firewall_config
        encrypt_ebs_volumes = self.app.pargs.encrypt_ebs_volumes
        ssl_certificate = self.app.pargs.ssl_certificates
        archive = self.app.pargs.archive

        target_ip = self.app.pargs.target_ip
        username = self.app.pargs.username
        password = self.app.pargs.password


        
        # Validate remote execution parameters
        if remote:
            if not target_ip:
                raise ValueError("--target-ip is required when using --remote")
            if not username:
                raise ValueError("--username is required when using --remote")
            if not password:
                raise ValueError("--password is required when using --remote")
                
        if archive and archive_only:
            raise ValueError("Cannot use --archive-only with --archive-dir together.")
        vpc_config = self.app.pargs.vpc_config

        if remote:
            remote_connection = initialize_ssh_connection(target_ip, username, password)
        else:
            remote_connection = None

        if remote:
            validate_iis_and_powershell_remote(remote_connection)
        else:
            validate_iis_version_greater_than_7_0()

        if remote:
            sites = populate_site_data_remote(remote_connection,
                                      establish_candidate_sites_remote(remote_connection, site_names))
        else:
            sites = establish_candidate_sites(site_names, interactive)

        on_an_ec2_instance = True
        environment_vpc, _region, instance_id, instance_tags = (
            dict(),
            None,
            list(),
            None,
        )

        try:
            if not remote:
                environment_vpc, _region, instance_id, instance_tags = (
                    construct_environment_vpc_config(on_prem_mode, verbose)
                )
                on_an_ec2_instance = not not instance_id
        except NotAnEC2Instance:
            on_an_ec2_instance = False
        if vpc_config:
            environment_vpc = load_environment_vpc_from_vpc_config(vpc_config)
        region = _region or establish_region(region, interactive, app_name, platform)
        LOG.debug("Writing region_name to .elasticbeanstalk/config")
        fileoperations.write_config_setting("global", "region_name", region)
        tags = tags or instance_tags
        snapshots_string = generate_snapshots_string(ebs_snapshots)

        app_name = establish_app_name(app_name, interactive, sites)
        env_name = establish_env_name(env_name, app_name, interactive, sites)
        platform = establish_platform_remote(remote_connection) if remote else establish_platform(platform, interactive)
        process_keyname(keyname)

        listener_configs = []
        if remote and not _arr_enabled_remote(remote_connection):
            listener_configs = get_listener_configs(sites, remote, remote_connection, ssl_certificate)

        if not remote and not _arr_enabled():
            listener_configs = get_listener_configs(sites, remote, remote_connection, ssl_certificate)

        all_ports = get_all_ports(sites)

        ec2_security_group = None
        load_balancer_security_group = None
        if on_an_ec2_instance and copy_firewall_config and not remote:
            load_balancer_security_group, ec2_security_group = (
                ec2.establish_security_group(all_ports, env_name, environment_vpc["id"])
            )

        source_bundle_zip = None
        upload_target_dir = None
        latest_migration_run_path = None
        if not archive:
            latest_migration_run_path = setup_migrations_dir(verbose)
            upload_target_dir = os.path.join(latest_migration_run_path, "upload_target")
            if remote:
                latest_migration_run_path_remote = setup_migrations_dir_remote(remote_connection)
                upload_target_dir_remote = windows_path_join(latest_migration_run_path, 'upload_target')
                os.makedirs(upload_target_dir, exist_ok=True)
                self.package_sites_remote(remote_connection, sites, latest_migration_run_path,
                                          latest_migration_run_path_remote, upload_target_dir, upload_target_dir_remote,
                                          verbose)
                import_packaged_sites_from_remote(remote_connection, latest_migration_run_path_remote, upload_target_dir)
                write_ebdeploy_utility_script(upload_target_dir)
                if _arr_enabled_remote(remote_connection):
                    export_arr_config_remote(remote_connection, upload_target_dir, verbose)
                if copy_firewall_config:
                    write_copy_firewall_config_script(upload_target_dir, sites)
                fileoperations.zip_up_folder(upload_target_dir, upload_target_zip_path())
            else:
                os.makedirs(upload_target_dir, exist_ok=True)
                self.package_sites(
                    sites, latest_migration_run_path, upload_target_dir, verbose
                )
                write_ebdeploy_utility_script(upload_target_dir)
                if _arr_enabled():
                    export_arr_config(upload_target_dir, verbose)
                if copy_firewall_config:
                    write_copy_firewall_config_script(upload_target_dir, sites)
                fileoperations.zip_up_folder(upload_target_dir, upload_target_zip_path())
        else:
            if zipfile.is_zipfile(archive):
                source_bundle_zip = archive
            else:
                upload_target_dir = archive
                latest_migration_run_path = os.path.dirname(upload_target_dir)
                self.package_sites(
                    sites, latest_migration_run_path, upload_target_dir, verbose
                )
                fileoperations.zip_up_folder(
                    upload_target_dir, upload_target_zip_path()
                )

        if listener_configs and latest_migration_run_path:
            with open(
                os.path.join(latest_migration_run_path, "listener_configs.json"), "w"
            ) as file:
                listener_configs_json = {"listener_configs": listener_configs}
                json.dump(listener_configs_json, file, indent=2)
        if archive_only and upload_target_dir:
            generate_upload_target_archive(upload_target_dir, env_name, region)
            return

        self.create_app_version_and_environment(
            app_name=app_name,
            source_bundle_zip=source_bundle_zip,
            instance_profile=instance_profile,
            service_role=service_role,
            instance_type=instance_type,
            cname=cname,
            env_name=env_name,
            encrypt_ebs_volumes=encrypt_ebs_volumes,
            environment_vpc=environment_vpc,
            ec2_security_group=ec2_security_group,
            platform=platform,
            keyname=keyname,
            tags=tags,
            snapshots_string=snapshots_string,
            listener_configs=listener_configs,
            load_balancer_security_group=load_balancer_security_group,
            interactive=interactive,
        )

        # -------------------------------------------------------------------------------
        # proceed to create application version and the EB environment beyond this point
        # -------------------------------------------------------------------------------

    def create_app_version_and_environment(
        self,
        app_name,
        source_bundle_zip,
        instance_profile,
        service_role,
        instance_type,
        cname,
        env_name,
        encrypt_ebs_volumes,
        environment_vpc,
        ec2_security_group,
        platform,
        keyname,
        tags,
        snapshots_string,
        listener_configs,
        load_balancer_security_group,
        interactive,
    ):
        version_label = commonops.create_app_version(
            app_name, source_bundle=source_bundle_zip or upload_target_zip_path()
        )
        instance_profile = establish_instance_profile(instance_profile)
        if not service_role:
            service_role = createops.create_default_service_role()
        instance_type = instance_type or "c5.2xlarge"
        cname = cname or get_unique_cname(env_name)
        if encrypt_ebs_volumes:
            do_encrypt_ebs_volumes()

        if environment_vpc and environment_vpc.get("securitygroups"):
            vpc_security_groups = set(environment_vpc["securitygroups"].split(","))
            if ec2_security_group:
                vpc_security_groups.add(ec2_security_group.get("Value", set()))
            environment_vpc["securitygroups"] = ",".join(list(vpc_security_groups))
            ec2_security_group = None

        root_volume = [
            {
                "Namespace": namespaces.LAUNCH_CONFIGURATION,
                "OptionName": "RootVolumeSize",
                "Value": "60",
            }
        ]

        env_request = requests.CreateEnvironmentRequest(
            app_name=app_name,
            env_name=env_name,
            platform=platform,
            version_label=version_label,
            instance_profile=instance_profile,
            service_role=service_role,
            key_name=keyname,
            tags=tags,
            vpc=environment_vpc,
            elb_type="application",
            instance_types=instance_type,
            min_instances="1",
            max_instances="4",
            block_device_mappings=snapshots_string,
            listener_configs=listener_configs,
            cname=cname,
            description="Environment created by `eb migrate`",
            load_balancer_security_group=load_balancer_security_group,
            ec2_security_group=ec2_security_group,
            root_volume=root_volume,
        )

        createops.make_new_env(env_request, interactive=interactive, timeout=15)

    def package_sites(
        self,
        sites: List["Site"],
        latest_migration_run_path: str,
        upload_target_dir: str,
        verbose: bool,
    ) -> None:
        """
        Package IIS sites and their components for deployment.

        Creates deployment bundles for specified IIS sites, including their applications
        and virtual directories. Generates necessary PowerShell scripts for deployment
        and permission management.

        Args:
            sites: List of IIS Site objects to package
            latest_migration_run_path: Path to store migration artifacts
            upload_target_dir: Directory for deployment scripts and bundles
            verbose: If True, provides detailed output during packaging

        Process Flow:
            1. Announces sites being packaged (if not verbose)
            2. Generates MS Deploy bundles for each site
            3. Creates necessary PowerShell scripts:
               - noop.ps1 for placeholder operations
               - Virtual directory permission script (if needed)
            4. Updates manifest with virtual directory configurations

        Notes:
            - Tracks additional virtual directory paths across all sites
            - Creates permission management scripts only if virtual directories exist
            - Uses MS Deploy for package generation
            - Maintains list of physical paths requiring special permissions

        Example Output (non-verbose):
            Generating source bundle for sites, applications, and virtual directories: [Site1, Site2]
        """
        additional_virtual_dir_physical_paths = []
        if not verbose:
            command_separated_sites_list = ", ".join([s.Name for s in sites])
            io.echo(
                f"Generating source bundle for sites, applications, and virtual directories: [{command_separated_sites_list}]"
            )
        for site in sites:
            self.generate_ms_deploy_source_bundle(
                site,
                destination=latest_migration_run_path,
                verbose=verbose,
                additional_virtual_dir_physical_paths=additional_virtual_dir_physical_paths,
            )
        create_noop_ps1_script(upload_target_dir)
        if additional_virtual_dir_physical_paths:
            create_virtualdir_path_permission_script(
                additional_virtual_dir_physical_paths, upload_target_dir
            )
            add_virtual_directory_custom_script_to_manifest(upload_target_dir)

    def package_sites_remote(self, remote_connection, sites, latest_migration_run_path, latest_migration_run_path_remote, upload_target_dir, upload_target_dir_remote, verbose):
        additional_virtual_dir_physical_paths = []
        if not verbose:
            command_separated_sites_list = ', '.join([s.Name for s in sites])
            io.echo(f"Generating source bundle for sites, applications, and virtual directories: [{command_separated_sites_list}]")
        for site in sites:
            self.generate_ms_deploy_source_bundle_remote(
                remote_connection,
                site,
                destination=latest_migration_run_path,
                destination_remote=latest_migration_run_path_remote,
                verbose=verbose,
                additional_virtual_dir_physical_paths=additional_virtual_dir_physical_paths
            )

        create_noop_ps1_script(upload_target_dir)
        if additional_virtual_dir_physical_paths:
            create_virtualdir_path_permission_script(additional_virtual_dir_physical_paths, upload_target_dir)
            add_virtual_directory_custom_script_to_manifest(upload_target_dir)


def import_packaged_sites_from_remote(remote_connection, latest_migration_run_path_remote, upload_target_dir):
    upload_target_dir_remote = latest_migration_run_path_remote + "/upload_target"
    remote_directory = convert_to_ssh_path(upload_target_dir_remote)
    local_directory = upload_target_dir

    remote_directory = remote_directory.replace('/', '\\').strip('\\')
    if remote_directory.startswith('\\'):
        remote_directory = remote_directory[1:]

    try:
        result = remote_connection.run(f'powershell -Command "Get-ChildItem -Path \"{remote_directory}\" -Filter *.zip | Select-Object -ExpandProperty Name"', hide=True)

        filenames = [f.strip().rstrip('?') for f in result.stdout.strip().split('\n') if f.strip()]

        for filename in filenames:
            temp_remote_file = remote_directory+"/"+filename
            temp_remote_file_normalized = convert_to_ssh_path(temp_remote_file)
            local_file_path = os.path.join(local_directory, filename)

            try:
                remote_connection.get(temp_remote_file_normalized, local_file_path)
            except Exception as e:
                io.echo(f"Failed to download {filename}: {e}")
                continue

        # Now handle folders containing zip files
        folder_result = remote_connection.run(
            f'powershell -Command "Get-ChildItem -LiteralPath \'{remote_directory}\' -Directory | Select-Object -ExpandProperty Name"',
            hide=True)
        folders = [f.strip() for f in folder_result.stdout.strip().split('\n') if f.strip()]

        for folder in folders:
            # Create the local folder
            local_folder_path = os.path.join(local_directory, folder)
            os.makedirs(local_folder_path, exist_ok=True)

            # Get zip files in this folder
            zip_result = remote_connection.run(
                f'powershell -Command "Get-ChildItem -LiteralPath \'{remote_directory}\\{folder}\' -Filter *.zip | Select-Object -ExpandProperty Name"',
                hide=True)
            zip_files = [f.strip() for f in zip_result.stdout.strip().split('\n') if f.strip()]

            for zip_file in zip_files:
                remote_zip_path = f"{remote_directory}\\{folder}\\{zip_file}"
                remote_zip_path_normalized = convert_to_ssh_path(remote_zip_path)
                local_zip_path = os.path.join(local_folder_path, zip_file)

                try:
                    remote_connection.get(remote_zip_path_normalized, local_zip_path)
                except Exception as e:
                    io.echo(f"Failed to download {zip_file} in folder {folder}: {e}")
                    continue

    except Exception as e:
        io.echo(f"Error during file download: {str(e)}")
        raise

    return True

def get_all_ports(sites):
    all_ports = set()
    for site in sites:
        for binding in site.Bindings:
            all_ports.add(int(binding.get_BindingInformation().split(":")[1]))
    return all_ports


def get_unique_non_80_ports(sites):
    all_ports = set()
    for site in sites:
        bindings = site.Bindings
        for binding in bindings:
            port = binding.BindingInformation.split(":")[1]
            if port != "80":
                all_ports.add(port)
    return all_ports


def absolute_to_relative_normalized_path(abs_path):
    relative_path = os.path.relpath(abs_path, os.getcwd())
    path_parts = relative_path.split(os.sep)  # Split path into components
    for i, part in enumerate(path_parts):
        if part.startswith("migration_"):
            path_parts[i] = "latest"
    return os.path.join(*path_parts)


def do_encrypt_ebs_volumes():
    try:
        ec2.enable_ebs_volume_encryption()
    except Exception as e:
        io.log_error(f"Failed to enable EBS volume encryption: {e}")
        raise e


def establish_instance_profile(instance_profile):
    instance_profile = instance_profile or commonops.create_default_instance_profile()
    fileoperations.write_config_setting("global", "instance_profile", instance_profile)
    return instance_profile


def generate_upload_target_archive(upload_target_dir, env_name, region):
    fileoperations.zip_up_folder(upload_target_dir, upload_target_zip_path())
    relative_normalized_upload_target_dir_path = absolute_to_relative_normalized_path(
        upload_target_dir
    )

    try:
        test_environment_exists(env_name)
        io.echo(
            f"\nGenerated destination archive ZIP at .\\{relative_normalized_upload_target_dir_path}.zip. "
            "You can now upload the zip using:\n\n"
            f"    eb deploy {env_name} --archive .\\migrations\\latest\\upload_target.zip --region {region}\n"
        )
    except NotFoundError:
        io.echo(
            f"\nGenerated destination archive directory at .\\{relative_normalized_upload_target_dir_path}.zip. "
            "You can create an environment with the zip using:\n\n"
            f"    eb migrate --environment-name {env_name} --archive .\\migrations\\latest\\upload_target.zip --region {region}\n"
        )


def test_environment_exists(env_name):
    elasticbeanstalk.get_environment(env_name=env_name)


def upload_target_zip_path():
    return os.path.join(os.getcwd(), "migrations", "latest", "upload_target.zip")


def add_virtual_directory_custom_script_to_manifest(upload_target_dir):
    manifest_file_path = os.path.join(
        upload_target_dir, "aws-windows-deployment-manifest.json"
    )
    if os.path.exists(manifest_file_path):
        with open(manifest_file_path) as file:
            manifest_contents = json.load(file)
    else:
        manifest_contents = {
            "manifestVersion": 1,
            "deployments": {"msDeploy": [], "custom": []},
        }
    manifest_contents["deployments"]["custom"].append(
        create_custom_manifest_section(
            "FixVirtualDirPermissions",
            "add_virtual_dir_read_access.ps1",
            "noop.ps1",
            "noop.ps1",
        )
    )
    with open(manifest_file_path, "w") as file:
        json.dump(manifest_contents, file, indent=4)


def process_keyname(keyname):
    if keyname:
        commonops.upload_keypair_if_needed(keyname)
        LOG.debug("Writing default_ec2_keyname to .elasticbeanstalk/config")
        fileoperations.write_config_setting("global", "default_ec2_keyname", keyname)


def establish_platform(platform, interactive):
    if not platform and interactive:
        platform = platformops.prompt_for_platform()
    elif not platform:
        io.echo("Determining EB platform based on host machine properties")
        platform = _determine_platform(platform_string=get_windows_server_version())
    else:
        io.echo(f"Determining EB platform based on input, {platform}")
        platform = _determine_platform(platform)
    LOG.debug("Writing platform_name to .elasticbeanstalk/config")
    fileoperations.write_config_setting("global", "platform_name", platform.name)
    return platform

def establish_platform_remote(remote_connection):
    io.echo("Determining EB platform based on remote machine properties")
    platform = _determine_platform(platform_string=get_windows_server_version_remote(remote_connection))

    return platform


def establish_env_name(env_name, app_name, interactive, sites):
    if not env_name and interactive:
        env_name = get_environment_name(app_name)
    elif not env_name:
        LOG.debug("Setting env_name to site_name with whitespaces removed")
        if len(sites) == 1:
            candidate_env_name = sites[0].Name.replace(" ", "")
        else:
            candidate_env_name = "EBMigratedEnv"
        env_name = get_unique_environment_name(candidate_env_name)
    return env_name


def establish_app_name(app_name, interactive, sites):
    if not app_name and interactive:
        app_name = _get_application_name_interactive()
    elif not app_name:
        LOG.debug("Setting app_name to site_name with whitespaces removed")
        if len(sites) == 1:
            app_name = sites[0].Name.replace(" ", "")
        else:
            app_name = "EBMigratedApp"
    LOG.debug("Writing application_name to .elasticbeanstalk/config")
    fileoperations.write_config_setting("global", "application_name", app_name)
    return app_name


def generate_snapshots_string(ebs_snapshots):
    snapshots_string = []
    if ebs_snapshots:
        char_iter = iter(string.ascii_lowercase)
        io.echo(f"Using input EBS snapshot configuration: {snapshots_string}")
        snapshots_string = ",".join(
            [f"/dev/sd{next(char_iter)}={snapshot}" for snapshot in ebs_snapshots]
        )
    return snapshots_string


def establish_region(region, interactive, app_name, platform):
    if not region and interactive:
        region = commonops.get_region(None, True)
    elif not region:
        region = commonops.get_region_force_non_interactive(platform)
    aws.set_region(region)
    fileoperations.create_config_file(
        app_name=app_name,
        region=region,
        solution_stack=platform,
        workspace_type="Application",
    )
    return region


def establish_candidate_sites(
    site_names: Optional[str], interactive: bool
) -> List["Site"]:
    """
    Determine which IIS sites to include in the migration process.

    Resolves the list of IIS sites to migrate based on input parameters and
    available sites. Sites can be specified explicitly, chosen interactively,
    or determined automatically based on the presence of Default Web Site.

    Args:
        site_names: Comma-separated string of site names to migrate.
                   If None, uses interactive or default behavior.
        interactive: If True and site_names is None, prompts user to select
                    a site from available options.

    Returns:
        List of IIS Site objects to be migrated

    Selection Logic:
        1. If site_names provided:
           - Validates all specified sites exist
           - Returns corresponding Site objects
        2. If interactive and no site_names:
           - Prompts user to select one site
           - Returns list with selected site
        3. If non-interactive and no site_names:
           - If Default Web Site exists, returns all sites
           - Otherwise, raises error

    Raises:
        ValueError: If specified site name doesn't exist
        EnvironmentError: If no sites specified in non-interactive mode and
                         Default Web Site doesn't exist

    Example:
        >>> # Explicit selection
        >>> sites = establish_candidate_sites("Site1,Site2", False)
        >>> # Interactive selection
        >>> sites = establish_candidate_sites(None, True)
        >>> # Default behavior
        >>> sites = establish_candidate_sites(None, False)
    """
    server_manager = ServerManager()
    if not server_manager.Sites:
        raise ValueError(
            "`eb migrate` failed because there are no sites on this IIS server."
        )
    available_sites = [s.Name for s in server_manager.Sites]
    if site_names:
        site_names = site_names.split(",")

    if site_names:
        for site_name in site_names:
            if site_name not in available_sites:
                raise ValueError(
                    f"Specified site, '{site_name}', does not exist. Available sites: [{', '.join(available_sites)}]"
                )
        sites = server_manager.Sites
    elif not site_names and interactive:
        io.echo("Select an IIS site to migrate:")
        site_name = utils.prompt_for_item_in_list(
            [s.Name for s in server_manager.Sites], default="1"
        )
        site = [s for s in server_manager.Sites if s.Name == site_name][0]
        sites = [site]
    else:
        sites = server_manager.Sites
    if not sites:
        raise EnvironmentError(
            "`eb migrate` failed because there are no sites on this IIS server."
        )
    return sites

def establish_candidate_sites_remote(remote_connection, site_names):
    ps_command = '''
    Import-Module WebAdministration
    Get-Website | Select-Object -ExpandProperty Name | ForEach-Object {
        Write-Host $_
    }
    '''
    command_bytes = ps_command.encode('utf-16le')
    encoded_command = base64.b64encode(command_bytes).decode()
    result = remote_connection.run(f'powershell -NoProfile -NonInteractive -EncodedCommand {encoded_command}', hide=True)
    output = result.stdout.strip()

    available_sites = [site for site in output.split('\n') if site.strip()]

    if not available_sites:
        raise EnvironmentError(
            "`eb migrate` failed because there are no sites on this IIS server."
        )

    if site_names:
        site_names = site_names.split(",")
        sites = []

        for site_name in site_names:
            if site_name not in available_sites:
                raise ValueError(
                    f"Specified site, '{site_name}', does not exist. Available sites: [{', '.join(available_sites)}]"
                )
            sites.append(site_name)
        return sites
    else:
        return available_sites

def populate_site_data_remote(remote_connection, site_names):
    sites = []
    for name in site_names:
        sites.append(get_site_remote(remote_connection, name))

    return sites

def get_site_remote(c, site_name) -> None:
    ps_command = f"""
    Import-Module WebAdministration
    $site = Get-Item "IIS:\\Sites\\{site_name}"
    $config = Get-WebConfiguration -Filter "system.webServer/httpProtocol/customHeaders" -PSPath "IIS:\\Sites\\{site_name}"
    $hsts = $config.Collection | Where-Object {{ $_.ElementTagName -eq 'add' -and $_.Attributes['name'].Value -eq 'Strict-Transport-Security' }}
    $bindings = Get-WebBinding -Name "{site_name}"

    $rootVDirs = @(Get-WebConfiguration "/system.applicationHost/sites/site[@name='{site_name}']/application[@path='/']/virtualDirectory" | ForEach-Object {{
        @{{
            Path = $_.GetAttributeValue("path")
            PhysicalPath = $_.GetAttributeValue("physicalPath")
        }}
    }})

    $rootApp = @{{
        Path = "/"
        ApplicationPoolName = $site.applicationPool
        PhysicalPath = $site.PhysicalPath
        VirtualDirectories = $rootVDirs
    }}

    $applications = Get-WebApplication -Site "{site_name}" | ForEach-Object {{
        $appPath = $_.path
        $appVDirs = @(Get-WebConfiguration "/system.applicationHost/sites/site[@name='{site_name}']/application[@path='$appPath']/virtualDirectory" | ForEach-Object {{
            @{{
                Path = $_.GetAttributeValue("path")
                PhysicalPath = $_.GetAttributeValue("physicalPath")
            }}
        }})

        @{{
            Path = $appPath
            ApplicationPoolName = $_.applicationPool
            PhysicalPath = $_.PhysicalPath
            VirtualDirectories = $appVDirs
        }}
    }}

    $allApplications = @($rootApp) + @($applications)

    $result = @{{
        Name = $site.Name
        Attributes = @($site.Attributes | ForEach-Object {{ @{{ Name = $_.Name; Value = $_.Value }} }})
        Bindings = @($bindings | ForEach-Object {{
            $bindingInfo = $_.bindingInformation -split ':'
            $hostValue = if ($bindingInfo[2] -eq '') {{ '*' }} else {{ $bindingInfo[2] }}
            @{{
                BindingInformation = $_.bindingInformation
                Protocol = $_.protocol
                CertificateHash = $_.certificateHash
                CertificateStoreName = $_.certificateStoreName
                Host = $hostValue
                EndPoint = @{{
                    Port = [int]$bindingInfo[1]
                    Address = $bindingInfo[0]
                }}
            }}
        }})
        Applications = $allApplications
        HSTS = @{{
            Enabled = $hsts -ne $null
            MaxAge = if ($hsts) {{ $hsts.Attributes['value'].Value }} else {{ $null }}
        }}
    }}

    ConvertTo-Json -InputObject $result -Depth 5
    """

    command_bytes = ps_command.encode('utf-16le')
    encoded_command = base64.b64encode(command_bytes).decode()
    result = c.run(f'powershell -NoProfile -NonInteractive -EncodedCommand {encoded_command}', hide=True)

    site_data = json.loads(result.stdout.strip())

    EndPoint = namedtuple('EndPoint', ['Port', 'Address'])

    Attribute = namedtuple('Attribute', ['get_Name', 'get_Value'])
    Binding = namedtuple('Binding', ['get_BindingInformation', 'BindingInformation', 'Protocol', 'get_Protocol', 'get_CertificateHash',
                                     'get_CertificateStoreName', 'Host', 'get_Host', 'EndPoint', 'get_EndPoint'])
    VirtualDirectory = namedtuple('VirtualDirectory', ['Path', 'PhysicalPath'])
    Application = namedtuple('Application', ['Path', 'ApplicationPoolName', 'PhysicalPath', 'VirtualDirectories'])
    HSTS = namedtuple('HSTS', ['Enabled', 'MaxAge'])
    Site = namedtuple('Site', ['Name', 'Bindings', 'get_Attributes', 'get_Bindings', 'Applications', 'HSTS'])

    attributes = [Attribute(
        get_Name=lambda name=attr['Name']: name,
        get_Value=lambda value=attr['Value']: value
    ) for attr in site_data['Attributes']]

    bindings = [Binding(
        get_BindingInformation=lambda bi=b['BindingInformation']: bi,
        BindingInformation=b['BindingInformation'],
        Protocol=b['Protocol'],
        get_Protocol=lambda p=b['Protocol']: p,
        get_CertificateHash=lambda ch=b['CertificateHash']: ch,
        get_CertificateStoreName=lambda csn=b['CertificateStoreName']: csn,
        Host=b['Host'],  # Use the Host value directly
        get_Host=lambda h=b['Host']: h,
        EndPoint=EndPoint(Port=b['EndPoint']['Port'], Address=b['EndPoint']['Address']),
        get_EndPoint=lambda ep=EndPoint(Port=b['EndPoint']['Port'], Address=b['EndPoint']['Address']): ep
    ) for b in site_data['Bindings']]

    applications = [Application(
        Path=app['Path'],
        ApplicationPoolName=app['ApplicationPoolName'],
        PhysicalPath=app['PhysicalPath'],
        VirtualDirectories=[VirtualDirectory(
            Path=vdir['Path'],
            PhysicalPath=vdir['PhysicalPath']
        ) for vdir in app['VirtualDirectories']]
    ) for app in site_data['Applications']]

    hsts = HSTS(
        Enabled=site_data['HSTS']['Enabled'],
        MaxAge=site_data['HSTS']['MaxAge']
    )

    site = Site(
        Name=site_data['Name'],
        Bindings=bindings,
        get_Attributes=lambda: attributes,
        get_Bindings=lambda: bindings,
        Applications=applications,
        HSTS=hsts
    )

    return site


def list_sites_verbosely():
    # TODO: Show URL rewrites and proxy information
    for i, site in enumerate(ServerManager().Sites, 1):
        io.echo(f"{i}: {site.Name}:")
        io.echo(f"  - Bindings:")
        for binding in site.Bindings:
            io.echo(f"    - {binding.BindingInformation}")
        for application in site.Applications:
            io.echo(f"  - Application '{application.Path}':")
            io.echo(f"    - Application Pool: {application.ApplicationPoolName}")
            io.echo(f"    - Enabled Protocols: {application.EnabledProtocols}")
            io.echo(f"    - Virtual Directories:")
            virdirs = application.VirtualDirectories
            for vdir in virdirs:
                io.echo(f"      - {vdir.Path}:")
                io.echo(f"        - Physical Path: {vdir.PhysicalPath}")
                io.echo(f"        - Logon Method: {vdir.LogonMethod}")
                if vdir.UserName:
                    io.echo(f"        - Username: {vdir.UserName}")
                if vdir.Password:
                    io.echo("        - Password: <redacted>")
    try:
        users = get_local_users()
    except:
        return
    io.echo("----------------------------------------------------")
    io.echo("Users:")
    for username, homedir in users:
        io.echo(f"  - {username}")
        io.echo(f"    - Home: {homedir}")


def get_local_users():
    ctx = PrincipalContext(ContextType.Machine)
    user_principal = UserPrincipal(ctx)
    searcher = PrincipalSearcher(user_principal)

    users = searcher.FindAll()
    user_list = [
        (user.SamAccountName, user.HomeDirectory) for user in users if user.Enabled
    ]

    return user_list


def load_environment_vpc_from_vpc_config(vpc_config: str) -> Dict[str, any]:
    """
    Load and validate VPC configuration from either a JSON file or JSON string.

    Parses VPC configuration from either a .json file or a JSON-formatted string,
    validates required fields, and provides defaults for optional parameters.

    Args:
        vpc_config: Either:
            - Path to a JSON file (must end in .json)
            - JSON-formatted string containing VPC configuration

    Returns:
        Dictionary containing VPC configuration with keys:
            - id: (required) VPC ID
            - publicip: (optional) Whether to assign public IPs, default True
            - elbscheme: (optional) ELB scheme, default "public"
            - ec2subnets: (optional) List of EC2 subnet IDs, default []
            - securitygroups: (optional) Comma-separated security group IDs, default ""
            - elbsubnets: (optional) List of ELB subnet IDs, default []

    Raises:
        FileNotFoundError: If vpc_config is a file path and:
            - File doesn't exist
            - File can't be opened
            - File is a directory
            - Permission denied
        ValueError: If:
            - JSON parsing fails
            - Required 'id' field is missing
            - Invalid JSON format in file or string

    Example JSON Format:
        {
            "id": "vpc-1234567890abcdef0",
            "publicip": true,
            "elbscheme": "public",
            "ec2subnets": ["subnet-123", "subnet-456"],
            "securitygroups": ["sg-123", "sg-456"],
            "elbsubnets": ["subnet-789", "subnet-abc"]
        }
    """
    if vpc_config.endswith(".json"):
        try:
            with open(os.path.join(vpc_config)) as file:
                vpc_config_dict = json.load(file)
        except FileNotFoundError | PermissionError | IsADirectoryError | OSError:
            raise FileNotFoundError(
                f"Cannot open file {vpc_config} to parse VPC config. Verify that it exists and contains valid JSON."
            )
        except json.JSONDecodeError:
            raise ValueError(
                f"Cannot parse {vpc_config}. Verify that it is a valid JSON file."
            )
    else:
        try:
            vpc_config_dict = json.loads(vpc_config)
        except json.JSONDecodeError:
            raise ValueError(
                f"Cannot parse VPC config: {vpc_config}. Verify that it is a valid JSON string."
            )

    try:
        vpc_config_dict["id"]
    except KeyError:
        raise ValueError(f"Must specify a VPC ID in VPC config file '{vpc_config}'")

    return {
        "id": vpc_config_dict["id"],
        "publicip": vpc_config_dict.get("publicip", True),
        "elbscheme": vpc_config_dict.get("elbscheme", "public"),
        "ec2subnets": vpc_config_dict.get("ec2subnets", []),
        "securitygroups": "".join(vpc_config_dict.get("securitygroups", [])),
        "elbsubnets": vpc_config_dict.get("elbsubnets", []),
    }


def construct_environment_vpc_config(
    on_prem_mode: bool, verbose: bool
) -> Tuple[Dict[str, str], Optional[str], Optional[str], List[Dict[str, str]]]:
    """
    Detect and construct VPC configuration from current EC2 instance or handle on-premises scenario.

    Attempts to gather VPC configuration from the current EC2 instance, including
    subnets, security groups, and tags. Falls back to empty configuration if running
    on-premises or if EC2 detection fails.

    Args:
        on_prem_mode: If True, skip EC2 detection and return empty configuration
        verbose: If True, print detailed VPC configuration information

    Returns:
        Tuple containing:
            - Dict[str, str]: VPC configuration with keys:
                * id: VPC ID
                * publicip: Always 'true'
                * elbscheme: Always 'public'
                * ec2subnets: Comma-separated list of first 3 subnet IDs
                * securitygroups: Comma-separated list of security group IDs
                * elbsubnets: Same as ec2subnets
            - Optional[str]: AWS region of instance, or None if not on EC2
            - Optional[str]: Instance ID, or None if not on EC2
            - List[Dict[str, str]]: Instance tags, excluding AWS system tags

    Notes:
        - Uses interleaved AZ subnet selection for high availability
        - Only includes first 3 subnets for EC2 and ELB
        - Filters out system tags (elasticbeanstalk:*, aws:*, Name)
        - Returns empty VPC config if:
            * on_prem_mode is True
            * Not running on EC2
            * EC2 metadata access fails

    Example Output (verbose=True):
        Identifying VPC configuration of this EC2 instance (i-1234567890abcdef0):
          id: vpc-1234567890abcdef0
          publicip: true
          elbscheme: public
          ec2subnets: subnet-123,subnet-456,subnet-789
          securitygroups: sg-123,sg-456
          elbsubnets: subnet-123,subnet-456,subnet-789
    """
    environment_vpc = dict()
    region = None
    tags = []
    instance_id = None

    current_instance_details = ec2.get_current_instance_details()

    try:
        if on_prem_mode:
            raise NotAnEC2Instance("Pretend this is an on-prem instance")

        instance_id = current_instance_details["InstanceId"]
        _vpc = current_instance_details["VpcId"]
        security_groups = current_instance_details["SecurityGroupIds"]
        subnets = ",".join(ec2.list_subnets_azs_interleaved(_vpc)[:3])
        region = current_instance_details["Region"]
        environment_vpc = {
            "id": _vpc,
            "publicip": "true",
            "elbscheme": "public",
            "ec2subnets": subnets,
            "publicip": "true",
            "securitygroups": ",".join(security_groups),
            "elbsubnets": subnets,
        }
        io.echo(f"Identifying VPC configuration of this EC2 instance ({instance_id}):")
        if verbose:
            for key, value in environment_vpc.items():
                io.echo(f"  {key}: {value}")
        tags = [
            tag
            for tag in current_instance_details["Tags"]
            if not (
                tag["Key"].startswith("elasticbeanstalk:")
                or tag["Key"].startswith("aws:")
                or tag["Key"] == "Name"
            )
        ]
    except NotAnEC2Instance:
        raise
    except Exception:
        io.echo(
            f"Unable to detect EC2 configuration. Possibly executing on a non-EC2 instance"
        )
        pass
    return environment_vpc, region, instance_id, tags


def _determine_platform(platform_string=None):
    if not platform_string:
        platform_string = platformops.get_configured_default_platform()

    if platform_string:
        platform = platformops.get_platform_for_platform_string(platform_string)
    else:
        raise ValueError(
            f"Couldn't identify a platform based on hint: {platform_string}"
        )

    if isinstance(platform, PlatformVersion):
        platform.hydrate(elasticbeanstalk.describe_platform_version)
        statusops.alert_platform_status(platform)

    return platform


def setup_migrations_dir(verbose: bool) -> str:
    """
    Create and configure a timestamped migration directory structure.

    Creates a migrations directory with a timestamped subdirectory for the current
    migration run, and sets up a 'latest' symlink pointing to it. The directory
    structure is used to store migration artifacts, logs, and deployment files.

    Args:
        verbose: If True, prints detailed information about log file locations
                and directory purposes

    Returns:
        str: Absolute path to the newly created migration directory

    Directory Structure:
        migrations/
        ├── latest -> migration_[timestamp]/  (symlink)
        └── migration_[timestamp]/
            ├── application.log    (msbuild.exe logs)
            ├── error.log         (msbuild.exe errors)
            └── upload_target/    (deployment artifacts)

    Notes:
        - Creates 'migrations' directory in current working directory if it doesn't exist
        - Generates unique directory name using UTC timestamp
        - Updates 'latest' symlink to point to new directory
        - Preserves original working directory
        - Creates directories with exist_ok=True to handle race conditions

    Example Output:
        Using .\\migrations\\migration_1708445678.123456 to contain artifacts for this migration run.
        If verbose:
            .\\migrations\\migration_1708445678.123456\\application.log -> msbuild.exe application logs
            .\\migrations\\migration_1708445678.123456\\error.log -> msbuild.exe error logs
            .\\migrations\\migration_1708445678.123456\\upload_target\\ -> destination archive dir
    """
    migrations_dir = "migrations"
    migrations_dir_path = os.path.join(os.getcwd(), migrations_dir)
    cwd = os.getcwd()
    os.makedirs(migrations_dir_path, exist_ok=True)
    os.chdir(migrations_dir_path)
    latest_migration_dir_name = "migration_" + str(
        datetime.datetime.utcnow().timestamp()
    )
    os.makedirs(latest_migration_dir_name)
    if os.path.exists("latest"):
        os.unlink("latest")
    os.symlink(latest_migration_dir_name, "latest", target_is_directory=True)
    os.chdir(cwd)
    latest_migration_run_path = os.path.join(
        migrations_dir_path, latest_migration_dir_name
    )
    relative_path = os.path.relpath(latest_migration_run_path, os.curdir)
    relative_normalized_path = absolute_to_relative_normalized_path(relative_path)
    io.echo(
        f"Using .\\{relative_normalized_path} to contain artifacts for this migration run."
    )
    if verbose:
        io.echo(
            f"  .\\{relative_normalized_path}\\application.log -> msbuild.exe application logs"
        )
        io.echo(f"  .\\{relative_normalized_path}\\error.log -> msbuild.exe error logs")
        io.echo(
            f"  .\\{relative_normalized_path}\\upload_target\\ -> destination archive directory"
        )
    return latest_migration_run_path

def setup_migrations_dir_remote(remote_connection):
    # PowerShell command to execute
    ps_command = '''
    $migrationsDir = "migrations"
    $migrationsDirPath = Join-Path -Path $PWD -ChildPath $migrationsDir
    $cwd = $PWD

    New-Item -Path $migrationsDirPath -ItemType Directory -Force | Out-Null

    Set-Location -Path $migrationsDirPath

    $latestMigrationDirName = "migration_" + [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    New-Item -Path $latestMigrationDirName -ItemType Directory | Out-Null

    if (Test-Path -Path "latest") {
        (Get-Item "latest").Delete()
    }

    $null = New-Item -ItemType Junction -Path "latest" -Target $latestMigrationDirName

    Set-Location -Path $cwd

    return Join-Path -Path $migrationsDirPath -ChildPath $latestMigrationDirName
    '''
    command_bytes = ps_command.encode('utf-16le')
    encoded_command = base64.b64encode(command_bytes).decode()
    result = remote_connection.run(f'powershell -NoProfile -NonInteractive -EncodedCommand {encoded_command}', hide=True)

    output = result.stdout.strip()

    return output


def get_environment_name(app_name):
    return io.prompt_for_environment_name(get_unique_environment_name(app_name))


def get_unique_environment_name(app_name):
    default_name = app_name + "-dev"
    current_environments = elasticbeanstalk.get_all_environment_names()

    return utils.get_unique_name(default_name, current_environments)


def _get_application_name_interactive():
    app_list = elasticbeanstalk.get_application_names()
    file_name = fileoperations.get_current_directory_name()
    new_app = False
    if len(app_list) > 0:
        io.echo()
        io.echo("Select an application to use")
        new_app_option = "[ Create new Application ]"
        app_list.append(new_app_option)
        try:
            default_option = app_list.index(file_name) + 1
        except ValueError:
            default_option = len(app_list)
        app_name = utils.prompt_for_item_in_list(app_list, default=default_option)
        if app_name == new_app_option:
            new_app = True

    if len(app_list) == 0 or new_app:
        io.echo()
        io.echo("Enter Application Name")
        unique_name = utils.get_unique_name(file_name, app_list)
        app_name = io.prompt_for_unique_name(unique_name, app_list)

    return app_name


def get_registry_value(key, subkey, value):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey)
        return winreg.QueryValueEx(key, value)[0]
    except WindowsError:
        return None, None


def get_windows_product_name():
    product_name = get_registry_value(
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
        "ProductName",
    )

    return product_name


def get_windows_server_version():
    product_name = get_windows_product_name()
    return product_name.replace(" Datacenter", "")

def get_windows_server_version_remote(c):
    ps_command = '''
    function Get-WindowsServerVersion {
        $registryPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        $valueName = "ProductName"

        try {
            $productName = Get-ItemPropertyValue -Path $registryPath -Name $valueName
            if ($productName -like "*Windows Server*") {
                return $productName -replace ' (Datacenter).*$', ''
            } else {
                Write-Host "This does not appear to be a Windows Server operating system."
                exit 1
            }
        }
        catch {
            Write-Host "Failed to retrieve Windows Product Name: $_"
            exit 1
        }
    }


    $windowsServerVersion = Get-WindowsServerVersion
    if ($windowsServerVersion) {
        $windowsServerVersion
    }
    '''

    command_bytes = ps_command.encode('utf-16le')
    encoded_command = base64.b64encode(command_bytes).decode()

    result = c.run(f'powershell -NoProfile -NonInteractive -EncodedCommand {encoded_command}', hide=True)
    output = result.stdout.strip()

    return output

def get_unique_cname(env_name):
    """
    Derive a unique CNAME for a new environment based on the environment name
    :param env_name: name of the environment
    directory
    :return: A unique CNAME for a new environment
    """
    cname = env_name
    tried_cnames = []
    while not elasticbeanstalk.is_cname_available(cname):
        tried_cnames.append(cname)
        utils.sleep(0.5)
        cname = utils.get_unique_name(cname, tried_cnames)
    return cname


def get_iis_version_from_registry() -> str:
    """
    Retrieve the IIS version from the Windows registry.

    Returns:
        str: The IIS version number.

    Raises:
        OSError: If unable to access the registry or retrieve the IIS version.
    """
    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\InetStp"
        ) as key:
            version = winreg.QueryValueEx(key, "VersionString")[0]
        return version.split()[-1]
    except (OSError, IndexError) as e:
        raise OSError(
            "Unable to retrieve IIS version from Windows registry. "
            "Please ensure that IIS (version 7.0 or later) is installed "
            "and that you have sufficient permissions to access the registry."
        ) from e


def validate_iis_version_greater_than_7_0() -> None:
    """
    Validate that the installed IIS version is 7.0 or later.

    Raises:
        EnvironmentError: If the IIS version is less than 7.0 or cannot be determined.
    """
    try:
        iis_version = float(get_iis_version_from_registry())
        if iis_version < 7.0:
            raise EnvironmentError(
                f"IIS version {iis_version} is not supported. "
                "Please upgrade to IIS version 7.0 or later."
            )
    except ValueError as e:
        raise EnvironmentError(
            "Unable to determine IIS version. "
            "Please ensure that IIS (version 7.0 or later) is properly installed."
        ) from e

def validate_iis_and_powershell_remote(remote_connection) -> None:
    ps_command = '''
    $is64Bit = [System.Environment]::Is64BitProcess
    Import-Module WebAdministration
    $iisVersion = Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\InetStp" | Select-Object -ExpandProperty MajorVersion

    if ($is64Bit -and [int]$iisVersion -gt 7) {
        Write-Host "Requirements met: 64-bit PowerShell and IIS version > 7"
    } else {
        $errors = @()
        if (-not $is64Bit) { $errors += "PowerShell is not 64-bit" }
        if (-not ([int]$iisVersion -gt 7)) { $errors += "IIS version is not > 7" }
        Write-Host ("Requirements not met: " + ($errors -join " and "))
        exit 1
    }
    '''
    command_bytes = ps_command.encode('utf-16le')
    encoded_command = base64.b64encode(command_bytes).decode()
    result = remote_connection.run(f'powershell -NoProfile -NonInteractive -EncodedCommand {encoded_command}', hide=True)
    output = result.stdout.strip()

    if not output.startswith("Requirements met:"):
        raise EnvironmentError(output)

def initialize_ssh_connection(target_ip, username, password):
    return Connection(target_ip, user=username, connect_kwargs={'password': password, 'allow_agent': False, 'look_for_keys': False})

def get_all_assemblies(root_assembly):
    visited = HashSet[str]()
    queue = Queue[Assembly]()
    queue.Enqueue(root_assembly)

    assemblies = []

    while queue.Count > 0:
        current_asm = queue.Dequeue()

        if not visited.Contains(current_asm.FullName):
            visited.Add(current_asm.FullName)
            assemblies.append(current_asm)

            # Enumerate references of the current assembly
            for ref_name in current_asm.GetReferencedAssemblies():
                try:
                    ref_asm = Assembly.Load(ref_name)
                    if ref_asm is not None and not visited.Contains(ref_asm.FullName):
                        queue.Enqueue(ref_asm)
                except Exception as e:
                    # Handle cases where an assembly fails to load
                    LOG.debug(
                        f"Could not load referenced assembly {ref_name.Name}: {e}"
                    )
                    io.log_warning(f"Could not load {ref_name.Name}.")

    return assemblies


def copy_assemblies_into_bin(bin_path: str, site_name: str) -> None:
    root_assembly = Assembly.LoadFrom(os.path.join(bin_path, f"{site_name}.dll"))
    LOG.debug(f"Transitive dependencies: ")
    for asm in get_all_assemblies(root_assembly):
        if asm.Location == os.path.join(bin_path, f"{site_name}.dll"):
            continue
        LOG.debug(f"Copying {asm.FullName}: {asm.Location} into {bin_path}")


def hsts_disablement_arg(site):
    try:
        if not site.HSTS.Enabled:
            return f'-skip:objectName=hsts,absolutePath="{site.Name}"'
    except AttributeError as e:
        if not "'Site' object has no attribute 'HSTS'" in str(e):
            raise e
    return ""


def ms_deploy_sync_application(
    site: "Site",
    application: "Application",
    destination: str,
    upload_target_dir: str,
    manifest_contents: Dict[str, Any],
) -> None:
    """
    Synchronize an IIS application to deployment artifacts and update the manifest.

    Creates deployment artifacts and manifest entries for an IIS application,
    handling different deployment scenarios based on whether the application
    belongs to the Default Web Site or a custom site.

    Args:
        site: IIS Site object containing the application
        application: IIS Application object to be synchronized
        destination: Directory for deployment artifacts and logs
        upload_target_dir: Target directory for generated files
        manifest_contents: Elastic Beanstalk deployment manifest to update

    Manifest Handling:
        - Default Web Site applications:
            * Added to 'msDeploy' section
            * Uses Web Deploy for deployment
            * May include port reassignment if not on port 80
        - Custom site applications:
            * Added to 'custom' section
            * Includes installation, restart, and removal scripts
            * May include ARR configuration if needed

    Special Cases:
        1. ARR Configuration:
            - Generates ARR configuration scripts if proxy is enabled
            - Adds Windows Proxy Feature enablement scripts
        2. Port Reassignment:
            - Handles Default Web Site running on non-standard ports
        3. IIS Start Page:
            - Adds configuration for iisstart.htm if present

    Generated Files:
        - Application bundle (.zip)
        - PowerShell scripts for site management
        - ARR configuration scripts (if needed)
        - Port reassignment scripts (if needed)
        - Default document configuration (if needed)

    Notes:
        - File paths in manifest are normalized and made relative to CWD
        - Site names are normalized (spaces removed) for file naming
        - Manifest sections are added only if they don't already exist
        - Uses 'noop.ps1' for optional restart/uninstall operations
    """
    _normalized_application_name = normalized_application_name(site, application)
    destination_archive_path = os.path.join(
        upload_target_dir, _normalized_application_name
    )
    relative_path = os.path.relpath(upload_target_dir, os.curdir)
    relative_normalized_path = absolute_to_relative_normalized_path(relative_path)
    io.echo(
        f"  {site.Name}{application.Path} -> .\\{relative_normalized_path}\\{_normalized_application_name}.zip"
    )
    _iis_application_name_value = iis_application_name_value(site, application)
    ms_deploy_args_str = construct_ms_deploy_command_for_application(
        site, application, _iis_application_name_value, destination_archive_path
    )
    LOG.debug("    Executing the following script to create destination application:")
    LOG.debug(f"\n        {ms_deploy_args_str}\n")
    do_ms_deploy_sync_application(
        ms_deploy_args_str,
        destination,
        destination_archive_path,
        upload_target_dir,
        _normalized_application_name,
    )
    manifest_section_name = _iis_application_name_value.strip("/")

    application_pool_name = application.ApplicationPoolName
    virts = [virt for virt in application.VirtualDirectories if virt.Path == "/"]
    if not virts:
        return
    physical_path = virts[0].PhysicalPath
    contains_iistart_htm = os.path.exists(os.path.join(physical_path, "iisstart.htm"))

    if site.Name != "Default Web Site":
        installation_script_name = f"install_site_{site.Name.replace(' ', '')}.ps1"
        removal_script_name = f"remove_site_{site.Name.replace(' ', '')}.ps1"
        restart_script_name = f"restart_site_{site.Name.replace(' ', '')}.ps1"

        write_custom_site_installer_script(
            upload_target_dir,
            site.Name,
            site.Bindings,
            physical_path,
            installation_script_name,
        )
        write_custom_site_removal_script(
            upload_target_dir, site.Name, removal_script_name
        )
        write_custom_site_restarter_script(
            upload_target_dir, site.Name, restart_script_name
        )
        manifest_section = create_custom_manifest_section(
            manifest_section_name,
            installation_script_name,
            restart_script_name,
            removal_script_name,
            f"Custom script to install {site.Name}",
        )
        manifest_contents["deployments"]["custom"].append(manifest_section)
        if _arr_enabled():
            write_windows_proxy_feature_enabler_script(upload_target_dir)
            manifest_section = create_custom_manifest_section(
                "WindowsProxyFeatureEnabler",
                "windows_proxy_feature_enabler.ps1",
                "noop.ps1",
                "noop.ps1",
                f"Custom script to execute Install-WindowsFeature Web Proxy",
            )
            add_unique_manifest_section(
                "WindowsProxyFeatureEnabler", manifest_contents, manifest_section
            )

            write_arr_configuration_importer_script(upload_target_dir)
            manifest_section = create_custom_manifest_section(
                "ArrConfigurationImporterScript",
                "arr_configuration_importer_script.ps1",
                "noop.ps1",
                "noop.ps1",
                f"Custom script to enable ARR proxy",
            )
            add_unique_manifest_section(
                "ArrConfigurationImporterScript", manifest_contents, manifest_section
            )
            # manifest_contents['deployments']['custom'].append(manifest_section)
    else:
        manifest_section = {
            "name": manifest_section_name,
            "parameters": {
                "appBundle": f"{_normalized_application_name}.zip",
                "iisPath": application.Path,
                "iisWebSite": site.Name,
            },
        }
        post_install_custom_script_section = None
        for binding in site.Bindings:
            host, port, domain = binding.get_BindingInformation().split(":")
            if port != "80":
                port_reassignment_script_name = (
                    "default_web_site_port_reassignment_script.ps1"
                )
                write_default_web_site_port_reassignment_script(
                    upload_target_dir, binding, port_reassignment_script_name
                )
                post_install_custom_script_section = create_custom_manifest_section(
                    "ExecuteDefaultWebSitePortReassignment",
                    port_reassignment_script_name,
                    port_reassignment_script_name,
                    port_reassignment_script_name,
                    f"Perform port-reassignment for {site.Name} away from port 80",
                )
                break
        manifest_contents["deployments"]["msDeploy"].append(manifest_section)
        if post_install_custom_script_section:
            add_unique_manifest_section(
                "ExecuteDefaultWebSitePortReassignment",
                manifest_contents,
                post_install_custom_script_section,
            )
    # TODO: identify all DefaultDocuments for a given site and determine
    # whether there are any extra ones to account for
    if contains_iistart_htm:
        write_reinstate_iisstart_htm_default_document_script(upload_target_dir)
        manifest_section = create_custom_manifest_section(
            "ReinstateIISStartHTMDefaultDocumentScript",
            "reinstate_iisstart_htm_default_document.ps1",
            "noop.ps1",
            "noop.ps1",
            f"Custom script to enable iisstart.htm default document",
        )
        add_unique_manifest_section(
            "ExecuteDefaultWebSitePortReassignment", manifest_contents, manifest_section
        )

def ms_deploy_sync_application_remote(
        remote_connection,
        site,
        application,
        destination,
        destination_remote,
        upload_target_dir,
        upload_target_dir_remote,
        manifest_contents
):
    _normalized_application_name = normalized_application_name(site, application)
    destination_archive_path_remote = windows_path_join(upload_target_dir_remote, _normalized_application_name)

    _iis_application_name_value = iis_application_name_value(site, application)
    ms_deploy_args_str = construct_ms_deploy_command_for_application(
        site,
        application,
        _iis_application_name_value,
        destination_archive_path_remote
    )
    LOG.debug("    Executing the following script to create destination application:")
    LOG.debug(f"\n        {ms_deploy_args_str}\n")

    ms_deploy_ps_command = construct_msdeploy_powershell_command(ms_deploy_args_str)

    do_ms_deploy_sync_application_remote(
        remote_connection,
        ms_deploy_args_str,
        destination_remote,
        destination_archive_path_remote,
        upload_target_dir_remote,
        _normalized_application_name,
        ms_deploy_ps_command
    )
    manifest_section_name = _iis_application_name_value.strip("/")

    application_pool_name = application.ApplicationPoolName
    virts = [virt for virt in application.VirtualDirectories if virt.Path == '/']
    if not virts:
        return
    physical_path = virts[0].PhysicalPath
    contains_iistart_htm = contains_iistart_htm_remote(remote_connection, physical_path)

    if site.Name != 'Default Web Site':
        installation_script_name = f"install_site_{site.Name.replace(' ', '')}.ps1"
        removal_script_name = f"remove_site_{site.Name.replace(' ', '')}.ps1"
        restart_script_name = f"restart_site_{site.Name.replace(' ', '')}.ps1"

        write_custom_site_installer_script_remote(
            remote_connection,
            upload_target_dir,
            site.Name,
            site.Bindings,
            physical_path,
            installation_script_name,
        )

        write_custom_site_removal_script(
            upload_target_dir, site.Name, removal_script_name
        )

        write_custom_site_restarter_script(
            upload_target_dir, site.Name, restart_script_name
        )

        manifest_section = create_custom_manifest_section(
            manifest_section_name,
            installation_script_name,
            restart_script_name,
            removal_script_name,
            f"Custom script to install {site.Name}"
        )
        manifest_contents['deployments']['custom'].append(manifest_section)
        if _arr_enabled_remote(remote_connection):
            write_windows_proxy_feature_enabler_script(upload_target_dir)
            manifest_section = create_custom_manifest_section(
                "WindowsProxyFeatureEnabler",
                "windows_proxy_feature_enabler.ps1",
                "noop.ps1",
                "noop.ps1",
                f"Custom script to execute Install-WindowsFeature Web Proxy",
            )
            add_unique_manifest_section(
                "WindowsProxyFeatureEnabler", manifest_contents, manifest_section
            )

            write_arr_configuration_importer_script(upload_target_dir)
            manifest_section = create_custom_manifest_section(
                "ArrConfigurationImporterScript",
                "arr_configuration_importer_script.ps1",
                "noop.ps1",
                "noop.ps1",
                f"Custom script to enable ARR proxy",
            )
            add_unique_manifest_section(
                "ArrConfigurationImporterScript", manifest_contents, manifest_section
            )
    else:
        manifest_section = {
            "name": manifest_section_name,
            "parameters": {
                "appBundle": f"{_normalized_application_name}.zip",
                "iisPath": application.Path,
                "iisWebSite": site.Name,
            },
        }
        post_install_custom_script_section = None
        for binding in site.Bindings:
            host, port, domain = binding.get_BindingInformation().split(":")
            if port != "80":
                port_reassignment_script_name = (
                    "default_web_site_port_reassignment_script.ps1"
                )
                write_default_web_site_port_reassignment_script(
                    upload_target_dir, binding, port_reassignment_script_name
                )
                post_install_custom_script_section = create_custom_manifest_section(
                    "ExecuteDefaultWebSitePortReassignment",
                    port_reassignment_script_name,
                    port_reassignment_script_name,
                    port_reassignment_script_name,
                    f"Perform port-reassignment for {site.Name} away from port 80",
                )
                break
        manifest_contents["deployments"]["msDeploy"].append(manifest_section)
        if post_install_custom_script_section:
            add_unique_manifest_section(
                "ExecuteDefaultWebSitePortReassignment",
                manifest_contents,
                post_install_custom_script_section,
            )
    # TODO: identify all DefaultDocuments for a given site and determine
    # whether there are any extra ones to account for
    if contains_iistart_htm:
        write_reinstate_iisstart_htm_default_document_script(upload_target_dir)
        manifest_section = create_custom_manifest_section(
            "ReinstateIISStartHTMDefaultDocumentScript",
            "reinstate_iisstart_htm_default_document.ps1",
            "noop.ps1",
            "noop.ps1",
            f"Custom script to enable iisstart.htm default document",
        )
        add_unique_manifest_section(
            "ExecuteDefaultWebSitePortReassignment", manifest_contents, manifest_section
        )

def add_unique_manifest_section(
    section_name: str,
    manifest_contents: Dict[str, Any],
    section_contents: Dict[str, Any],
) -> None:
    """
    Add a section to the deployment manifest only if it doesn't already exist.

    Checks the custom deployments section of an Elastic Beanstalk manifest for
    a section with the specified name, and adds the new section only if no
    section with that name exists.

    Args:
        section_name: Name of the section to check for and potentially add
        manifest_contents: Complete manifest dictionary containing the deployments
                         structure with a 'custom' list
        section_contents: New section configuration to add if section_name
                        doesn't exist

    Notes:
        - Operates on manifest_contents in-place
        - Only checks sections under ['deployments']['custom']
        - Preserves existing section if name match is found
        - Appends new section if no matching name is found

    Example:
        >>> manifest = {
        ...     'deployments': {
        ...         'custom': [
        ...             {'name': 'existing_section', 'scripts': {...}}
        ...         ]
        ...     }
        ... }
        >>> new_section = {'name': 'new_section', 'scripts': {...}}
        >>> add_unique_manifest_section('new_section', manifest, new_section)
    """
    found = False
    for manifest_section in manifest_contents["deployments"]["custom"]:
        if manifest_section["name"] == section_name:
            found = True
            break
    if not found:
        manifest_contents["deployments"]["custom"].append(section_contents)


def cleanup_previous_migration_artifacts(force: bool, verbose: bool) -> None:
    """
    Clean up old migration directories while preserving the 'latest' migration.

    Removes previous migration artifacts from the 'migrations' directory, keeping
    only the 'latest' symbolic link and its target. Can operate in interactive
    or force mode.

    Args:
        force: If True, skip confirmation prompt and delete automatically.
              If False, prompt user for confirmation.
        verbose: If True, print detailed information about deleted directories.
                If False, log deletions at debug level only.

    Directory Structure:
        migrations/
        ├── latest -> timestamp_directory/  (symlink preserved)
        ├── timestamp_directory/           (preserved if latest)
        ├── old_timestamp_1/              (deleted)
        └── old_timestamp_2/              (deleted)

    Notes:
        - Only operates if 'migrations' directory exists in current working directory
        - Preserves 'latest' symlink and its target directory
        - Prompts for confirmation unless force=True
        - Logs or prints deletion operations based on verbose setting
        - Handles both relative and absolute paths safely

    Example:
        >>> cleanup_previous_migration_artifacts(force=True, verbose=True)
        # Output:
        # Deleting older migration artifacts.
        #   - Deleting directory: migrations/20240219_120000
        #   - Deleting directory: migrations/20240218_120000
    """
    migration_dir_name = "migrations"
    if not os.path.exists(migration_dir_name):
        io.echo("There is no directory called 'migrations' in PWD. Nothing to do.")
        return
    should_delete = force or io.get_boolean_response(
        text=prompts["migrate.should_cleanup"], default=False
    )
    if not should_delete:
        return
    latest_path = os.path.realpath(os.path.join(migration_dir_name, "latest"))
    io.echo("Deleting older migration artifacts.")
    for item in os.listdir(migration_dir_name):
        if item == "latest":
            continue
        item_path = os.path.abspath(os.path.join("migrations", item))
        if os.path.isdir(item_path) and item_path != latest_path:
            if verbose:
                io.echo(f"  - Deleting directory: {item_path}")
            else:
                LOG.debug(f"  - Deleting directory: {item_path}")
            shutil.rmtree(item_path)


def construct_msdeploy_powershell_command(args_string):
    ps_command = ['$msdeployExe = "${env:ProgramFiles}\\IIS\\Microsoft Web Deploy V3\\msdeploy.exe"']
    ps_command.append('$msdeployArgs = @(')

    # Split on space-hyphen-letter, but keep the hyphen-letter part
    args = re.split(r' (?=-[a-zA-Z])', args_string)

    for arg_str in args:
        arg_str = arg_str.strip()
        if not arg_str:
            continue

        arg_str = arg_str.replace("'", '"')

        if arg_str.startswith('-dest:archiveDir='):
            path = arg_str.split('=', 1)[1]
            path = path.strip('"').strip("'")
            arg_str = f'-dest:archiveDir=`"{path}`"'
        else:
            arg_str = arg_str.replace('"', '`"')

        ps_command.append(f'    "{arg_str}"')

    ps_command.append(')')
    ps_command.append('$output = & $msdeployExe $msdeployArgs 2>&1')

    return '\n'.join(ps_command)

def do_ms_deploy_sync_application(
    ms_deploy_args_str: str,
    destination: str,
    destination_archive_path: str,
    upload_target_dir: str,
    _normalized_application_name: str,
) -> None:
    """
    Execute Web Deploy synchronization for an IIS application and process the results.

    Runs msdeploy.exe with specified arguments to export an IIS application,
    captures output and errors, and packages the result into a ZIP file if successful.

    Args:
        ms_deploy_args_str: Complete Web Deploy command arguments string
        destination: Directory for log files
        destination_archive_path: Temporary directory for Web Deploy output
        upload_target_dir: Target directory for final ZIP file
        _normalized_application_name: Sanitized application name for ZIP file

    Raises:
        RuntimeError: If Web Deploy process exits with non-zero status

    Process Flow:
        1. Locates msdeploy.exe
        2. Executes Web Deploy with specified arguments
        3. Captures stdout/stderr to log files
        4. On success:
            - Creates ZIP from destination_archive_path
            - Cleans up temporary directory
        5. On failure:
            - Logs error
            - Raises exception with exit code

    Notes:
        - Creates/appends to 'application.log' and 'error.log' in destination directory
        - Final ZIP file will be named '{_normalized_application_name}.zip'
        - Cleans up temporary archive directory after successful ZIP creation
    """
    ms_deploy_exe, use_64bit = get_webdeployv3path()

    start_info = ProcessStartInfo()
    start_info.FileName = ms_deploy_exe
    start_info.Arguments = ms_deploy_args_str
    start_info.RedirectStandardOutput = True
    start_info.RedirectStandardError = True
    start_info.UseShellExecute = False
    start_info.CreateNoWindow = True

    # Start the process
    process = Process()
    process.StartInfo = start_info
    process.Start()

    # Redirect standard output and error to files
    with open(os.path.join(destination, "application.log"), "a") as stdout_file:
        stdout_file.write(process.StandardOutput.ReadToEnd())

    with open(os.path.join(destination, "error.log"), "a") as stderr_file:
        stderr_file.write(process.StandardError.ReadToEnd())

    process.WaitForExit()

    if process.ExitCode == 0:
        fileoperations.zip_up_folder(
            destination_archive_path,
            os.path.join(upload_target_dir, f"{_normalized_application_name}.zip"),
        )
        shutil.rmtree(destination_archive_path)
    else:
        io.log_error(f"MSDeploy process exited with code {process.ExitCode}.")
        raise RuntimeError(
            f"MSDeploy process exited with code {process.ExitCode}. You can find execution logs at .\\migrations\\latest\\error.log"
        )


def do_ms_deploy_sync_application_remote(
        remote_connection,
        ms_deploy_args_str,
        destination_remote,
        destination_archive_path_remote,
        upload_target_dir_remote,
        _normalized_application_name,
        ms_deploy_ps_command
):
    ps_script_1 = f"""
    New-Item -ItemType Directory -Force -Path "{destination_remote}" | Out-Null
    New-Item -ItemType Directory -Force -Path "{upload_target_dir_remote}" | Out-Null

    $null > "{destination_remote}\\application.log"
    $null > "{destination_remote}\\error.log"

    try {{
        # Get MSDeploy path
        $programFiles = $env:ProgramFiles
        $msdeployExe = Join-Path $programFiles "IIS\Microsoft Web Deploy V3\msdeploy.exe"

        if (-not (Test-Path $msdeployExe)) {{
            throw "Could not find MSDeploy.exe at: $msdeployExe"
            exit 1
        }}

        Write-Host "Using MSDeploy: $msdeployExe"
    }}
    catch {{
        Write-Error "Error during execution: $_"
        throw
    }}
    """
    ps_script_2 = ms_deploy_ps_command
    ps_script_3 = f"""
    try {{
        $exitCode = $LASTEXITCODE

        # Log standard output and error
        $output | Out-File -Append -FilePath "{destination_remote}\\application.log"

        if ($exitCode -eq 0) {{
            Write-Host "MSDeploy completed successfully"
        }}
        else {{
            $errorMessage = "MSDeploy process exited with code $exitCode"
            Write-Error $errorMessage
            throw $errorMessage
        }}
    }}
    catch {{
        Write-Error "Error during execution: $_"
        throw
    }}
    """

    ps_script_5 = f"""
        try {{
            $ErrorActionPreference = 'Continue'
            $src="{destination_archive_path_remote}";$dst="{upload_target_dir_remote}\\{_normalized_application_name}.zip"
            if(Test-Path -Path $dst){{Remove-Item -Path $dst -Recurse -Force}}
            Add-Type -A System.IO.Compression,System.IO.Compression.FileSystem
            $z=[System.IO.Compression.ZipFile]::Open($dst,[System.IO.Compression.ZipArchiveMode]::Create)
            Get-ChildItem $src -Recurse -Force|Where-Object{{$_.Name -ne '.gitignore' -and $_.FullName -notlike '*.elasticbeanstalk*'}}|ForEach-Object{{
                $p=$_.FullName.Substring($src.Length+1).Replace('\\','/')
                if($_.PSIsContainer){{
                    if(-not$p.EndsWith('/')){{$p+='/'}}
                    $e=$z.CreateEntry($p);$e.ExternalAttributes=0x41ED0000  # Directory: 755
                }}else{{
                    $e=$z.CreateEntry($p)
                    if($_.Attributes -band [IO.FileAttributes]::ReparsePoint){{
                        $t=[IO.Path]::GetFullPath((Get-Item $_.FullName).Target)
                        $b=[Text.Encoding]::UTF8.GetBytes($t);$e.ExternalAttributes=0xA1FF0000  # Symlink: 777
                        $s=$e.Open();$s.Write($b,0,$b.Length);$s.Dispose()
                    }}else{{
                        $e.ExternalAttributes=0x81A40000  # Regular file: 644
                        $b=[IO.File]::ReadAllBytes($_.FullName)
                        $s=$e.Open();$s.Write($b,0,$b.Length);$s.Dispose()
                    }}
                }}
            }}
            $z.Dispose()
            if(Test-Path -Path $src){{Remove-Item -Path $src -Recurse -Force}}
        }}catch{{Write-Output "Error: $_";throw}}
        """

    combined_ps_script = f"""
    # First command
    {ps_script_1}

    # Second command
    {ps_script_2}

    # Third command
    {ps_script_3}
    """

    ps_script_23 = ps_script_2 + "\n\n" + ps_script_3

    command_one_bytes = ps_script_1.encode('utf-16le')
    encoded_command_one = base64.b64encode(command_one_bytes).decode()
    result_one = remote_connection.run(f'powershell -NoProfile -NonInteractive -EncodedCommand {encoded_command_one}', hide=True)

    output_one = result_one.stdout.strip()

    command_two_bytes = ps_script_23.encode('utf-16le')
    encoded_command_two = base64.b64encode(command_two_bytes).decode()
    result_2 = remote_connection.run(f'powershell -NonInteractive -EncodedCommand {encoded_command_two}', hide=True)

    output_2 = result_2.stdout.strip()

    command_three_bytes = ps_script_5.encode('utf-16le')
    encoded_command_three = base64.b64encode(command_three_bytes).decode()
    result_3 = remote_connection.run(f'powershell -NonInteractive -EncodedCommand {encoded_command_three}', hide=True)

    output_3 = result_3.stdout.strip()

def contains_iistart_htm_remote(remote_connection, physical_path):
    physical_path = physical_path.replace('/', '\\')

    ps_command = f'''
    function Test-IISStartHtm {{
        param(
            [string]$physicalPath
        )

        try {{
            # Expand any environment variables in the path
            $expandedPath = [System.Environment]::ExpandEnvironmentVariables($physicalPath)

            # Resolve the path to handle relative paths
            $resolvedPath = Resolve-Path $expandedPath -ErrorAction Stop | Select-Object -ExpandProperty Path

            $fullPath = Join-Path -Path $resolvedPath -ChildPath "iisstart.htm"
            $exists = Test-Path -Path $fullPath -PathType Leaf

            # Return the result as a string
            return $exists.ToString().ToLower()
        }}
        catch {{
            Write-Error "Failed to check for iisstart.htm: $_"
            return "error"
        }}
    }}

    $result = Test-IISStartHtm -physicalPath '{physical_path}'
    Write-Output $result
    '''

    command_bytes = ps_command.encode('utf-16le')
    encoded_command = base64.b64encode(command_bytes).decode()

    result = remote_connection.run(f'powershell -NoProfile -NonInteractive -EncodedCommand {encoded_command}', hide=True)
    output = result.stdout.strip()

    return output.lower() == 'true'


def construct_ms_deploy_command_for_application(
    site: "Site",
    application: "Application",
    _iis_application_name_value: str,
    destination_archive_path: str,
) -> str:
    """
    Construct Web Deploy (MSDeploy) command for exporting an IIS application.

    Builds a command string for Web Deploy to synchronize an IIS application
    configuration to an archive directory, including application pool settings
    and security configurations.

    Args:
        site: IIS Site object containing the application
        application: IIS Application object to be exported
        _iis_application_name_value: Full application path in IIS format
                                   (e.g., "Default Web Site/MyApp")
        destination_archive_path: Path where the application archive will be created

    Returns:
        str: Complete MSDeploy command string with all necessary parameters and
             settings for application export

    Command Components:
        - Sync verb for export operation
        - Source from IIS application host configuration
        - Destination archive directory
        - Application pool configuration and parameterization
        - IIS application name parameterization
        - Security content handling
        - HSTS settings handling

    Example:
        >>> cmd = construct_ms_deploy_command_for_application(
        ...     site,
        ...     app,
        ...     "Default Web Site/MyApp",
        ...     "C:\\export\\myapp"
        ... )
        >>> # Returns: "-verb:sync -source:apphostconfig=... -dest:archiveDir=..."
    """
    ms_deploy_verb = "-verb:sync"
    ms_deploy_source = f'-source:apphostconfig="{_iis_application_name_value}"'
    ms_deploy_dest = f"-dest:archiveDir='{destination_archive_path}'"
    ms_deploy_enable_app_pool_ext = "-enableLink:AppPoolExtension"
    application_pool_name = application.ApplicationPoolName
    ms_deploy_app_pool = (
        "-declareParam:name='Application Pool',"
        f"defaultValue='{application_pool_name}',"
        f"description='Application pool for application {application.Path}',"
        "kind=DeploymentObjectAttribute,"
        "scope=appHostConfig,"
        "match='application/@applicationPool'"
    )

    iis_website_application_name_arg = (
        "-declareParam:name='IIS Web Application Name',"
        f"defaultValue='{_iis_application_name_value.strip('/')}'"
    )

    copy_secure_content_arg = "-enableRule:CopySecureContent"

    ms_deploy_args = [
        ms_deploy_verb,
        ms_deploy_source,
        ms_deploy_dest,
        ms_deploy_enable_app_pool_ext,
        ms_deploy_app_pool,
        iis_website_application_name_arg,
        hsts_disablement_arg(site),
        copy_secure_content_arg,
    ]
    return " ".join(ms_deploy_args)


def normalized_application_name(site, application):
    if application.Path == '/':
        return site.Name.replace(' ', '')
    return f'{site.Name}-{application.Path.strip('/')}'


def get_webdeployv3path() -> Tuple[str, bool]:
    """
    Locate the Web Deploy V3 (msdeploy.exe) installation path from Windows registry.

    Searches the Windows registry for Web Deploy V3 installation, checking both
    64-bit and 32-bit registry views. Returns the full path to msdeploy.exe and
    indicates whether it was found in the 64-bit registry.

    Returns:
        tuple: (path_to_msdeploy, is_64bit) where:
            - path_to_msdeploy (str): Full path to msdeploy.exe
            - is_64bit (bool): True if found in 64-bit registry, False if in 32-bit

    Raises:
        RuntimeError: If Web Deploy V3 installation cannot be found in either
                     registry view, with instructions for installation

    Notes:
        - Checks registry key: SOFTWARE\\Microsoft\\IIS Extensions\\MSDeploy\\3
        - Tries 64-bit registry first, falls back to 32-bit
        - Returns InstallPath value plus "msdeploy.exe"

    Example:
        >>> path, is_64bit = get_webdeployv3path()
        >>> # Typical return value:
        >>> # ("C:\\Program Files\\IIS\\Microsoft Web Deploy V3\\msdeploy.exe", True)
    """
    webdeployv3_key = r"SOFTWARE\Microsoft\IIS Extensions\MSDeploy\3"
    use_64bit = True
    # Try 64-bit registry first
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            webdeployv3_key,
            0,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
        )
    except WindowsError:
        use_64bit = False
        # If 64-bit fails, try 32-bit
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                webdeployv3_key,
                0,
                winreg.KEY_READ | winreg.KEY_WOW64_32KEY,
            )
        except WindowsError:
            error = "Couldn't find msdeploy.exe. Follow instructions here: https://learn.microsoft.com/en-us/iis/install/installing-publishing-technologies/installing-and-configuring-web-deploy"
            raise RuntimeError(error)

    install_path = winreg.QueryValueEx(key, "InstallPath")[0]
    winreg.CloseKey(key)
    return install_path + "msdeploy.exe", use_64bit


def warn_about_password_protection(site, application):
    _iis_application_name_value = iis_application_name_value(site, application)
    try:
        for vdir in application.VirtualDirectories:
            if vdir.Password:
                io.log_warning(
                    f"Cannot copy virtual directory associated with site because it is password protected: Site [{site.Name}/{_iis_application_name_value}], Path hosting:[{vdir.PhysicalPath}]"
                )
    except AttributeError:
        pass


def iis_application_name_value(site: "Site", application: "Application"):
    if application.Path == "/":
        return site.Name + "/"
    else:
        return f"{site.Name}\\{application.Path.strip('/')}"


def create_noop_ps1_script(upload_target_dir):
    script_path = os.path.join(os.path.dirname(__file__), "migrate_scripts", "noop.ps1")
    with open(script_path, "r") as source_file:
        script = source_file.read()

    with open(
        os.path.join(upload_target_dir, "ebmigrateScripts", "noop.ps1"), "w"
    ) as file:
        file.write(script)


def create_virtualdir_path_permission_script(physical_paths, upload_target_dir):
    script_path = os.path.join(
        os.path.dirname(__file__), "migrate_scripts", "add_virtual_dir_read_access.ps1"
    )
    with open(script_path, "r") as source_file:
        script_template = source_file.read()

    # Create the physical paths array string
    physical_paths_array_string = ",\n  ".join([f'"{p}"' for p in set(physical_paths)])

    # Replace the placeholder in the template
    script = script_template.replace(
        "# This will be populated dynamically with physical paths",
        physical_paths_array_string,
    )

    with open(
        os.path.join(
            upload_target_dir, "ebmigrateScripts", "add_virtual_dir_read_access.ps1"
        ),
        "w",
    ) as file:
        file.write(script)


def _arr_enabled() -> bool:
    """
    Check if Application Request Routing (ARR) is enabled in IIS configuration.

    Examines the applicationHost.config file to determine if ARR is both installed
    and enabled by checking the system.webServer/proxy section's 'enabled' attribute.

    Returns:
        bool: True if ARR is installed and enabled in IIS configuration,
              False if ARR is not installed or is disabled

    Notes:
        - Checks applicationHost.config via ServerManager COM interface
        - Returns False if proxy section doesn't exist (ARR not installed)
        - Logs debug message if proxy section is missing
        - Propagates unexpected exceptions

    Raises:
        Exception: Any unexpected errors during configuration access,
                  except for missing configuration section
    """
    server_manager = ServerManager()
    try:
        proxy_config_section = (
            server_manager.GetApplicationHostConfiguration().GetSection(
                "system.webServer/proxy"
            )
        )
        if proxy_config_section is None:
            return False
        return proxy_config_section.GetAttributeValue("enabled")
    except COMException:
        LOG.debug(
            "ConfigurationSection system.webServer/proxy does not exist in applicationHost.config."
        )
        pass
    except Exception as e:
        raise e

def _arr_enabled_remote(remote_connection):
    ps_command = '''
    function Check-ARREnabled {
        try {
            # Import WebAdministration module
            Import-Module WebAdministration -ErrorAction Stop

            # Check if the proxy section exists in IIS configuration
            $proxySection = Get-WebConfiguration -Filter "system.webServer/proxy" -ErrorAction SilentlyContinue

            if ($proxySection -ne $null) {
                Write-Output "True"
            } else {
                Write-Output "False"
            }
        }
        catch {
            Write-Output "False"
            Write-Error "Error checking ARR status: $_"
            exit 1
        }
    }

    Check-ARREnabled
    '''

    command_bytes = ps_command.encode('utf-16le')
    encoded_command = base64.b64encode(command_bytes).decode()

    try:
        result = remote_connection.run(f'powershell -NoProfile -NonInteractive -EncodedCommand {encoded_command}', hide=True)
        output = result.stdout.strip()

        return output.lower() == "true"
    except Exception as e:
        io.echo(f"Error checking ARR status: {str(e)}")
        return False


def export_arr_config(upload_target_dir: str, verbose: bool) -> None:
    """
    Export IIS Application Request Routing (ARR) configuration to XML files.

    Exports modified (non-default) settings from ARR-related IIS configuration
    sections to XML files. These files can be used to replicate ARR configuration
    on other servers during Elastic Beanstalk deployments.

    Args:
        upload_target_dir: Base directory for deployment artifacts. Configuration files
                          will be written to '{upload_target_dir}/ebmigrateScripts/'
        verbose: If True, provides detailed output about each configuration section
                and export operation

    Configuration Sections Exported:
        - system.webServer/proxy: ARR proxy settings
        - system.webServer/rewrite: URL rewrite rules
        - system.webServer/caching: Caching configuration

    Notes:
        - Only exports attributes that differ from default values
        - Creates one XML file per configuration section:
            * arr_config_proxy.xml
            * arr_config_rewrite.xml
            * arr_config_caching.xml
        - Skips sections that don't exist in the current configuration
        - Automatically generates ARR import script after export

    Raises:
        Exception: If export fails, with detailed error message

    Example XML Output:
        <proxy enabled="true" timeout="00:02:00" />
    """
    config_sections = [
        "system.webServer/proxy",
        "system.webServer/rewrite",
        "system.webServer/caching",
    ]
    if not _arr_enabled() and verbose:
        io.echo("No Automatic Request Routing (ARR) configuration found.")
        return
    else:
        io.echo("Automatic Request Routing (ARR) configuration found.")

    server_manager = ServerManager()
    try:
        for i, section in enumerate(config_sections, 1):
            section_name = section.split("/")[-1]
            arr_config_file = f"arr_config_{section_name}.xml"
            arr_config_file_path = os.path.join(
                upload_target_dir, "ebmigrateScripts", arr_config_file
            )
            with open(arr_config_file_path, "w") as file:
                config = server_manager.GetApplicationHostConfiguration()
                try:
                    section_obj = config.GetSection(section)
                except COMException:
                    if verbose:
                        io.echo(f"  {i}. Section {section} not found")
                    continue

                modified_attributes = [
                    attr
                    for attr in section_obj.Attributes
                    if not attr.IsInheritedFromDefaultValue
                ]

                # TODO: Handle child attributes for system.webserver/caching as well
                xml_content = f"<{section_name}"
                for attr in modified_attributes:
                    xml_content += f' {attr.Name}="{attr.Value}"'
                xml_content += " />"

                file.write(xml_content)
                if verbose:
                    io.echo(
                        f"  {i}. Modified {section_name} configuration exported to {arr_config_file_path}"
                    )
        if not verbose:
            io.echo("Exported ARR config.")
    except Exception as e:
        io.log_error(f"Failed to export ARR configuration: {str(e)}")
        raise
    write_arr_import_script_to_source_bundle(upload_target_dir)

def export_arr_config_remote(remote_connection, upload_target_dir, verbose):
    config_sections = [
        "system.webServer/proxy",
        "system.webServer/rewrite",
        "system.webServer/caching",
    ]
    if not _arr_enabled_remote(remote_connection):
        io.echo("No Automatic Request Routing configuration found.")
        return
    else:
        io.echo("Automatic Request Routing (ARR) configuration found.")

    try:
        for i, section in enumerate(config_sections, 1):
            section_name = section.split('/')[-1]
            arr_config_file = f"arr_config_{section_name}.xml"
            arr_config_file_path = os.path.join(upload_target_dir, 'ebmigrateScripts', arr_config_file)

            section_config = get_arr_section_config_remote(remote_connection, section)

            if section_config is None:
                if verbose:
                    io.echo(f"  {i}. Section {section} not found")
                continue

            xml_content = f"<{section_name}"
            for attr_name, attr_value in section_config.items():
                xml_content += f' {attr_name}="{attr_value}"'
            xml_content += " />"

            with open(arr_config_file_path, 'w') as file:
                file.write(xml_content)

            if verbose:
                io.echo(f"  {i}. Modified {section_name} configuration exported to {arr_config_file_path}")

        if not verbose:
            io.echo("Exported ARR config.")
    except Exception as e:
        io.echo(f"Failed to export ARR configuration: {str(e)}")
        raise
    write_arr_import_script_to_source_bundle(upload_target_dir)


def get_arr_section_config_remote(remote_connection, section_path):
    # For proxy section, we need special handling
    if section_path == "system.webServer/proxy":
        ps_command = '''
        Import-Module WebAdministration

        # Get the current configuration
        $config = Get-WebConfiguration -Filter "system.webServer/proxy"

        # Create a hashtable to store only the attributes we know are modified
        $modified = @{}

        # Check each attribute against known defaults
        # These are the attributes that appear in the local execution

        # enabled - default is False
        if ($config.enabled -eq $true) {
            $modified["enabled"] = $config.enabled
        }

        # timeout - default is 00:02:00 (2 minutes)
        if ($config.timeout.TotalMinutes -ne 2) {
            $h = $config.timeout.Hours.ToString("00")
            $m = $config.timeout.Minutes.ToString("00")
            $s = $config.timeout.Seconds.ToString("00")
            $modified["timeout"] = "$h`:$m`:$s"
        }

        # minResponseBuffer - default is 0
        if ($config.minResponseBuffer -ne 0) {
            $modified["minResponseBuffer"] = $config.minResponseBuffer
        }

        # responseBufferLimit - default is 4194304
        if ($config.responseBufferLimit -ne 4194304) {
            $modified["responseBufferLimit"] = $config.responseBufferLimit
        }

        ConvertTo-Json -InputObject $modified -Compress
        '''
    elif section_path == "system.webServer/caching":
        ps_command = '''
        Import-Module WebAdministration

        # Get the current configuration
        $config = Get-WebConfiguration -Filter "system.webServer/caching"

        # Create a hashtable to store only the attributes we know are modified
        $modified = @{}

        # Check each attribute against known defaults

        # enabled - default is False
        if ($config.enabled -eq $true) {
            $modified["enabled"] = $config.enabled
        }

        # enableKernelCache - default is False
        if ($config.enableKernelCache -eq $true) {
            $modified["enableKernelCache"] = $config.enableKernelCache
        }

        ConvertTo-Json -InputObject $modified -Compress
        '''
    else:
        # For other sections, return empty object
        ps_command = '''
        ConvertTo-Json -InputObject @{} -Compress
        '''

    command_bytes = ps_command.encode('utf-16le')
    encoded_command = base64.b64encode(command_bytes).decode()

    try:
        result = remote_connection.run(f'powershell -NoProfile -NonInteractive -EncodedCommand {encoded_command}', hide=True)
        output = result.stdout.strip()

        if output == "SECTION_NOT_FOUND":
            return None

        return json.loads(output)
    except Exception as e:
        io.echo(f"Error getting section config: {str(e)}")
        return None

def write_arr_import_script_to_source_bundle(upload_target_dir: str) -> None:
    """
    Generate a PowerShell script for downloading and installing IIS ARR component.

    Creates a script that handles the download and installation of Application Request
    Routing (ARR) for IIS. The script includes verification of existing installation
    and error handling for download/installation failures.

    Args:
        upload_target_dir: Base directory for deployment artifacts. The script will be
            written to '{upload_target_dir}/ebmigrateScripts/arr_msi_installer.ps1'

    Notes:
        - Generated script downloads from Microsoft's official URL
        - Creates installers directory at C:\\installers\\arr-install
        - Reports issues to aws-elastic-beanstalk-cli GitHub repository
    """
    script_path = os.path.join(
        os.path.dirname(__file__), "migrate_scripts", "arr_msi_installer.ps1"
    )
    with open(script_path, "r") as source_file:
        script = source_file.read()

    with open(
        os.path.join(upload_target_dir, "ebmigrateScripts", "arr_msi_installer.ps1"),
        "w",
    ) as file:
        file.write(script)


def write_windows_proxy_feature_enabler_script(upload_target_dir):
    script_path = os.path.join(
        os.path.dirname(__file__),
        "migrate_scripts",
        "windows_proxy_feature_enabler.ps1",
    )
    with open(script_path, "r") as source_file:
        script_contents = source_file.read()

    with open(
        os.path.join(
            upload_target_dir, "ebmigrateScripts", "windows_proxy_feature_enabler.ps1"
        ),
        "w",
    ) as file:
        file.write(script_contents)


def write_arr_configuration_importer_script(upload_target_dir: str) -> None:
    """
    Generate a PowerShell script for importing Application Request Routing (ARR) configuration.

    Creates a script that handles the import of ARR configuration from XML files,
    including proxy, rewrite, and caching settings. The script includes backup
    functionality and type-safe configuration import.

    Args:
        upload_target_dir: Base directory for deployment artifacts. The script will be
            written to '{upload_target_dir}/ebmigrateScripts/arr_configuration_importer_script.ps1'

    Notes:
        - Generated script requires WebAdministration PowerShell module
        - Handles three IIS configuration sections:
            * system.webServer/proxy
            * system.webServer/rewrite
            * system.webServer/caching
        - Expects configuration files in C:\\staging\\ebmigrateScripts\\
    """
    script_path = os.path.join(
        os.path.dirname(__file__),
        "migrate_scripts",
        "arr_configuration_importer_script.ps1",
    )
    with open(script_path, "r") as source_file:
        script_contents = source_file.read()

    with open(
        os.path.join(
            upload_target_dir,
            "ebmigrateScripts",
            "arr_configuration_importer_script.ps1",
        ),
        "w",
    ) as file:
        file.write(script_contents)

def convert_to_ssh_path(remote_path):
    # Replace backslashes with forward slashes
    ssh_path = remote_path.replace('\\', '/')

    # Add leading forward slash if not present
    if not ssh_path.startswith('/'):
        ssh_path = '/' + ssh_path

    return ssh_path

def write_custom_site_installer_script(
    upload_target_dir: str,
    site_name: str,
    bindings: List["Binding"],
    physical_path: str,
    installation_script_name: str,
) -> None:
    """
    Generate a PowerShell script for installing and configuring an IIS website.

    Creates an installation script that will be referenced in the Elastic Beanstalk
    deployment manifest's custom section. The script handles complete website setup
    including app pool creation, website configuration, and permissions. If Application
    Request Routing (ARR) is enabled in IIS, additional ARR configuration is included.

    Args:
        upload_target_dir: Base directory for deployment artifacts
        site_name: Name of the IIS website to create
        bindings: List of IIS binding objects defining site endpoints
        physical_path: Physical path where website content will be deployed
        installation_script_name: Name of the PowerShell script file to generate

    Generated Script Features:
        - Creates and configures application pool with .NET 4.0 runtime
        - Creates website with specified bindings and physical path
        - Deploys content using Web Deploy (msdeploy.exe)
        - Sets appropriate file system permissions
        - Handles ARR configuration if proxy is enabled:
            * Installs ARR components if needed
            * Imports ARR configuration from XML files
            * Configures proxy settings

    Notes:
        - Script requires WebAdministration PowerShell module
        - Uses site_name for both website and app pool names
        - Expects website content at 'C:\\staging\\{site_name}.zip'
        - Includes ARR configuration only if proxy is enabled in IIS
        - Generated script is referenced in EB deployment manifest
    """
    binding_protocol_tuples = []
    invoke_arr_import_script_call = ""
    for binding in bindings:
        binding_string = binding.BindingInformation
        # Always add the binding information regardless of ARR status
        if binding_string and binding_string.strip():
            binding_protocol_tuples.append(
                f'"{binding_string.strip()}" = "{binding.Protocol.lower()}"'
            )
            # Only set ARR import script if ARR is enabled
            if _arr_enabled():
                invoke_arr_import_script_call = "Invoke-ARRImportScript"
    binding_protocol_powershell_array = "\n".join(binding_protocol_tuples)

    # Read the template script
    script_path = os.path.join(
        os.path.dirname(__file__), "migrate_scripts", "site_installer_template.ps1"
    )
    with open(script_path, "r") as source_file:
        script_template = source_file.read()

    # Replace placeholders in the template
    script_content = (
        script_template.replace("{site_name}", site_name)
        .replace(
            "{binding_protocol_powershell_array}", binding_protocol_powershell_array
        )
        .replace("{physical_path}", physical_path)
        .replace("{invoke_arr_import_script_call}", invoke_arr_import_script_call)
    )

    with open(
        os.path.join(upload_target_dir, "ebmigrateScripts", installation_script_name),
        "w",
    ) as file:
        file.write(script_content)

def write_custom_site_installer_script_remote(
    remote_connection,
    upload_target_dir: str,
    site_name: str,
    bindings: List["Binding"],
    physical_path: str,
    installation_script_name: str,
) -> None:
    """
    Generate a PowerShell script for installing and configuring an IIS website.

    Creates an installation script that will be referenced in the Elastic Beanstalk
    deployment manifest's custom section. The script handles complete website setup
    including app pool creation, website configuration, and permissions. If Application
    Request Routing (ARR) is enabled in IIS, additional ARR configuration is included.

    Args:
        upload_target_dir: Base directory for deployment artifacts
        site_name: Name of the IIS website to create
        bindings: List of IIS binding objects defining site endpoints
        physical_path: Physical path where website content will be deployed
        installation_script_name: Name of the PowerShell script file to generate

    Generated Script Features:
        - Creates and configures application pool with .NET 4.0 runtime
        - Creates website with specified bindings and physical path
        - Deploys content using Web Deploy (msdeploy.exe)
        - Sets appropriate file system permissions
        - Handles ARR configuration if proxy is enabled:
            * Installs ARR components if needed
            * Imports ARR configuration from XML files
            * Configures proxy settings

    Notes:
        - Script requires WebAdministration PowerShell module
        - Uses site_name for both website and app pool names
        - Expects website content at 'C:\\staging\\{site_name}.zip'
        - Includes ARR configuration only if proxy is enabled in IIS
        - Generated script is referenced in EB deployment manifest
    """
    binding_protocol_tuples = []
    invoke_arr_import_script_call = ""
    for binding in bindings:
        binding_string = binding.BindingInformation
        # Always add the binding information regardless of ARR status
        if binding_string and binding_string.strip():
            binding_protocol_tuples.append(
                f'"{binding_string.strip()}" = "{binding.Protocol.lower()}"'
            )
            # Only set ARR import script if ARR is enabled
            if _arr_enabled_remote(remote_connection):
                invoke_arr_import_script_call = "Invoke-ARRImportScript"
    binding_protocol_powershell_array = "\n".join(binding_protocol_tuples)

    # Read the template script
    script_path = os.path.join(
        os.path.dirname(__file__), "migrate_scripts", "site_installer_template.ps1"
    )
    with open(script_path, "r") as source_file:
        script_template = source_file.read()

    # Replace placeholders in the template
    script_content = (
        script_template.replace("{site_name}", site_name)
        .replace(
            "{binding_protocol_powershell_array}", binding_protocol_powershell_array
        )
        .replace("{physical_path}", physical_path)
        .replace("{invoke_arr_import_script_call}", invoke_arr_import_script_call)
    )

    with open(
        os.path.join(upload_target_dir, "ebmigrateScripts", installation_script_name),
        "w",
    ) as file:
        file.write(script_content)


def write_custom_site_removal_script(
    upload_target_dir: str, site_name: str, uninstallation_script_name: str
) -> None:
    """
    Generate a PowerShell script for removing an IIS website during uninstallation.

    Creates an uninstallation script that will be referenced in the Elastic Beanstalk
    deployment manifest's custom section, typically used as an uninstall script
    in a custom deployment action.

    Args:
        upload_target_dir: Base directory for deployment artifacts
        site_name: Name of the IIS website to remove
        uninstallation_script_name: Name of the PowerShell script file to generate
                                   (must have .ps1 extension)

    Notes:
        - Creates script in '{upload_target_dir}/ebmigrateScripts/{uninstallation_script_name}'
        - Generated script requires WebAdministration PowerShell module
        - Script includes utility functions from ebdeploy_utils.ps1
    """
    # Read the template script
    script_path = os.path.join(
        os.path.dirname(__file__), "migrate_scripts", "site_removal_template.ps1"
    )
    with open(script_path, "r") as source_file:
        script_template = source_file.read()

    # Replace the site_name placeholder
    script_contents = script_template.replace("{site_name}", site_name)

    with open(
        os.path.join(upload_target_dir, "ebmigrateScripts", uninstallation_script_name),
        "w",
    ) as file:
        file.write(script_contents)


def write_custom_site_restarter_script(
    upload_target_dir: str, site_name: str, restarter_script_name: str
) -> None:
    """
    Generate a PowerShell script for restarting an IIS website during deployment.

    Creates a restart script that will be referenced in the Elastic Beanstalk
    deployment manifest's custom section, typically used as a restart script
    in a custom deployment action.

    Args:
        upload_target_dir: Base directory for deployment artifacts
        site_name: Name of the IIS website to restart
        restarter_script_name: Name of the PowerShell script file to generate
                             (must have .ps1 extension)

    Notes:
        - Creates script in '{upload_target_dir}/ebmigrateScripts/{restarter_script_name}'
        - Generated script requires WebAdministration PowerShell module
        - Script includes utility functions from ebdeploy_utils.ps1
    """
    # Read the template script
    script_path = os.path.join(
        os.path.dirname(__file__), "migrate_scripts", "site_restart_template.ps1"
    )
    with open(script_path, "r") as source_file:
        script_template = source_file.read()

    # Replace the site_name placeholder
    script_contents = script_template.replace("{site_name}", site_name)

    with open(
        os.path.join(upload_target_dir, "ebmigrateScripts", restarter_script_name), "w"
    ) as file:
        file.write(script_contents)


def write_default_web_site_port_reassignment_script(
    upload_target_dir: str, binding: "Binding", port_reassignment_script_name: str
) -> None:
    """
    Generate a PowerShell script for IIS Default Web Site port reassignment.

    Args:
        upload_target_dir: Base directory for deployment artifacts
        binding: IIS Binding object containing the target binding configuration
        port_reassignment_script_name: Name of the PowerShell script file to generate
                                     (must have .ps1 extension)

    Notes:
        - Creates script in '{upload_target_dir}/ebmigrateScripts/{port_reassignment_script_name}'
        - Generated script requires WebAdministration PowerShell module
        - Script includes utility functions from ebdeploy_utils.ps1
    """
    host, port, domain = binding.BindingInformation.split(":")

    # Read the template script
    script_path = os.path.join(
        os.path.dirname(__file__),
        "migrate_scripts",
        "default_web_site_port_reassignment_template.ps1",
    )
    with open(script_path, "r") as source_file:
        script_template = source_file.read()

    # Replace placeholders in the template
    script_content = (
        script_template.replace("{host}", host)
        .replace("{port}", port)
        .replace("{domain}", domain)
    )

    with open(
        os.path.join(
            upload_target_dir, "ebmigrateScripts", port_reassignment_script_name
        ),
        "w",
    ) as file:
        file.write(script_content)


def write_ebdeploy_utility_script(upload_target_dir: str) -> None:
    """
    Generate a PowerShell utility script containing common deployment functions.

    Creates ebdeploy_utils.ps1, a shared PowerShell module used by other deployment
    scripts. This utility script provides common functions for logging and ACL
    management during the Elastic Beanstalk deployment process.

    Args:
        upload_target_dir: Base directory for deployment artifacts. The script will be
            written to '{upload_target_dir}/ebmigrateScripts/ebdeploy_utils.ps1'

    Notes:
        - Script is imported by other deployment scripts using dot-sourcing
        - All logging functions use UTC timestamps for consistency
        - ACL rules include both container and object inheritance
        - All access rules are "Allow" type
    """
    script_path = os.path.join(
        os.path.dirname(__file__), "migrate_scripts", "ebdeploy_utils.ps1"
    )
    with open(script_path, "r") as source_file:
        script_content = source_file.read()

    with open(
        os.path.join(upload_target_dir, "ebmigrateScripts", "ebdeploy_utils.ps1"), "w"
    ) as file:
        file.write(script_content)


def write_copy_firewall_config_script(
    upload_target_dir: str, sites: List["Site"]
) -> None:
    """
    Generate and configure deployment of Windows Firewall rules based on IIS site bindings.

    Creates a PowerShell script that replicates the source environment's firewall
    configuration on the target environment. The script is added to the Elastic Beanstalk
    deployment manifest for execution during deployment.

    The function:
    1. Extracts HTTP/HTTPS ports from IIS site bindings
    2. Retrieves existing firewall rules for those ports
    3. Generates New-NetFirewallRule commands for each rule
    4. Creates a deployment script in the ebmigrateScripts directory
    5. Adds the script to the deployment manifest's custom section

    Args:
        upload_target_dir: Base directory for deployment artifacts. The script will be
            written to '{upload_target_dir}/ebmigrateScripts/modify_firewall_config.ps1'

    Notes:
        - Only processes HTTP and HTTPS site bindings
        - Generates inbound firewall rules only
        - Preserves original rule properties:
            * Display name
            * Action (Allow/Block)
            * Protocol
            * Port specifications
            * Enabled state
        - Uses noop.ps1 for restart and uninstall operations
        - If no relevant firewall rules are found, no script is generated
        - Modifies aws-windows-deployment-manifest.json to include the script

    Warning:
        Current implementation does not handle cleanup of firewall rules when
        sites are removed. Firewall rules persist after site removal.
    """
    ports = set()
    for site in sites:
        for binding in site.Bindings:
            host, port, domain = binding.BindingInformation.split(":")
            protocol = binding.Protocol
            if protocol in ["http", "https"]:
                ports.add(port.strip())
    firewall_rules = get_firewall_rules(ports)
    powershell_commands = []
    for rule in firewall_rules:
        command = (
            f'New-NetFirewallRule -DisplayName "{rule["Name"]}" '
            f'-Direction Inbound -Action {rule["Action"]} '
            f'-Protocol {rule["Protocol"]} -LocalPort {rule["LocalPorts"]} '
        )
        if not rule["Enabled"]:
            command += "-Enabled False"

        powershell_commands.append(command)
    if not powershell_commands:
        return

    # Read the template script
    script_path = os.path.join(
        os.path.dirname(__file__), "migrate_scripts", "modify_firewall_config.ps1"
    )
    with open(script_path, "r") as source_file:
        script_template = source_file.read()

    # Replace the placeholder with the actual firewall commands
    script_content = script_template.replace(
        "{firewall_rules}", "\n".join(powershell_commands)
    )

    with open(
        os.path.join(
            upload_target_dir, "ebmigrateScripts", "modify_firewall_config.ps1"
        ),
        "w",
    ) as file:
        file.write(script_content)

    with open(
        os.path.join(upload_target_dir, "aws-windows-deployment-manifest.json")
    ) as file:
        manifest = json.load(file)
        manifest["deployments"]["custom"].append(
            create_custom_manifest_section(
                "ModifyFirewallConfig",
                "modify_firewall_config.ps1",
                "noop.ps1",
                "noop.ps1",
            )
        )
    with open(
        os.path.join(upload_target_dir, "aws-windows-deployment-manifest.json"), "w"
    ) as file:
        json.dump(manifest, file, indent=4)


def create_custom_manifest_section(
    section_name: str,
    install_file: str,
    restart_file: str,
    uninstall_file: str,
    description: Optional[str] = None,
) -> Dict[str, any]:
    """
    Create a custom deployment section for the AWS Windows Deployment Manifest.

    Generates a configuration dictionary for the 'custom' section of an Elastic Beanstalk
    Windows deployment manifest. This section defines PowerShell scripts to be executed
    during installation, restart, and uninstallation phases of deployment.

    Args:
        section_name: Name identifier for this custom deployment section
        install_file: Name of PowerShell script to run during installation
        restart_file: Name of PowerShell script to run during restart
        uninstall_file: Name of PowerShell script to run during uninstallation
        description: Optional description of the deployment section.
                    Defaults to section_name if not provided.

    Returns:
        Dictionary containing the custom deployment section configuration:
            {
                "name": section name,
                "description": section description,
                "scripts": {
                    "install": {"file": "ebmigrateScripts\\install_script.ps1"},
                    "restart": {"file": "ebmigrateScripts\\restart_script.ps1"},
                    "uninstall": {"file": "ebmigrateScripts\\uninstall_script.ps1"}
                }
            }

    Notes:
        - All scripts are expected to be in the 'ebmigrateScripts' directory
        - This section will be added to the 'custom' array in the manifest
        - The manifest is used by Elastic Beanstalk to orchestrate deployments
    """
    ebmigrate_scripts_dir_name = "ebmigrateScripts"
    return {
        "name": section_name,
        "description": description or section_name,
        "scripts": {
            "install": {"file": f"{ebmigrate_scripts_dir_name}\\{install_file}"},
            "restart": {"file": f"{ebmigrate_scripts_dir_name}\\{restart_file}"},
            "uninstall": {"file": f"{ebmigrate_scripts_dir_name}\\{uninstall_file}"},
        },
    }


def is_port_in_rule(port: Union[int, str], local_ports: str) -> bool:
    """
    Check if a specific port is covered by a Windows Firewall rule's port specification.

    Evaluates whether a port number matches a firewall rule's local ports definition,
    handling both individual ports and port ranges.

    Args:
        port: Port number to check (can be integer or string)
        local_ports: Port specification string from firewall rule. Can be:
            - Individual ports: "80", "443"
            - Port ranges: "8081-8083"
            - Multiple specifications: "80,443,8081-8083"
            - "*" (all ports)

    Returns:
        True if the port is covered by the local_ports specification,
        False otherwise

    Notes:
        - Returns False for empty port specifications or "*"
        - Handles comma-separated lists of port specifications
        - Port ranges must be numeric and properly formatted (start-end)
        - Whitespace around port specifications is ignored

    Examples:
        >>> is_port_in_rule(80, "80")
        True
        >>> is_port_in_rule(80, "80,443")
        True
        >>> is_port_in_rule(8082, "8081-8083")
        True
        >>> is_port_in_rule(8080, "*")
        False
    """
    if not local_ports or local_ports == "*":
        return False

    port = str(port)
    for part in local_ports.split(","):
        part = part.strip()
        # Handle ports specified as ranges. e.g. 8081-8083
        if "-" in part:
            start, end = part.split("-")
            if start.isdigit() and end.isdigit():
                if int(start) <= int(port) <= int(end):
                    return True
        elif part == port:
            return True
    return False


def get_firewall_rules(ports_to_check: Set[int]) -> List[Dict[str, Any]]:
    """
    Retrieve Windows Firewall rules that apply to specified HTTP/HTTPS ports.

    Uses the Windows Firewall COM interface (INetFwPolicy2) to enumerate firewall rules
    and filter those that affect the specified ports.

    Args:
        ports_to_check: Set of port numbers (typically HTTP/HTTPS ports) to check
                       for associated firewall rules

    Returns:
        List of dictionaries, each representing a firewall rule with:
            - Name: Rule name (str)
            - ServiceName: Associated Windows service name (str)
            - Protocol: 'TCP' or 'UDP'
            - LocalPorts: Port specification string
            - Action: 'Allow' or 'Block'
            - Enabled: Boolean indicating if rule is active

    Raises:
        EnvironmentError: If unable to access or query the Windows Firewall

    Notes:
        - Uses Windows Firewall COM interface (HNetCfg.FwPolicy2)
        - Only includes rules that explicitly reference the specified ports
        - Protocol values are mapped from:
            * 6 -> 'TCP'
            * 17 -> 'UDP'
        - Action values are mapped from:
            * 1 -> 'Allow'
            * 2 -> 'Block'
    """
    try:
        fw_policy = win32com.client.Dispatch("HNetCfg.FwPolicy2")
    except Exception as e:
        io.log_error(
            f"Encountered failure during firewall configuration analysis: {str(e)}"
        )
        raise EnvironmentError(e)

    rules = fw_policy.Rules
    rule_list = []

    for rule in rules:
        if rule.LocalPorts and any(
            is_port_in_rule(p, rule.LocalPorts) for p in ports_to_check
        ):
            rule_list.append(
                {
                    "Name": rule.Name,
                    "ServiceName": rule.ServiceName,
                    "Protocol": "TCP" if rule.Protocol == 6 else "UDP",
                    "LocalPorts": rule.LocalPorts,
                    "Action": "Allow" if rule.Action == 1 else "Block",
                    "Enabled": rule.Enabled,
                }
            )
    return rule_list


def write_reinstate_iisstart_htm_default_document_script(
    upload_target_dir: str,
) -> None:
    """
    Generate a PowerShell script to restore IIS's default document configuration.

    Creates a PowerShell script that ensures 'iisstart.htm' is reinstated as a default
    document in IIS's configuration. This is necessary because Elastic Beanstalk's
    deployment process removes 'iisstart.htm' from IIS's default document list, which
    can affect sites relying on this default document behavior.

    Default documents in IIS determine which files (e.g., 'iisstart.htm', 'default.htm',
    'index.html') are served when a user requests a directory without specifying a
    specific file.

    Args:
        upload_target_dir: Base directory for deployment artifacts. The script will be
            written to '{upload_target_dir}/ebmigrateScripts/reinstate_iisstart_htm_default_document.ps1'

    Notes:
        - Script execution is managed by Elastic Beanstalk through its manifest file
        - The manifest entry ensures this script runs during deployment
        - Uses Add-WebConfigurationProperty cmdlet to modify IIS configuration
        - Modifies system.webServer/defaultDocument/files configuration section
        - Script is typically deployed to '.\\migrations\\latest\\upload_target\\ebmigrateScripts\'
        - Requires IIS WebAdministration module to be available on target system
    """
    script_path = os.path.join(
        os.path.dirname(__file__),
        "migrate_scripts",
        "reinstate_iisstart_htm_default_document.ps1",
    )
    with open(script_path, "r") as source_file:
        script_contents = source_file.read()

    with open(
        os.path.join(
            upload_target_dir,
            "ebmigrateScripts",
            "reinstate_iisstart_htm_default_document.ps1",
        ),
        "w",
    ) as file:
        file.write(script_contents)


# TODO: allow override through .ebextensions or a `--alb-configs alb-configs.json`
def get_listener_configs(sites: List["Site"], remote, remote_connection, ssl_certificate_domain_name: str = None) -> dict:
    """
    Generate complete Elastic Beanstalk listener configurations from IIS site configurations.

    Processes IIS sites to create comprehensive ALB listener configurations, including HTTP
    and HTTPS listeners, rules, and process mappings. Handles both protocol types and
    automatically determines default processes.

    Args:
    sites: List of IIS Site objects to generate listener configs from
    ssl_certificate_domain_name: Optional ARN of SSL certificate for HTTPS listeners.
        Required if any HTTPS listeners are configured.

    Returns:
        List of Elastic Beanstalk option settings containing:
            - HTTP/HTTPS listener configurations with default processes
            - Listener rules with priorities and conditions
            - Process configurations with ports and protocols
            - Protocol mappings for each target group
        Returns empty list if no valid listener rules are found or on error.

    Notes:
        - Processes sites to extract bindings and create corresponding ALB rules
        - Handles both HTTP and HTTPS protocols if certificate provided
        - Creates process mappings based on port numbers
        - Assigns rule priorities based on specificity
        - Treats configuration errors as non-fatal
    """
    option_settings = []
    try:
        site_configs = get_site_configs_remote(remote_connection, sites=sites) if remote else get_site_configs(sites=sites)
        alb_rules = create_alb_rules(site_configs)

        converted_alb_rules = convert_alb_rules_to_option_settings(
            alb_rules, ssl_certificate_domain_name
        )
        http_listener_rule_option_settings = (
            converted_alb_rules.http_listener_rule_option_settings
        )
        if ssl_certificate_domain_name:
            https_listener_rule_option_settings = (
                converted_alb_rules.https_listener_rule_option_settings
            )
        else:
            https_listener_rule_option_settings = []
        process_protocol_mappings = converted_alb_rules.process_protocol_mappings

        if (
            not http_listener_rule_option_settings
            and not https_listener_rule_option_settings
        ):
            return []

        http_listener_rule_names = _extract_and_join_rule_names(
            http_listener_rule_option_settings
        )
        if ssl_certificate_domain_name:
            https_listener_rule_names = _extract_and_join_rule_names(
                https_listener_rule_option_settings
            )
        else:
            https_listener_rule_names = []

        http_processes = _extract_process_values(http_listener_rule_option_settings)
        if ssl_certificate_domain_name:
            https_processes = _extract_process_values(
                https_listener_rule_option_settings
            )
        else:
            https_processes = []

        default_process_name = None
        if "default" in http_processes:
            default_process_name = "default"
        elif http_processes:
            default_process_name = sorted(list(http_processes))[0]

        default_https_process_name = None
        if https_processes:
            default_https_process_name = sorted(list(https_processes))[0]

        option_settings.extend(
            _create_http_listener_settings(
                default_process_name, http_listener_rule_names
            )
        )

        if https_listener_rule_option_settings:
            option_settings.extend(
                _create_https_listener_settings(
                    default_https_process_name,
                    https_listener_rule_names,
                    ssl_certificate_domain_name,
                )
            )

        process_option_settings = _create_process_option_settings(
            process_protocol_mappings
        )

        option_settings += (
            http_listener_rule_option_settings
            + https_listener_rule_option_settings
            + process_option_settings
        )

        return option_settings
    except Exception as e:
        import traceback
        io.log_warning(
            f"Error: {str(e)}. Treating listener rule creation as non-fatal. This might cause environment to be in degraded state."
        )
        io.log_warning(f"Traceback: {traceback.format_exc()}")


def _create_process_option_settings(
    process_protocol_mappings: Dict[str, str],
) -> List[dict]:
    """
    Create Elastic Beanstalk process option settings from process-protocol mappings.

    Generates configuration settings for each process, including protocol and port settings.
    The 'default' process is mapped to port 80, while other processes use their name as the port.

    Args:
        process_protocol_mappings: Dictionary mapping process names to their protocols
            (e.g., {'default': 'HTTP', '8080': 'HTTPS'})

    Returns:
        List of option settings dictionaries, each containing:
            - Namespace: AWS namespace for the process (aws:elasticbeanstalk:environment:process:{process})
            - OptionName: Either 'Protocol' or 'Port'
            - Value: The corresponding protocol or port value

    Example:
        >>> _create_process_option_settings({'default': 'HTTP', '8080': 'HTTPS'})
        [
            {
                'Namespace': 'aws:elasticbeanstalk:environment:process:default',
                'OptionName': 'Protocol',
                'Value': 'HTTP'
            },
            {
                'Namespace': 'aws:elasticbeanstalk:environment:process:default',
                'OptionName': 'Port',
                'Value': '80'
            },
            {
                'Namespace': 'aws:elasticbeanstalk:environment:process:8080',
                'OptionName': 'Protocol',
                'Value': 'HTTPS'
            },
            {
                'Namespace': 'aws:elasticbeanstalk:environment:process:8080',
                'OptionName': 'Port',
                'Value': '8080'
            }
        ]
    """
    settings = []
    for process, protocol in process_protocol_mappings.items():
        port = "80" if process == "default" else process
        namespace = f"aws:elasticbeanstalk:environment:process:{process}"
        settings.extend(
            [
                {
                    "Namespace": namespace,
                    "OptionName": "Protocol",
                    "Value": protocol.upper(),
                },
                {"Namespace": namespace, "OptionName": "Port", "Value": port},
            ]
        )
    return settings


def _create_listener_settings(
    namespace: str, option_name_value_pairs: List[Tuple[str, str]]
) -> List[dict]:
    """
    Create Elastic Beanstalk listener option settings from name-value pairs.

    Args:
        namespace: The AWS Elastic Beanstalk namespace for the settings
        option_name_value_pairs: List of tuples containing (option_name, value) pairs

    Returns:
        List of dictionaries, each containing:
            - Namespace: The provided namespace
            - OptionName: Name of the option
            - Value: Value for the option
    """
    return [
        {"Namespace": namespace, "OptionName": option_name, "Value": value}
        for option_name, value in option_name_value_pairs
    ]


def _create_http_listener_settings(
    default_process_name: str, rule_names: str
) -> List[dict]:
    """
    Create HTTP listener configuration settings for Elastic Beanstalk.

    Creates settings for an HTTP listener with specified default process and rules.

    Args:
        default_process_name: Name of the default process to handle requests
        rule_names: Comma-separated string of rule names

    Returns:
        List of option settings configuring an HTTP listener with:
            - HTTP protocol
            - Specified default process
            - Enabled listener
            - Specified routing rules
    """
    option_name_value_pairs = [
        ("Protocol", "HTTP"),
        ("DefaultProcess", default_process_name),
        ("ListenerEnabled", "true"),
        ("Rules", rule_names),
    ]
    return _create_listener_settings(
        "aws:elbv2:listener:default", option_name_value_pairs
    )


def _create_https_listener_settings(
    default_process_name: str, rule_names: str, ssl_cert: str
) -> List[dict]:
    """
    Create HTTPS listener configuration settings for Elastic Beanstalk.

    Creates settings for an HTTPS listener with specified default process, rules,
    and SSL certificate.

    Args:
        default_process_name: Name of the default process to handle requests
        rule_names: Comma-separated string of rule names
        ssl_cert: ARN of the SSL certificate to use for HTTPS

    Returns:
        List of option settings configuring an HTTPS listener with:
            - HTTPS protocol
            - Specified default process
            - Enabled listener
            - Specified routing rules
            - SSL certificate configuration
    """
    option_name_value_pairs = [
        ("Protocol", "HTTPS"),
        ("DefaultProcess", default_process_name),
        ("ListenerEnabled", "true"),
        ("Rules", rule_names),
    ]
    if ssl_cert:
        option_name_value_pairs.append(("SSLCertificate", ssl_cert))
    return _create_listener_settings("aws:elbv2:listener:443", option_name_value_pairs)


def _extract_and_join_rule_names(option_settings: List[dict]) -> str:
    rule_names = {option["Namespace"].split(":")[-1] for option in option_settings}
    return ",".join(sorted(rule_names))


def _extract_process_values(option_settings: List[dict]) -> Set[str]:
    return {
        setting["Value"]
        for setting in option_settings
        if setting["OptionName"] == "Process"
    }


@dataclass
class ConvertedALBRules:
    """
    Container for ALB rule configurations separated by protocol.

    Attributes:
        http_listener_rule_option_settings: List of option settings for HTTP listener rules
        https_listener_rule_option_settings: List of option settings for HTTPS listener rules
        process_protocol_mappings: Dictionary mapping process names to their protocols
    """

    http_listener_rule_option_settings: List[Dict[str, str]]
    https_listener_rule_option_settings: List[Dict[str, str]]
    process_protocol_mappings: Dict[str, str]


def convert_alb_rules_to_option_settings(
    alb_rules: List[Dict[str, Any]], ssl_certificate_domain_name: Optional[str]
) -> ConvertedALBRules:
    """
    Convert ALB rules into Elastic Beanstalk option settings format.

    Transforms ALB rules into EB option settings, organizing them by protocol (HTTP/HTTPS)
    and creating the necessary listener rule configurations.

    Args:
        alb_rules: List of ALB rule dictionaries, each containing:
            - Priority: Rule priority number
            - Protocol: 'HTTP' or 'HTTPS'
            - Conditions: List of routing conditions (host-headers, path-pattern)
            - Actions: Forward actions with target group configuration

    Returns:
        ConvertedALBRules object containing:
            - HTTP listener rule options
            - HTTPS listener rule options
            - Process to protocol mappings

    Each listener rule option is a dictionary with:
        - Namespace: 'aws:elbv2:listenerrule:ruleN' where N is the rule number
        - OptionName: One of 'Priority', 'Process', 'HostHeaders', or 'PathPatterns'
        - Value: Corresponding value for the option

    Notes:
        - Process names are extracted from target group ARNs
        - Port 80 is mapped to 'default' process name
        - If no host header is specified, path pattern defaults to '*'
    """
    http_listener_rule_option_settings: List[Dict[str, str]] = []
    https_listener_rule_option_settings: List[Dict[str, str]] = []
    process_protocol_mappings: Dict[str, str] = dict()

    for i, rule in enumerate(alb_rules, 1):
        host_header, path_pattern = None, None

        conditions = rule.get("Conditions", [])
        if conditions:
            for condition in conditions:
                if condition["Field"] == "host-header":
                    host_header = condition["Values"][0]
                if condition["Field"] == "path-pattern":
                    path_pattern = condition["Values"][0]

        namespace = f"aws:elbv2:listenerrule:rule{i}"
        protocol = rule["Protocol"].upper()
        listener_rule_option_settings = list()
        listener_rule_option_settings.append(
            {
                "Namespace": namespace,
                "OptionName": "Priority",
                "Value": str(rule["Priority"]),
            }
        )

        target_group = rule["Actions"][0]["ForwardConfig"]["TargetGroups"][0][
            "TargetGroupArn"
        ]
        process = target_group.split("/")[-1]
        if process == "80":
            process = "default"
        listener_rule_option_settings.append(
            {"Namespace": namespace, "OptionName": "Process", "Value": process}
        )
        if host_header:
            listener_rule_option_settings.append(
                {
                    "Namespace": namespace,
                    "OptionName": "HostHeaders",
                    "Value": host_header,
                }
            )
        if not host_header:
            path_pattern = path_pattern or "*"
        if path_pattern:
            listener_rule_option_settings.append(
                {
                    "Namespace": namespace,
                    "OptionName": "PathPatterns",
                    "Value": path_pattern,
                }
            )
        if protocol.strip().lower() == "http":
            http_listener_rule_option_settings.extend(listener_rule_option_settings)
        else:
            https_listener_rule_option_settings.extend(listener_rule_option_settings)
        if protocol.strip().lower() == "http":
            process_protocol_mappings[process] = protocol.strip().upper()
        elif protocol.strip().lower() == "https" and ssl_certificate_domain_name:
            process_protocol_mappings[process] = protocol.strip().upper()

    return ConvertedALBRules(
        http_listener_rule_option_settings,
        https_listener_rule_option_settings,
        process_protocol_mappings,
    )


class SiteConfig:
    """
    Configuration class representing an IIS website with its binding and path information.

    Args:
        name: The name of the IIS website
        binding_info: A colon-separated string containing binding information in the format
                     "ip:port:hostname". Example: "*:80:example.com"
        physical_path: The filesystem path where the website content is located
        protocol: The web protocol used by the site ('http' or 'https')

    Attributes:
        name (str): The name of the IIS website
        port (int): The port number extracted from binding_info
        host_header (Optional[str]): The hostname for the site, or None if not specified
        physical_path (str): The filesystem path where the website content is located
        protocol (str): The lowercase protocol ('http' or 'https')
        rewrite_rules (List): A list of rewrite rules for the site (empty by default)

    Raises:
        ValueError: If binding_info doesn't contain enough segments for parsing
    """

    def __init__(
        self, name: str, binding_info: str, physical_path: str, protocol: str
    ) -> None:
        self.name = name
        self.port = int(binding_info.split(":")[1])
        self.host_header = binding_info.split(":")[2] or None
        self.physical_path = physical_path
        self.protocol = protocol.lower()
        self.rewrite_rules: List = []


def _parse_binding_info(binding: "Binding") -> Dict[str, Union[str, int]]:
    """
    Parse an IIS binding configuration into a dictionary of its components.

    Takes a Binding object from IIS's configuration and splits its BindingInformation
    string (format: "IP:port:hostname") into individual components.

    Args:
        binding: An IIS Binding object containing BindingInformation and Protocol properties

    Returns:
        A dictionary containing:
            - 'ip' (str): IP address or '*' for all addresses
            - 'port' (int): Port number
            - 'host' (str): Hostname or empty string if not specified
            - 'protocol' (str): Protocol type ('http' or 'https')

    Raises:
        IndexError: If binding.BindingInformation doesn't contain the expected three colon-separated values
    """
    parts = binding.BindingInformation.split(":")
    return {
        "ip": parts[0],
        "port": int(parts[1]),
        "host": parts[2],
        "protocol": binding.Protocol,  # This should give us http/https
    }


def get_site_configs(sites: List["Site"]):
    """
    Retrieve and parse IIS site configurations from the local server.

    Connects to IIS using ServerManager and processes each site's:
    - Basic site information (name, bindings)
    - Physical path information
    - URL rewrite rules from web.config files

    Args:
    sites: List of IIS Site objects to process

    Returns:
        List[SiteConfig]: A list of SiteConfig objects, each containing:
            - name: Site name from IIS
            - binding_info: Parsed binding information (ip:port:hostname)
            - physical_path: Site's root directory path
            - protocol: HTTP/HTTPS protocol
            - rewrite_rules: List of dictionaries containing URL rewrite rules from web.config:
                * name: Rule name
                * pattern: URL pattern to match
                * action_type: Type of rewrite action (Rewrite/Redirect)
                * action_url: Target URL for rewrite

    Notes:
        - Processes each site's bindings separately
        - Parses web.config files for URL rewrite rules
        - Skips invalid web.config files with warning
        - Requires administrative access to IIS
    """
    site_configs = []

    for site in sites:
        for binding in site.Bindings:
            binding_info = _parse_binding_info(binding)

            config = SiteConfig(
                name=site.Name,
                binding_info=binding.BindingInformation,
                physical_path=site.Applications["/"]
                .VirtualDirectories["/"]
                .PhysicalPath,
                protocol=binding_info["protocol"],
            )

            # Get rewrite rules from web.config
            web_config_path = os.path.join(config.physical_path, "web.config")
            if os.path.exists(web_config_path):
                try:
                    tree = ET.parse(web_config_path)
                    root = tree.getroot()
                    rules = root.findall(".//rewrite/rules/rule")

                    for rule in rules:
                        config.rewrite_rules.append(
                            {
                                "name": rule.get("name"),
                                "pattern": rule.find("match").get("url"),
                                "action_type": rule.find("action").get("type"),
                                "action_url": rule.find("action").get("url"),
                            }
                        )
                except Exception as e:
                    io.log_warning(
                        f"Error reading web.config for {site.Name}: {str(e)}. Skipping over rewrite rule identification for {site.Name}"
                    )

            site_configs.append(config)

    return site_configs

def get_site_configs_remote(remote_connection, sites: List["Site"]) -> "SiteConfig":
    site_configs = []

    for site in sites:
        for binding in site.Bindings:
            binding_info = _parse_binding_info(binding)
            physical_path = None
            for app in site.Applications:
                if app.Path == "/":
                    for vdir in app.VirtualDirectories:
                        if vdir.Path == "/":
                            physical_path = vdir.PhysicalPath
                            break
                    break
            config = SiteConfig(
                name=site.Name,
                binding_info=binding.BindingInformation,
                physical_path=physical_path,
                protocol=binding_info["protocol"],
            )

            # Get rewrite rules from web.config remotely
            if "SystemDrive" in config.physical_path:
                web_config_path = config.physical_path.replace("%SystemDrive%", "")  # This will leave \inetpub\wwwroot
                web_config_path = windows_path_join(web_config_path, "web.config")
                # Check if web.config exists remotely
                ps_check_file = f'''
                $path = $env:SystemDrive + "{web_config_path}"
                if (Test-Path -Path $path -PathType Leaf) {{
                    Write-Output "EXISTS"
                }} else {{
                    Write-Output "NOT_EXISTS"
                }}
                '''
                command_bytes = ps_check_file.encode('utf-16le')
                encoded_command = base64.b64encode(command_bytes).decode()
                result = remote_connection.run(f'powershell -NoProfile -NonInteractive -EncodedCommand {encoded_command}', hide=True)
                file_exists = result.stdout.strip() == "EXISTS"
            else:
                web_config_path = windows_path_join(config.physical_path, "web.config")
                # Check if web.config exists remotely
                ps_check_file = f'''
                $path = "{web_config_path}"
                if (Test-Path -Path $path -PathType Leaf) {{
                    Write-Output "EXISTS"
                }} else {{
                    Write-Output "NOT_EXISTS"
                }}
                '''
                command_bytes = ps_check_file.encode('utf-16le')
                encoded_command = base64.b64encode(command_bytes).decode()
                result = remote_connection.run(f'powershell -NoProfile -NonInteractive -EncodedCommand {encoded_command}', hide=True)
                file_exists = result.stdout.strip() == "EXISTS"
            
            if file_exists:
                try:
                    # Read web.config content remotely
                    ps_read_file = f'''
                    $webConfigContent = Get-Content -Path "{web_config_path}" -Raw
                    Write-Output $webConfigContent
                    '''
                    command_bytes = ps_read_file.encode('utf-16le')
                    encoded_command = base64.b64encode(command_bytes).decode()
                    result = remote_connection.run(f'powershell -NoProfile -NonInteractive -EncodedCommand {encoded_command}', hide=True)
                    web_config_content = result.stdout.strip()
                    
                    # Parse XML content
                    root = ET.fromstring(web_config_content)
                    rules = root.findall(".//rewrite/rules/rule")

                    for rule in rules:
                        match_element = rule.find("match")
                        action_element = rule.find("action")
                        
                        if match_element is not None and action_element is not None:
                            config.rewrite_rules.append({
                                "name": rule.get("name"),
                                "pattern": match_element.get("url"),
                                "action_type": action_element.get("type"),
                                "action_url": action_element.get("url"),
                            })
                except Exception as e:
                    io.log_warning(
                        f"Error reading web.config for {site.Name}: {str(e)}. Skipping over rewrite rule identification for {site.Name}"
                    )

            site_configs.append(config)

    return site_configs




def _sort_rules_by_specificity(rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort Application Load Balancer rules by their specificity in descending order.

    Rules are sorted based on a scoring system where:
    - Path pattern conditions contribute 20 points
    - Host header conditions contribute 10 points
    The total score determines the rule's specificity, with higher scores indicating
    more specific rules.

    Args:
        rules: A list of ALB rule dictionaries. Each rule is a dictionary containing:
            - 'Actions': List of action configurations
            - 'Protocol': String indicating the protocol (e.g., "http")
            - 'Conditions' (optional): List of condition dictionaries with 'Field' and 'Values'

    Returns:
        A new list containing the same rules sorted by specificity in descending order,
        where rules with more specific conditions (higher scores) appear first.

    Example:
        A rule with both path-pattern and host-header conditions (score: 30) would be
        sorted before a rule with only a host-header condition (score: 10).
    """

    def calculate_rule_specificity(rule):
        score = 0
        conditions = rule.get("Conditions", [])

        for condition in conditions:
            if condition["Field"] == "host-header":
                score += 10
            elif condition["Field"] == "path-pattern":
                score += 20
        return score

    return sorted(rules, key=calculate_rule_specificity, reverse=True)


def create_alb_rules(site_configs: List["SiteConfig"]) -> List[Dict[str, Any]]:
    """
        Create Application Load Balancer (ALB) rules from IIS site configurations.

        Transforms IIS site configurations into ALB rules by:
        1. Grouping sites by port
        2. Creating host-header based rules for each site
        3. Creating path-pattern based rules from site rewrite rules
        4. Sorting rules by specificity and assigning priorities

    Args:
        site_configs: List of SiteConfig objects containing IIS site configurations

        Returns:
            List of ALB rule dictionaries, each containing:
                - Priority: Integer indicating rule precedence (1-based)
                - Protocol: The protocol ('http' or 'https')
                - Actions: Forward action configuration with target group ARN
                - Conditions: List of conditions:
                    * host-header conditions from site bindings
                    * path-pattern conditions from rewrite rules

        Process Flow:
            1. Groups sites by port for target group creation
            2. Processes host-header based rules first
            3. Processes URL rewrite rules from web.config
            4. Sorts rules by specificity (host+path > host > path)
            5. Assigns sequential priorities to sorted rules

        Notes:
            - Creates synthetic target group ARNs using port numbers
            - Deduplicates patterns per host header
            - Only processes HTTP/HTTPS protocols
            - Host header rules take precedence over path patterns
    """
    port_groups = collections.defaultdict(list)
    valid_protocols = ["http", "https"]
    for config in site_configs:
        if config.protocol in valid_protocols:
            port_groups[config.port].append(config)

    target_group_template_arn = (
        "arn:aws:elasticloadbalancing:region:account-id:targetgroup/{port}"
    )
    target_groups = {
        port: target_group_template_arn.format(port=port) for port in port_groups.keys()
    }

    unsorted_rules = _process_host_header_based_rules(port_groups, target_groups)
    processed_patterns = set()
    rewrite_rules = _process_url_rewrite_rules(
        port_groups, processed_patterns, target_groups
    )
    unsorted_rules.extend(rewrite_rules)
    sorted_rules = _sort_rules_by_specificity(unsorted_rules)
    return _assign_priorities_after_sorting(sorted_rules)


def _process_host_header_based_rules(port_groups, target_groups):
    host_header_rules = []
    for iis_port, sites in port_groups.items():
        for site in sites:
            host_rule = {
                "Actions": [
                    {
                        "Type": "forward",
                        "ForwardConfig": {
                            "TargetGroups": [
                                {"TargetGroupArn": target_groups[iis_port], "Weight": 1}
                            ]
                        },
                    }
                ],
                "Protocol": site.protocol,
            }
            if site.host_header:
                host_rule["Conditions"] = [
                    {"Field": "host-header", "Values": [site.host_header]}
                ]
            host_header_rules.append(host_rule)
            continue
    return host_header_rules


def _process_url_rewrite_rules(port_groups, processed_patterns, target_groups):
    rules = []
    for iis_port, sites in port_groups.items():
        for site in sites:
            for rule in site.rewrite_rules:
                rewrite_rule = _process_url_rewrite_rule(
                    rule, processed_patterns, site, target_groups, iis_port
                )
                rules.append(rewrite_rule)
    return rules


def _process_url_rewrite_rule(rule, processed_patterns, site, target_groups, iis_port):
    # Create unique key for pattern+host combination
    pattern_key = f"{rule['pattern']}:{site.host_header}"

    # Skip if we've already processed this pattern for this host
    if pattern_key in processed_patterns:
        return None

    processed_patterns.add(pattern_key)

    conditions = []
    if site.host_header:
        conditions.append({"Field": "host-header", "Values": [site.host_header]})

    conditions.append(
        {"Field": "path-pattern", "Values": [translate_iis_to_alb(rule["pattern"])]}
    )

    return _create_rewrite_rule(conditions, target_groups[iis_port], site.protocol)


def _create_rewrite_rule(
    conditions: List[Dict[str, Union[str , List[str]]]], target_group_arn: str, protocol: str
) -> Dict[str, Any]:
    return {
        "Conditions": conditions,
        "Actions": [
            {
                "Type": "forward",
                "ForwardConfig": {
                    "TargetGroups": [{"TargetGroupArn": target_group_arn, "Weight": 1}]
                },
            }
        ],
        "Protocol": protocol,
    }


def _assign_priorities_after_sorting(
    sorted_rules: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    alb_rules = []
    for priority, rule in enumerate(sorted_rules, 1):
        rule["Priority"] = priority
        alb_rules.append(rule)
    return alb_rules


def translate_iis_to_alb(iis_pattern: str) -> str:
    """
    Convert an IIS (Internet Information Services) URL rewrite pattern to an ALB (Application Load Balancer) path pattern.

    This function takes a URL rewrite pattern typically used in IIS and transforms it into a format compatible with
    AWS Application Load Balancer (ALB) path patterns. The transformation involves several steps to simplify and
    standardize the pattern.

    Parameters:
    iis_pattern (str): The IIS URL rewrite pattern to be converted. This pattern may contain various regex elements
                       such as anchors, capture groups, character classes, and quantifiers.

    Returns:
    str: The converted ALB path pattern. This pattern will be simplified to use '*' as a wildcard character and
         will be prefixed with a '/' if it does not already start with one.

    Example:
    >>> translate_iis_to_alb("^/products/{id:int}/details$")
    '/products/*/details'
    >>> translate_iis_to_alb("^/users/([a-zA-Z0-9]+)/profile$")
    '/users/*/profile'
    >>> translate_iis_to_alb("/articles/(.*)")
    '/articles/*'

    Note:
    - The function assumes that the input pattern is a valid IIS URL rewrite pattern.
    - The resulting ALB pattern will use '*' as a wildcard to match any sequence of characters.
    - Complex regex features not covered by the simplification rules will be approximated with '*'.
    """
    alb_pattern = iis_pattern.strip("^$")

    # replace .+ with *
    alb_pattern = re.sub(r"\.\+", "?*", alb_pattern)
    # replace .* with *
    alb_pattern = re.sub(r"\.\*", "*", alb_pattern)
    # replace {segment} with *
    alb_pattern = re.sub("({.*})", "*", alb_pattern)
    alb_pattern = alb_pattern.lstrip("^")
    # replace groupings of the type "[0-9]+" with "*"
    alb_pattern = re.sub(r"\[.*?\]\+", "*", alb_pattern)
    # replace groupings of the type "[0-9]*" with "*"
    alb_pattern = re.sub(r"\[.*?\]\*", "*", alb_pattern)
    # replace groupings of the type "([0-9]*)" with "*"
    alb_pattern = re.sub(r"\([^()]*\)", "*", alb_pattern)

    # Ensure pattern starts with /
    if not alb_pattern.startswith("/"):
        alb_pattern = "/" + alb_pattern
    # Remove any double asterisks
    alb_pattern = alb_pattern.replace("**", "*")
    # Remove any trailing *
    alb_pattern = alb_pattern.rstrip("$")

    return alb_pattern

def windows_path_join(*args):
    return '\\'.join(arg.rstrip('\\') for arg in args)


def sanitize_windows_path(path):
    """
    Sanitize a path for Windows systems.

    This function:
    1. Replaces forward slashes with backslashes
    2. Normalizes multiple consecutive backslashes to single backslashes
    3. Removes trailing backslashes (unless it's a root drive path like "C:\")
    4. Handles UNC paths correctly

    Args:
        path (str): The path to sanitize

    Returns:
        str: A sanitized Windows path
    """
    if not path:
        return path

    # Replace forward slashes with backslashes
    sanitized_path = path.replace('/', '\\')

    # Normalize multiple consecutive backslashes to single backslashes
    # (except for UNC paths which start with \\)
    if sanitized_path.startswith('\\\\'):
        sanitized_path = '\\\\' + sanitized_path[2:].replace('\\\\', '\\')
    else:
        sanitized_path = sanitized_path.replace('\\\\', '\\')

    # Remove trailing backslash unless it's a root drive path like "C:\"
    if sanitized_path.endswith('\\') and not (len(sanitized_path) == 3 and sanitized_path[1] == ':'):
        sanitized_path = sanitized_path.rstrip('\\')

    return sanitized_path


def create_migration_folders_remote(remote_connection, bundle_dir_remote, upload_target_dir_remote):

    ps_command = f'''
    New-Item -Path "{bundle_dir_remote}" -ItemType Directory -Force
    New-Item -Path "{upload_target_dir_remote}" -ItemType Directory -Force
    Write-Host "Successfully created bundle and upload_target_dir directories"
    '''
    command_bytes = ps_command.encode('utf-16le')
    encoded_command = base64.b64encode(command_bytes).decode()
    result = remote_connection.run(f'powershell -NoProfile -NonInteractive -EncodedCommand {encoded_command}', hide=True)

    output = result.stdout.strip()

    return output
