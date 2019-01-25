# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
"""
IMPORTANT: Ensure you have reinstalled `awsebcli` from the commit you are testing!
"""
import os
import shutil
import subprocess
import sys
import threading
import types

from ebcli.core import fileoperations
from ebcli.core import io


class TestHelpTexts(object):
    maxDiff = None

    @classmethod
    def run(cls):
        cls.setUpClass()

        test_functions = [
            attr for attr in dir(cls)
            if
            attr.startswith('test_') and isinstance(getattr(cls, attr), types.FunctionType)
        ]

        while test_functions:
            test_function_threads = []
            for thread_index in range(min(16, len(test_functions))):
                class_instance = cls()
                test_function = test_functions.pop()
                test_thread = threading.Thread(target=getattr(cls, test_function), args=(class_instance,))
                test_thread.start()
                test_function_threads.append(test_thread)
            [t.join() for t in test_function_threads]

        cls.tearDownClass()


class HelpTestsMixin(object):
    def assertEqual(self, first, second):
        if first != second:
            raise AssertionError(
                """Expected:
{first}

Actual:

{second}""".format(
                    first=io.color('green', first),
                    second=io.color('red', second)
                   )
            )

    def output_of(self, args):
        (stdout, _) = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        string_output = stdout if sys.version_info < (3, 0) else stdout.decode()
        return string_output.strip().replace('\r\n', '\n')

    def test_eb_platform(self):
        self.assertEqual(
            """usage: eb platform <command> [options...]

Commands for managing platforms.
For more information on a specific command, enter "eb platform {cmd} --help".
To get started enter "eb platform init". Then enter "eb platform create".

application workspace commands:
  show                  Shows information about current platform.
  select                Selects a default platform.

platform workspace commands:
  init                  Initializes your directory with the EB CLI to create and manage Platforms.
  status                Displays metadata about your current custom platform version.
  use                   Selects the active custom platform version to use for this workspace.
  create                Creates a new custom platform version.
  delete                Deletes a custom platform version.
  events                Displays events for the custom platform associated with this workspace.
  logs                  Retrieves logs for your custom platform build event.

common commands:
  list                  In a platform workspace, lists versions of the custom platform associated with this workspace. Elsewhere, lists available platforms.

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'platform', '--help'])
        )

    def test_eb_platform_create(self):
        self.assertEqual(
            """usage: eb platform create <version> [options...]

Creates a new custom platform version.

positional arguments:
  version               platform version

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -M, --major-increment
                        major version increment
  -m, --minor-increment
                        minor version increment
  -p, --patch-increment
                        patch version increment
  -i INSTANCE_TYPE, --instance-type INSTANCE_TYPE
                        instance type i.e. t1.micro
  -ip INSTANCE_PROFILE, --instance_profile INSTANCE_PROFILE
                        the instance profile to use when creating AMIs for
                        custom platforms
  --vpc.id VPC_ID       specify id of VPC to launch Packer builder into
  --vpc.subnets VPC_SUBNETS
                        specify subnets to launch Packer builder into
  --vpc.publicip        associate public IPs to EC2 instances launched if
                        specified
  --timeout TIMEOUT     timeout period in minutes
  --tags TAGS           a comma separated list of tags as key=value pairs

Creates a new platform version. If no version is specified then it will do a patch-increment based on the most recent platform version. The version and increment options are mutually exclusive.
""".strip(),
            self.output_of(['eb', 'platform', 'create', '--help'])
        )

    def test_eb_platform_delete(self):
        self.assertEqual(
            """usage: eb platform delete <version> [options...]

Deletes a custom platform version.

positional arguments:
  version               platform version

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  --cleanup             remove all platform versions in the "Failed" state
  --all-platforms       enables cleanup for all of your platforms.
  --force               skip confirmation prompt

You must explicitly select the version to delete.
""".strip(),
            self.output_of(['eb', 'platform', 'delete', '--help'])
        )

    def test_eb_platform_events(self):
        self.assertEqual(
            """usage: eb platform events <version> [options...]

Displays events for the custom platform associated with this workspace.

positional arguments:
  version               version to retrieve events for

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -f, --follow          wait and continue to print events as they come
""".strip(),
            self.output_of(['eb', 'platform', 'events', '--help'])
        )

    def test_eb_platform_init(self):
        self.assertEqual(
            """usage: eb platform init <platform name> [options...]

Initializes your directory with the EB CLI to create and manage Platforms.
(Uninitialized or platform workspace only)

positional arguments:
  platform_name         platform name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -i, --interactive     force interactive mode
  -k KEYNAME, --keyname KEYNAME
                        default EC2 key name

This command is safe when run in a previously initialized directory. To re-initialize with different options, use the -i option. Note this command cannot change the workspace type of a directory that was already initialized.
""".strip(),
            self.output_of(['eb', 'platform', 'init', '--help'])
        )

    def test_eb_platform_list(self):
        self.assertEqual(
            """usage: eb platform list [options...]

In a platform workspace, lists versions of the custom platform associated with this workspace. You can reduce the result set by using filters.
Elsewhere, shows a list of platforms for use with "eb init -p". Enter "--verbose" to get the full platform name.

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -a, --all-platforms   lists the versions of all platforms owned by your account
                        (platform workspace only)
  -s STATUS, --status STATUS
                        the status that you wish to filter on (Ready, Failed, Deleting, Creating)
                        (platform workspace only)
""".strip(),
            self.output_of(['eb', 'platform', 'list', '--help'])
        )

    def test_eb_platform_logs(self):
        self.assertEqual(
            """usage: eb platform logs <version> [options...]

Retrieves logs for your custom platform build event.

positional arguments:
  version               platform version to retrieve logs for

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  --stream              enable/disable log streaming to CloudWatch Logs
""".strip(),
            self.output_of(['eb', 'platform', 'logs', '--help'])
        )

    def test_eb_platform_status(self):
        self.assertEqual(
            """usage: eb platform status <version> [options...]

Displays metadata about your current custom platform version.

positional arguments:
  version               platform version

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates

Will display details about the current version if no version is specified.
""".strip(),
            self.output_of(['eb', 'platform', 'status', '--help'])
        )

    def test_eb_platform_use(self):
        self.assertEqual(
            """usage: eb platform use <platform> [options...]

Selects the active custom platform version to use for this workspace.

positional arguments:
  platform              platform name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'platform', 'use', '--help'])
        )

    def test_ebp(self):
        self.assertEqual(
            """usage: ebp (sub-commands ...) [options ...] {arguments ...}

Welcome to the Elastic Beanstalk Command Line Interface (EB CLI).
The "ebp" command is equivalent to "eb platform". It offers sub-commands for managing platforms.
We recommend that you use "eb platform" instead of "ebp".
For more information on a specific command, enter "eb platform {cmd} --help".
To get started, enter "eb platform init". Then enter "eb platform create".

platform workspace commands:
  init                  Initializes your directory with the EB CLI to create and manage Platforms.
  create                Creates a new custom platform version.
  delete                Deletes a custom platform version.
  events                Displays events for the custom platform associated with this workspace.
  logs                  Retrieves logs for your custom platform build event.
  status                Displays metadata about your current custom platform version.
  use                   Selects the active custom platform version to use for this workspace.

common commands:
  list                  In a platform workspace, lists versions of the custom platform associated with this workspace. Elsewhere, lists available platforms.

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  --version             show application/version info

To get started type "ebp init". Then type "ebp create"
""".strip(),
            self.output_of(['ebp', '--help'])
        )

    def test_ebp_create(self):
        self.assertEqual(
            """usage: ebp create <version> [options...]

Creates a new custom platform version.

positional arguments:
  version               platform version

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -M, --major-increment
                        major version increment
  -m, --minor-increment
                        minor version increment
  -p, --patch-increment
                        patch version increment
  -i INSTANCE_TYPE, --instance-type INSTANCE_TYPE
                        instance type i.e. t1.micro
  -ip INSTANCE_PROFILE, --instance_profile INSTANCE_PROFILE
                        the instance profile to use when creating AMIs for
                        custom platforms
  --vpc.id VPC_ID       specify id of VPC to launch Packer builder into
  --vpc.subnets VPC_SUBNETS
                        specify subnets to launch Packer builder into
  --vpc.publicip        associate public IPs to EC2 instances launched if
                        specified
  --timeout TIMEOUT     timeout period in minutes
  --tags TAGS           a comma separated list of tags as key=value pairs

Creates a new platform version. If no version is specified then it will do a patch-increment based on the most recent platform version. The version and increment options are mutually exclusive.
""".strip(),
            self.output_of(['ebp', 'create', '--help'])
        )

    def test_ebp_delete(self):
        self.assertEqual(
            """usage: ebp delete <version> [options...]

Deletes a custom platform version.

positional arguments:
  version               platform version

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  --cleanup             remove all platform versions in the "Failed" state
  --all-platforms       enables cleanup for all of your platforms.
  --force               skip confirmation prompt

You must explicitly select the version to delete.
""".strip(),
            self.output_of(['ebp', 'delete', '--help'])
        )

    def test_ebp_events(self):
        self.assertEqual(
            """usage: ebp events <version> [options...]

Displays events for the custom platform associated with this workspace.

positional arguments:
  version               version to retrieve events for

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -f, --follow          wait and continue to print events as they come
""".strip(),
            self.output_of(['ebp', 'events', '--help'])
        )

    def test_ebp_init(self):
        self.assertEqual(
            """usage: ebp init <platform name> [options...]

Initializes your directory with the EB CLI to create and manage Platforms.
(Uninitialized or platform workspace only)

positional arguments:
  platform_name         platform name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -i, --interactive     force interactive mode
  -k KEYNAME, --keyname KEYNAME
                        default EC2 key name

This command is safe when run in a previously initialized directory. To re-initialize with different options, use the -i option. Note this command cannot change the workspace type of a directory that was already initialized.
""".strip(),
            self.output_of(['ebp', 'init', '--help'])
        )

    def test_ebp_list(self):
        self.assertEqual(
            """usage: ebp list [options...]

Lists available custom platforms

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -a, --all-platforms   lists the versions of all platforms owned by your account
                        (platform workspace only)
  -s STATUS, --status STATUS
                        the status that you wish to filter on (Ready, Failed, Deleting, Creating)
                        (platform workspace only)
""".strip(),
            self.output_of(['ebp', 'list', '--help'])
        )

    def test_ebp_logs(self):
        self.assertEqual(
            """usage: ebp logs <version> [options...]

Retrieves logs for your custom platform build event.

positional arguments:
  version               platform version to retrieve logs for

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  --stream              enable/disable log streaming to CloudWatch Logs
""".strip(),
            self.output_of(['ebp', 'logs', '--help'])
        )

    def test_ebp_status(self):
        self.assertEqual(
            """usage: ebp status <version> [options...]

Displays metadata about your current custom platform version.

positional arguments:
  version               platform version

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates

Will display details about the current version if no version is specified.
""".strip(),
            self.output_of(['ebp', 'status', '--help'])
        )

    def test_ebp_use(self):
        self.assertEqual(
            """usage: ebp use <platform> [options...]

Selects the active custom platform version to use for this workspace.

positional arguments:
  platform              platform name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['ebp', 'use', '--help'])
        )

    def test_eb(self):
        self.assertEqual(
            """usage: eb (sub-commands ...) [options ...] {arguments ...}

Welcome to the Elastic Beanstalk Command Line Interface (EB CLI). 
For more information on a specific command, type "eb {cmd} --help".

commands:
  abort        Cancels an environment update or deployment.
  appversion   Listing and managing application versions
  clone        Clones an environment.
  codesource   Configures the code source for the EB CLI to use by default.
  config       Modify an environment's configuration. Use subcommands to manage saved configurations.
  console      Opens the environment in the AWS Elastic Beanstalk Management Console.
  create       Creates a new environment.
  deploy       Deploys your source code to the environment.
  events       Gets recent events.
  health       Shows detailed environment health.
  init         Initializes your directory with the EB CLI. Creates the application.
  labs         Extra experimental commands.
  list         Lists all environments.
  local        Runs commands on your local machine.
  logs         Gets recent logs.
  open         Opens the application URL in a browser.
  platform     Commands for managing platforms.
  printenv     Shows the environment variables.
  restore      Restores a terminated environment.
  scale        Changes the number of running instances.
  setenv       Sets environment variables.
  ssh          Opens the SSH client to connect to an instance.
  status       Gets environment information and status.
  swap         Swaps two environment CNAMEs with each other.
  tags         Allows adding, deleting, updating, and listing of environment tags.
  terminate    Terminates the environment.
  upgrade      Updates the environment to the most recent platform version.
  use          Sets default environment.

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  --version             show application/version info

To get started type "eb init". Then type "eb create" and "eb open"
""".strip(),
            self.output_of(['eb', '--help'])
        )

    def test_eb_abort(self):
        self.assertEqual(
            """usage: eb abort <environment_name> [options ...]

Cancels an environment update or deployment.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'abort', '--help'])
        )

    def test_eb_appversion(self):
        self.assertEqual(
            """usage: eb appversion <lifecycle> [options ...]

Listing and managing application versions

commands:
  lifecycle   Modifying application version lifecycle policy

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  --delete VERSION_LABEL, -d VERSION_LABEL
                        delete the specified application version
""".strip(),
            self.output_of(['eb', 'appversion', '--help'])
        )

    def test_eb_clone(self):
        self.assertEqual(
            """usage: eb clone <environment_name> (-n CLONE_NAME) [options ...]

Clones an environment.

positional arguments:
  environment_name      name of environment to clone

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -n CLONE_NAME, --clone_name CLONE_NAME
                        desired name for environment clone
  -c CNAME, --cname CNAME
                        cname prefix
  --scale SCALE         number of desired instances
  --tags TAGS           a comma separated list of tags as key=value pairs
  --envvars ENVVARS     a comma-separated list of environment variables as
                        key=value pairs
  -nh, --nohang         return immediately, do not wait for clone to be
                        completed
  --timeout TIMEOUT     timeout period in minutes
  --exact               match the platform version of the original environment
""".strip(),
            self.output_of(['eb', 'clone', '--help'])
        )

    def test_eb_codesource(self):
        self.assertEqual(
            """usage: eb codesource <sourcename> [options ...]

Configures the code source for the EB CLI to use by default.

positional arguments:
  {codecommit,local}    name of the code source to set as default

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'codesource', '--help'])
        )

    def test_eb_config(self):
        for command in [
            ['eb', 'config', '--help'],
            ['eb', 'config', 'delete', '--help'],
            ['eb', 'config', 'get', '--help'],
            ['eb', 'config', 'list', '--help'],
            ['eb', 'config', 'put', '--help'],
            ['eb', 'config', 'save', '--help'],
        ]:
            self.assertEqual("""usage: eb config < |save|get|put|list|delete> <name> [options ...]

Modify an environment's configuration. Use subcommands to manage saved configurations.

commands:
  delete   Delete a configuration.
  get      Download a configuration from S3.
  list     List all configurations.
  put      Upload a configuration to S3.
  save     Save a configuration of the environment.

positional arguments:
  name                  environment_name|template_name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -nh, --nohang         return immediately, do not wait for config to be
                        completed
  --timeout TIMEOUT     timeout period in minutes
  --cfg CFG             name of configuration

Use this command to work with environment configuration settings. 
To update your environment directly in an interactive editor, type:
  eb config
""".strip(),
                             self.output_of(command)
                             )

    def test_eb_console(self):
        self.assertEqual("""usage: eb console <environment_name> [options ...]

Opens the environment in the AWS Elastic Beanstalk Management Console.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
                         self.output_of(['eb', 'console', '--help'])
                         )

    def test_eb_create(self):
        self.assertEqual("""usage: eb create <environment_name> [options ...]

Creates a new environment.

positional arguments:
  environment_name      desired Environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -m [MODULES [MODULES ...]], --modules [MODULES [MODULES ...]]
                        a list of modules
  -g ENV_GROUP_SUFFIX, --env-group-suffix ENV_GROUP_SUFFIX
                        group suffix
  -c CNAME, --cname CNAME
                        cname prefix
  -t TIER, --tier TIER  environment tier type
  -i INSTANCE_TYPE, --instance_type INSTANCE_TYPE
                        instance type i.e. t1.micro
  -p PLATFORM, --platform PLATFORM
                        platform
  -s, --single          environment will use a single instance with no load
                        balancer
  --sample              use Sample Application
  -d, --branch_default  set as branches default environment
  -ip INSTANCE_PROFILE, --instance_profile INSTANCE_PROFILE
                        EC2 Instance profile
  -sr SERVICE_ROLE, --service-role SERVICE_ROLE
                        Service Role
  --version VERSION     version label to deploy
  -k KEYNAME, --keyname KEYNAME
                        EC2 SSH KeyPair name
  --scale SCALE         number of desired instances
  -nh, --nohang         return immediately, do not wait for create to be
                        completed
  --timeout TIMEOUT     timeout period in minutes
  --tags TAGS           a comma separated list of tags as key=value pairs
  --envvars ENVVARS     a comma-separated list of environment variables as
                        key=value pairs
  --cfg CFG             saved configuration name
  --source SOURCE       source of code to create from directly; example
                        source_location/repo/branch
  --elb-type ELB_TYPE   load balancer type
  -db, --database       create a database
  --vpc                 create environment inside a VPC
  -pr, --process        enable preprocessing of the application version

Type "--vpc." or "--database." for more VPC and database options.
""".strip(),
                         self.output_of(['eb', 'create', '--help'])
                         )

    def test_eb_deploy(self):
        self.assertEqual(
            """usage: eb deploy <environment_name> [options ...]

Deploys your source code to the environment.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  --modules [MODULES [MODULES ...]]
                        modules to deploy
  -g ENV_GROUP_SUFFIX, --env-group-suffix ENV_GROUP_SUFFIX
                        group suffix
  --version VERSION     existing version label to deploy
  -l LABEL, --label LABEL
                        label name which version will be given
  -m MESSAGE, --message MESSAGE
                        description for version
  -nh, --nohang         return immediately, do not wait for deploy to be
                        completed
  --staged              deploy files staged in git rather than the HEAD commit
  --timeout TIMEOUT     timeout period in minutes
  --source SOURCE       source of code to deploy directly; example
                        source_location/repo/branch
  -p, --process         enable preprocessing of the application version
""".strip(),
            self.output_of(['eb', 'deploy', '--help'])
        )

    def test_eb_events(self):
        self.assertEqual(
            """usage: eb events <environment_name> [options ...]

Gets recent events.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -f, --follow          wait and continue to print events as they come
""".strip(),
            self.output_of(['eb', 'events', '--help'])
        )

    def test_eb_health(self):
        self.assertEqual(
            """usage: eb health <environment_name> [options ...]

Shows detailed environment health.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  --refresh             refresh
  --mono                no color
  --view {split,status,request,cpu}
""".strip(),
            self.output_of(['eb', 'health', '--help'])
        )

    def test_eb_init(self):
        self.assertEqual(
            """usage: eb init <application_name> [options ...]

Initializes your directory with the EB CLI. Creates the application.

positional arguments:
  application_name      application name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -m [MODULES [MODULES ...]], --modules [MODULES [MODULES ...]]
                        module directory
  -p PLATFORM, --platform PLATFORM
                        default Platform
  -k KEYNAME, --keyname KEYNAME
                        default EC2 key name
  -i, --interactive     force interactive mode
  --source SOURCE       source of code to set as default; example
                        source_location/repo/branch
  --tags TAGS           a comma separated list of tags as key=value pairs

This command is safe when run in a previously initialized directory. To re-initialize with different options, use the -i option. Note this command cannot change the workspace type of a directory that was already initialized.
""".strip(),
            self.output_of(['eb', 'init', '--help'])
        )

    def test_eb_labs(self):
        self.assertEqual(
            """usage: eb labs {cmd} <environment_name> [options ...]

Extra experimental commands.

commands:
  cleanup-versions       Cleans up old application versions.
  convert-dockerrun      Converts Dockerrun.aws.json from version 1 to version 2.
  download               Download Application Version.
  quicklink              Generate a quick-launch link for your project.
  setup-cloudwatchlogs   Create .ebextensions files necessary for setting up CloudWatch used in logging instance deployment.
                         (alias: setup-cwl)
  setup-ssl              Sets up ssl on your environment.

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'labs', '--help'])
        )

    def test_eb_labs_cleanup_versions(self):
        self.assertEqual(
            """usage: eb labs cleanup-versions [options...]

Cleans up old application versions.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  --num-to-leave NUM    number of unused versions to leave DEFAULT=10
  --older-than DAYS     delete only versions older than x days DEFAULT=60
  --force               don't prompt for confirmation
""".strip(),
            self.output_of(['eb', 'labs', 'cleanup-versions', '--help'])
        )

    def test_eb_labs_convert_dockerrun(self):
        self.assertEqual(
            """usage: eb labs convert-dockerrun [options...]

Converts Dockerrun.aws.json from version 1 to version 2.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'labs', 'convert-dockerrun', '--help'])
        )

    def test_eb_labs_download(self):
        self.assertEqual(
            """usage: eb download <environment_name> [options ...]

Download Application Version.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'labs', 'download', '--help'])
        )

    def test_eb_labs_quicklink(self):
        self.assertEqual(
            """usage: eb quicklink <environment_name> [options ...]

Generate a quick-launch link for your project.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates

Applications and environments created from the quick link are accessible to your account only. 
To share the link with other accounts, you must explicitly grant those accounts read access to your S3 application version .zip file.
""".strip(),
            self.output_of(['eb', 'labs', 'quicklink', '--help'])
        )

    def test_eb_labs_setup_cloudwatchlogs(self):
        self.assertEqual(
            """usage: eb labs setup-cloudwatchlogs [options ...]

Create .ebextensions files necessary for setting up CloudWatch used in logging instance deployment.

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  --remove              remove .ebextensions
""".strip(),
            self.output_of(['eb', 'labs', 'setup-cloudwatchlogs', '--help'])
        )

    def test_eb_labs_setup_ssl(self):
        self.assertEqual(
            """usage: eb labs setup-ssl <environment_name> [options...]

Sets up ssl on your environment.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  --cert-file CERT_FILE
                        certificate file
  --private-key PRIVATE_KEY
                        private key file
  --cert-chain CERT_CHAIN
                        certificate chain file
  --name NAME           certificate name DEFAULT={environment-name}
""".strip(),
            self.output_of(['eb', 'labs', 'setup-ssl', '--help'])
        )

    def test_eb_list(self):
        self.assertEqual(
            """usage: eb list [options ...]

Lists all environments.

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -a, --all             show environments for all applications
""".strip(),
            self.output_of(['eb', 'list', '--help'])
        )

    def test_eb_local(self):
        self.assertEqual(
            """usage: eb local (sub-commands ...) [options ...]

Runs commands on your local machine.

commands:
  logs             Prints where logs are locally saved.
  open             Opens the application URL in a browser.
  printenv         Shows local environment variables.
  run              Runs the Docker container on your local machine.
  setenv           Sets local environment variables.
  status           Gets container information and status.

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'local', '--help'])
        )

    def test_eb_local_logs(self):
        self.assertEqual(
            """usage: eb local logs [options ...]

Prints where logs are locally saved.

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'local', 'logs', '--help'])
        )

    def test_eb_local_open(self):
        self.assertEqual(
            """usage: eb local open [options ...]

Opens the application URL in a browser.

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'local', 'open', '--help'])
        )

    def test_eb_local_printenv(self):
        self.assertEqual(
            """usage: eb local printenv [options ...]

Shows local environment variables.

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'local', 'printenv', '--help'])
        )

    def test_eb_local_run(self):
        self.assertEqual(
            """usage: eb local run [options ...]

Runs the Docker container on your local machine.

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  --envvars ENVVARS     a comma-separated list of environment variables as
                        key=value pairs
  --port PORT           the host port that is exposed and mapped to the
                        container port
  --allow-insecure-ssl  Allow insecure connections to the docker registry
""".strip(),
            self.output_of(['eb', 'local', 'run', '--help'])
        )

    def test_eb_local_setenv(self):
        self.assertEqual(
            """usage: eb local setenv [VAR_NAME=KEY ...] [options ...]

Sets local environment variables.

positional arguments:
  varKey                space-separated list in format: VAR_NAME=KEY

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates

Use this command to set environment variables by typing a space-separated list of key=value pairs.
""".strip(),
            self.output_of(['eb', 'local', 'setenv', '--help'])
        )

    def test_eb_local_status(self):
        self.assertEqual(
            """usage: eb local status [options ...]

Gets container information and status.

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'local', 'status', '--help'])
        )

    def test_eb_logs(self):
        self.assertEqual(
            """usage: eb logs <environment_name> [options ...]

Gets recent logs.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -a, --all             retrieve all logs
  -z, --zip             retrieve all logs as .zip
  -i INSTANCE, --instance INSTANCE
                        retrieve logs only for this instance
  -g LOG_GROUP, --log-group LOG_GROUP
                        retrieve logs only for this log group
  -cw [{enable,disable}], --cloudwatch-logs [{enable,disable}]
                        enable/disable log streaming to CloudWatch Logs
  -cls CLOUDWATCH_LOG_SOURCE, --cloudwatch-log-source CLOUDWATCH_LOG_SOURCE
                        CloudWatch logs source to enable/disable or to retrieve
                        valid values:
                          with --cloudwatch-logs (enable/disable): instance | environment-health | all
                          without --cloudwatch-logs (retrieve): instance | environment-health
  --stream              enable/disable log streaming to CloudWatch Logs

This command displays the last 100 lines of logs. To retrieve all logs, use the "--all" option.
""".strip(),
            self.output_of(['eb', 'logs', '--help'])
        )

    def test_eb_open(self):
        self.assertEqual(
            """usage: eb open <environment_name> [options ...]

Opens the application URL in a browser.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'open', '--help'])
        )

    def test_eb_platform_select(self):
        self.assertEqual(
            """usage: eb platform select [options...]

Selects a default platform.
(application workspace only)

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates

This command is an alternative to "eb init -i" and "eb init -p". It doesn't change the platform on any existing environments.
To upgrade an environment's platform, enter:
    eb upgrade
""".strip(),
            self.output_of(['eb', 'platform', 'select', '--help'])
        )

    def test_eb_platform_show(self):
        self.assertEqual(
            """usage: eb platform show <environment_name> [options ...]

Shows information about current platform.
(application workspace only)

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'platform', 'show', '--help'])
        )

    def test_eb_printenv(self):
        self.assertEqual(
            """usage: eb printenv <environment_name> [options ...]

Shows the environment variables.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'printenv', '--help'])
        )

    def test_eb_restore(self):
        self.assertEqual(
            """usage: eb restore <environment_id> [options ...]

Restores a terminated environment.

positional arguments:
  environment_id        The ID of the environment to restore

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'restore', '--help'])
        )

    def test_eb_scale(self):
        self.assertEqual(
            """usage: eb scale {number} <environment_name> [options ...]

Changes the number of running instances.

positional arguments:
  number                number of desired instances
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -f, --force           skip confirmation prompt
  --timeout TIMEOUT     timeout period in minutes
""".strip(),
            self.output_of(['eb', 'scale', '--help'])
        )

    def test_eb_ssh(self):
        self.assertEqual(
            """usage: eb ssh <environment_name> [options ...]

Opens the SSH client to connect to an instance.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -n NUMBER, --number NUMBER
                        index of instance in list
  -i INSTANCE, --instance INSTANCE
                        instance id
  -c COMMAND, --command COMMAND
                        Execute a shell command on the specified instance
                        instead of starting an SSH session.
  -e CUSTOM, --custom CUSTOM
                        Specify an SSH command to use instead of 'ssh -i
                        keyfile'. Do not include the remote user and hostname.
  -o, --keep_open       keep port 22 open
  --force               force port 22 open to 0.0.0.0
  --setup               setup SSH for the environment
  --timeout TIMEOUT     Specify the timeout period in minutes. Can only be
                        used with the '--setup' argument.
""".strip(),
            self.output_of(['eb', 'ssh', '--help'])
        )

    def test_eb_status(self):
        self.assertEqual(
            """usage: eb status <environment_name> [options ...]

Gets environment information and status.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
""".strip(),
            self.output_of(['eb', 'status', '--help'])
        )

    def test_eb_swap(self):
        self.assertEqual(
            """usage: eb swap <environment_name> [options ...]

Swaps two environment CNAMEs with each other.

positional arguments:
  environment_name      name of source environment

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -n DESTINATION_NAME, --destination_name DESTINATION_NAME
                        name of destination environment
""".strip(),
            self.output_of(['eb', 'swap', '--help'])
        )

    def test_eb_tags(self):
        self.assertEqual(
            """usage: eb tags [<environment_name>] option [options ...]

Allows adding, deleting, updating, and listing of environment tags.

positional arguments:
  environment_name      environment on which to perform tags operation

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  -l, --list            lists all environment resource tags
  -a key1=value1[,key2=value2,...], --add key1=value1[,key2=value2,...]
                        create new environment tags provided as a comma-
                        separated list of key=value pairs
  -d key1[,key2,...], --delete key1[,key2,...]
                        delete existing environment tags provided as a comma-
                        separated list of keys
  -u key1=value1[,key2=value2,...], --update key1=value1[,key2=value2,...]
                        update existing environment tags provided as a comma-
                        separated list of keys=value pairs
  --resource-arn RESOURCE_ARN
                        Finds tags associated with given resource.
""".strip(),
            self.output_of(['eb', 'tags', '--help'])
        )

    def test_eb_terminate(self):
        self.assertEqual(
            """usage: eb terminate <environment_name> [options ...]

Terminates the environment.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  --force               skip confirmation prompt
  --ignore-links        terminate even if environment is linked
  --all                 terminate everything
  -nh, --nohang         return immediately, do not wait for terminate to be
                        completed
  --timeout TIMEOUT     timeout period in minutes

This command terminates the environment. To terminate the application and everything in it, use the "--all" option.
""".strip(),
            self.output_of(['eb', 'terminate', '--help'])
        )

    def test_eb_upgrade(self):
        self.assertEqual(
            """usage: eb upgrade <environment_name> [options ...]

Updates the environment to the most recent platform version.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  --timeout TIMEOUT     timeout period in minutes
  --force               skip confirmation prompt
  --noroll              do not enable rolling updates before upgrade
""".strip(),
            self.output_of(['eb', 'upgrade', '--help'])
        )

    def test_eb_use(self):
        self.assertEqual(
            """usage: eb use [environment_name] [options ...]

Sets default environment.

positional arguments:
  environment_name      environment name

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -v, --verbose         toggle verbose output
  --profile PROFILE     use a specific profile from your credential file
  -r REGION, --region REGION
                        use a specific region
  --no-verify-ssl       don't verify AWS SSL certificates
  --source SOURCE       source of code to deploy directly; example
                        source_location/repo/branch
""".strip(),
            self.output_of(['eb', 'use', '--help'])
        )


class PlatformWorkspaceTests(TestHelpTexts, HelpTestsMixin):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = os.getcwd()
        if os.path.exists('testDir'):
            shutil.rmtree('testDir')
        os.mkdir('testDir')
        os.chdir('testDir')

        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            'my-custom-platform',
            workspace_type='Platform'
        )

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.root_dir)


class ApplicationWorkspaceTests(TestHelpTexts, HelpTestsMixin):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = os.getcwd()
        if os.path.exists('testDir'):
            shutil.rmtree('testDir')
        os.mkdir('testDir')
        os.chdir('testDir')

        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            'php-7.2',
            workspace_type='Application'
        )

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.root_dir)


class NoWorkspaceTests(TestHelpTexts, HelpTestsMixin):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = os.getcwd()
        if os.path.exists('testDir'):
            shutil.rmtree('testDir')
        os.mkdir('testDir')
        os.chdir('testDir')

        try:
            if fileoperations.eb_file_exists(os.getcwd()):
                raise EnvironmentError(
                    'Found a .elasticbeanstalk/config.yml at a level above CWD. '
                    'Before rerunning this test, ensure that all .elasticbeanstalk '
                    'directories directly above this directory are deleted.'
                )
        except fileoperations.NotInitializedError:
            pass

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.root_dir)


if __name__ == '__main__':
    io.echo('1. Reinstalling awsebcli')
    subprocess.Popen(['pip', 'uninstall', '-y', 'awsebcli'], stdout=subprocess.PIPE).communicate()
    subprocess.Popen(['pip', 'install', '.'], stdout=subprocess.PIPE).communicate()

    io.echo('2. Checking help outputs in platform workspaces')
    PlatformWorkspaceTests.run()

    io.echo('3. Checking help outputs in application workspaces')
    ApplicationWorkspaceTests.run()

    io.echo('4. Checking help outputs in non-workspaces')
    NoWorkspaceTests.run()
