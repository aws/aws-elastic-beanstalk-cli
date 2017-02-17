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
from ebcli.resources.statics import iam_attributes

strings = {
    # Inform customers that this has created the platform builder environment
    'platformbuildercreation.info': "Note: An environment called '{0}' has been created in order to build your application. "
        "This environment will not automatically be terminated and it does have a cost associated with it. "
        "Once your platform creation has completed you can terminate this builder environment using the command "
        "'eb terminate'.",
    # Version message got 'eb --version'
    'app.version_message': 'EB CLI',
    # When an update is available on PyPi
    'base.update_available': 'An update to the EB CLI is available. '
                             'Run "pip install --upgrade awsebcli" to get the latest version.',
    # Initial text that you see on a 'eb --help'
    'base.info': 'Welcome to the Elastic Beanstalk Command Line Interface (EB CLI). \n'
                 'For more information on a specific command, type "eb {cmd} --help".',
    # Initial epilog (last line) that you see on 'eb --help'
    'base.epilog': 'To get started type "eb init". Then type "eb create" and "eb open"',
    'ebpbase.info': 'Welcome to the Elastic Beanstalk Command Line Interface (EB CLI). \n'
                 'For more information on a specific command, type "ebp {cmd} --help".',
    'ebpbase.epilog': 'To get started type "ebp init". Then type "ebp create"',

    # All .infos are for --help text. All .epilogs are the epilogs shown on the given command
    'init.info': 'Initializes your directory with the EB CLI. Creates the application.',
    'init.epilog': 'This command is safe when run in a previously initialized'
                   ' directory. To re-initialize with different options, '
                   'use the -i option. Note this command cannot change the workspace type'
                   ' of a directory that was already initialized.',
    'init.dir.notexists': 'The specified directory {dir} does not exist. Please ensure that you are specifying the proper directory.',
    'init.usingenvyamlplatform': 'Using platform specified in env.yaml: {platform}',
    'create.info': 'Creates a new environment.',
    'create.epilog': 'Type "--vpc." or "--database." for more VPC and database options.',
    'create.missinggroup': 'A group name is required when creating multiple environments. Please use the --group option.',
    'events.info': 'Gets recent events.',
    'open.info': 'Opens the application URL in a browser.',
    'console.info': 'Opens the environment in the AWS Elastic Beanstalk Management Console.',
    'clone.info': 'Clones an environment.',
    'clone.epilog': 'This command clones your environment and attempts to upgrade the platform to the latest version.\n'
                    'To create a clone with the same platform version, use the "--exact" option.',
    'abort.info': 'Cancels an environment update or deployment.',
    'use.info': 'Sets default environment.',
    'health.info': 'Shows detailed environment health.',
    'deploy.info': 'Deploys your source code to the environment.',
    'platforminit.info': 'Prepares your workspace to build and manage custom platforms.',
    'platformcleanup.info': 'Terminates your platform builder environment.',
    'platformset.version': 'Setting workspace platform version to:',
    'platformset.newplatform': 'New platform "%s"',

    'platformworkspaceshow.info': 'Displays details about platform resources.',
    'platformshowversion.info': 'Displays metadata about your current custom platform version.',
    'platformbuilderlogs.info': 'Retrieves logs from your platform builder environment.',
    'platformlogs.info': 'Retrieves logs for your custom platform build event.',
    'platformssh.info': 'SSH into your platform builder environment.',
    'platformshowversion.epilog': 'Will display details about the current version if no version is specified.',

    'platformworkspacelist.info': 'Lists platform resources.',
    'platformlistversions.info': 'Lists versions of the custom platform associated with this workspace.',
    'platformlistversions.epilog': 'You can reduce the result set by using filters.',

    'platformcreate.info': 'Creates platform resources.',
    'platformcreateversion.info': 'Creates a new custom platform version.',
    'platformcreateversion.epilog': 'Creates a new platform version. If no version is specified then it will do a ' \
                             'patch-increment based on the most recent platform version. The version and increment '
                             'options are mutually exclusive.',

    'platformcreateiamdescribeerror.info': "Insufficient IAM privileges. Unable to determine if instance profile '{0}'exists.".format(iam_attributes.DEFAULT_PLATFORM_BUILDER_ROLE),
    'platformcreateiamcreated.info': "Created instance profile '{0}'".format(iam_attributes.DEFAULT_PLATFORM_BUILDER_ROLE),
    'platformcreateiamcreateerror.info': "Insufficient IAM privileges. Unable to create instance profile '{0}', assuming that it exists.".format(
                    iam_attributes.DEFAULT_PLATFORM_BUILDER_ROLE),

    'platformcreateiampolicyadded.info': "Added required permissions to instance profile '{0}'".format(
        iam_attributes.DEFAULT_PLATFORM_BUILDER_ROLE),


    'platformdelete.info': 'Deletes platform resources.',
    'platformdeleteversion.info': 'Deletes a custom platform version.',
    'platformdeleteversion.epilog': 'You must explicitly select the version to delete.',
    'platformdeletevalidation.error': 'Unable to delete platform version ({0}/{1}) because it is being used by the following environments:\n {2}\n'
                                      'Please terminate or upgrade these environments before trying to delete this platform.',

    'platformdelete.events': 'Shows events for the current platform',

    'platforminit.info': 'Initializes your directory with the EB CLI to create and manage Platforms.',
    'platforminit.epilog': 'This command is safe when run in a previously initialized'
                   ' directory. To re-initialize with different options, '
                   'use the -i option. Note this command cannot change the workspace type'
                   ' of a directory that was already initialized.',
    'platforminit.noinstanceprofile': 'You are creating a workspace without an instance profile. Without an '
                                      'instance profile you cannot create a platform with a customized AMI. '
                                      'Use eb platform init -i or -I to configure your instance profile.',
    'platform.info': 'Commands for managing platforms.',
    'platformshow.info': 'Shows information about current platform.',
    'platformlist.info': 'Lists available platforms.',
    'platformworkspaceselect.info': 'Selects platform resources to use for this workspace.',
    'platformworkspaceselectversion.info': 'Selects the active custom platform version to use for this workspace.',
    'platformselect.info': 'Selects a default platform.',
    'platformselect.epilog': 'This command is an alternative to "eb init -i" and "eb init -p". It does not change the platform on any existing environments.\n'
                             'To upgrade an environment\'s platform, type:\n'
                             '    eb upgrade',
    'platformevents.info': 'Displays events for the custom platform associated with this workspace.',
    'platformlist.epilog': 'Shows a list of platforms for use with "eb init -p". Type "--verbose" to get the full platform name.',
    'upgrade.info': 'Updates the environment to the most recent platform version.',
    'scale.info': 'Changes the number of running instances.',
    'status.info': 'Gets environment information and status.',
    'setenv.info': 'Sets environment variables.',
    'setenv.epilog': 'Use this command to set environment variables by typing a space-separated list of key=value pairs.\n'
                     'For example, to set HeapSize to 256m and Site_Url to mysite.elasticbeanstalk.com, type:\n'
                     '  eb setenv HeapSize=256m Site_Url=mysite.elasticbeanstalk.com\n'
                     'You can also remove environment variables by specifying no value. For example:\n'
                     '  eb setenv HeapSize= Site_Url=\n'
                     'This removes the environment variables.',
    'swap.info': 'Swaps two environment CNAMEs with each other.',
    'config.epilog': 'Use this command to work with environment configuration settings. \n'
                     'To update your environment directly in an interactive editor, type:\n'
                     '  eb config\n',
    'config.notfound': 'Elastic Beanstalk could not find any saved configuration with the name "{config-name}".',
    'config.envyamlexists': 'It appears your environment is using an env.yaml file. Be aware that a saved configuration will take precedence over the contents of your env.yaml file when both are present.',
    'list.info': 'Lists all environments.',
    'terminate.info': 'Terminates the environment.',
    'terminate.epilog': 'This command terminates the environment. To terminate the application and everything in it, use the "--all" option.',
    'config.info': "Modify an environment's configuration. Use subcommands to manage saved configurations.",
    'platformconfig.info': "Modify an platform's configuration. Use subcommands to manage saved configurations.",
    'ssh.info': 'Opens the SSH client to connect to an instance.',
    'printenv.info': 'Shows the environment variables.',
    'local.info': 'Runs commands on your local machine.',
    'local.printenv.info': 'Shows local environment variables.',
    'local.run.info': 'Runs the Docker container on your local machine.',
    'local.setenv.info': 'Sets local environment variables.',
    'local.logs.info': 'Prints where logs are locally saved.',
    'local.open.info': 'Opens the application URL in a browser.',
    'local.status.info': 'Gets container information and status.',
    'local.setenv.epilog': 'Use this command to set environment variables by typing a space-separated list of key=value pairs.',
    # Error when --sample and --label flag are both used on create
    'create.sampleandlabel': 'You cannot use the "--sample" and "--version" options together.',
    'create.singleandsize': 'You cannot use the "--single" and "--scale" options together.',
    'create.appdoesntexist': 'The specified app {app_name} does not exist. Skipping.',
    'create.missinggroupsuffix': 'The environment name specified in env.yaml ends with a \'+\', but no group suffix was provided. Please pass the --env-group-suffix argument.',
    'ssh.instanceandnumber': 'You cannot use the "--instance" and "--number" options together.',
    # Text shown if 'eb terminate' is called while no environment is selected as default
    'terminate.noenv': 'To delete the application and all application versions, type "eb terminate --all".',

    'cred.prompt':  'You have not yet set up your credentials or your credentials are incorrect \n'
                    'You must provide your credentials.',
    'prompt.invalid': 'You did not provide a valid value.',
    'prompt.yes-or-no': 'Type either "Y" or "N".',
    # Default description for apps created with cli
    'app.description': 'Application created from the EB CLI using "eb init"',
    # Default description for environment created with cli
    'env.description': 'Environment created from the EB CLI using "eb create"',
    # Same as above but for cloned environments
    'env.clonedescription': 'Environment cloned from {env-name} from the EB CLI using "eb clone"',
    # Default template description
    'template.description': 'Configuration created from the EB CLI using "eb config save".',
    'env.exists': 'An environment with that name already exists.',
    # Error, no solution stacks returned. Almost always due to permissions
    'sstacks.notfound': 'Elastic Beanstalk could not find any platforms. Ensure you have the necessary permissions to access Elastic Beanstalk.',
    'sstacks.notaversion': 'Elastic Beanstalk could not find any supported platforms for the given version {version}.',
    'timeout.error': 'The operation timed out. The state of the environment is unknown. The timeout can be set using the --timeout option.',
    'sc.notfound': 'Git is not set up for this project. EB CLI will deploy a .zip file of the entire directory.',
    'exit.platformworkspacenotsupported': 'This command is not supported for Platform workspaces.',
    'exit.applicationworkspacenotsupported': 'This command is not supported for Application workspaces.',
    'exit.notsetup': 'This directory has not been set up with the EB CLI\n'
                     'You must first run "eb init".',
    'exit.noregion': 'The EB CLI cannot find a default region. Run "eb init" or use a specific region by including the "--region" option with the command.',
    'exit.platformworkspaceempty': 'The current directory does not contain any Platform configuration files. Unable to create new Platform.',
    # Typical response when an environment is in pending state
    'exit.invalidstate': 'The operation cannot be completed at this time due to a pending operation. Try again later.',
    'exit.argerror': 'There was an argument error in the given command',
    'exit.invalidversion': 'Invalid version format. Only ARNs, version numbers, or platform_name/version formats are accepted.',
    'exit.no_pdf_file': 'Unable to create platform version. Your workspace does not have a Platform Definition File, \'platform.yaml\', in the root directory.',
    'exit.nosuchplatformversion': 'No such version exists for the current platform.',
    'exit.nosuchplatform': 'No such platform exists.',
    'branch.noenv': 'This branch does not have a default environment. You must either specify an environment by typing '
                    '"eb {cmd} my-env-name" or set a default environment by typing "eb use my-env-name".',
    'ssh.notpresent': 'SSH is not installed. You must install SSH before continuing.',
    'ssh.filenotfound': 'The EB CLI cannot find your SSH key file for keyname "{key-name}".'
                        ' Your SSH key file must be located in the .ssh folder in your home directory.',
    'local.logs.location': 'Elastic Beanstalk will write logs locally to {location}',
    'local.logs.lastlocation': 'Logs were most recently created {prettydate} and written to {location}',
    'local.logs.symlink': 'Updated symlink at {symlink}',
    'local.logs.nologs': 'There are currently no local logs.',
    'setenv.invalidformat': 'You must use the format KEY=VALUE to set an environment variable. '
                            'Variables must start with a letter.',
    'tags.invalidformat': 'You must provide a comma-separated list using the format name=value to set tags. '
                          'Tags may only contain letters, numbers, and the following symbols: / _ . : + = - @',
    'tags.max': 'Elastic Beanstalk supports a maximum of 7 tags.',
    'deploy.invalidoptions': 'You cannot use the "--version" option with either the "--message" or "--label" option.',
    'init.getvarsfromoldeb': 'You previous used an earlier version of eb. Getting options from .elasticbeanstalk/config.\n'
                             'Credentials will now be stored in ~/.aws/config',
    'ssh.noip': 'This instance does not have a Public IP address. This is possibly because the instance is terminating.',
    # Error thrown when someone provides a cname with a worker tier
    'worker.cname': 'Worker tiers do not support a CNAME.',
    # Error thrown when available cname is not available
    'cname.unavailable': 'The CNAME prefix {cname} is already in use.',
    'ssh.openingport': 'INFO: Attempting to open port 22.',
    'ssh.portopen': 'INFO: SSH port 22 open.',
    'ssh.notopening': 'Found source restriction on ssh port; not attempting to open. Use the --force flag to force opening of the port.',
    'ssh.closeport': 'INFO: Closed port 22 on ec2 instance security group.',
    'ssh.uploaded': 'Uploaded SSH public key for "{keyname}" into EC2 for region {region}.',
    'swap.unsupported': 'You must have at least 2 running environments to swap CNAMEs.',
    'connection.error': 'Having trouble communicating with AWS. Please ensure the provided region is correct and you have a working internet connection.',
    'toomanyplatforms.error': 'You have reached your platform limit. Please consider deleting failed platform versions, or versions that you no longer require.',
    'sc.unstagedchanges': 'You have uncommitted changes.',
    'sc.gitnotinstalled': 'Your project is using git, but git doesn\'t appear to be installed.\n'
                          'Have you added git to your PATH?',
    'events.streamprompt': ' -- Events -- (safe to Ctrl+C)',
    'events.unsafestreamprompt': ' -- Events -- (Ctrl+C will abort the deployment)',
    'events.abortmessage': ' Use "eb abort" to cancel the command.',
    'abort.noabortableenvs': 'There are no environments currently being updated.',
    'local.unsupported': 'You can use "eb local" only with preconfigured, generic and multicontainer Docker platforms.',
    'local.dockernotpresent': 'You must install Docker version {docker-version} to continue. If you are using Mac OS X, ensure you have boot2docker version {boot2docker-version}. Currently, "eb local" does not support Windows.',
    'local.filenotfound': 'The EB CLI cannot find Dockerfile or the Dockerrun.aws.json file in the application root directory.',
    'local.missingdockerrun': 'This environment requires a Dockerrun.aws.json file to run.',
    'local.invaliddockerrunversion': 'The AWSEBDockerrunVersion key in the Dockerrun.aws.json file is not valid or is not included.',
    'local.missingdockerrunimage': 'The Dockerrun.aws.json file requires the Image key.',
    'local.missingdockerrunports': 'The Dockerrun.aws.json file requires the Ports key.',
    'local.missingdockerruncontainerport': 'The Dockerrun.aws.json file requires the ContainerPort field.',
    'local.invalidjson': 'The Dockerrun.aws.json file is not in valid JSON format.',
    'local.run.noportexposed': 'The Dockerfile must list ports to expose on the Docker container. Specify at least one port, and then try again.',
    'local.run.nobaseimg': 'The Dockerfile or Dockerrun.aws.json file does not specify a base image. Specify a base image, and then try again.',
    'local.run.socketperms': 'If you are on Ubuntu, ensure that you have added yourself into the Unix docker group by running "sudo usermod -aG docker $USER" '
                             'and then log out and log back in.',
    'local.open.nocontainer': 'Elastic Beanstalk did not detect a running Docker container. Ensure that a container is running before you use "eb local open".',
    'local.open.noexposedport': 'This container has no exposed host ports.',
    'labs.info': 'Extra experimental commands.',
    'quicklink.info': 'Generate a quick-launch link for your project.',
    'quicklink.epilog': 'Applications and environments created from the quick link are accessible to your account only. \n'
                        'To share the link with other accounts, you must explicitly grant those accounts read access to your S3 application version .zip file.',
    'download.info': 'Download Application Version.',
    'convert-dockkerrun.info': 'Converts Dockerrun.aws.json from version 1 to version 2.',
    'cleanup-versions.info': 'Cleans up old application versions.',
    'setup-ssl.info': 'Sets up ssl on your environment.',
    'region.china.credentials': 'To use the China (Beijing) region, account credentials unique to the China (Beijing) region must be used.',
    'deploy.notadirectory': 'The directory {module} does not exist.',
    'deploy.modulemissingenvyaml': 'All specified modules require an env.yaml file.\n'
                                   'The following modules are missing this file: {modules}',
    'deploy.noenvname': 'No environment name was specified in env.yaml for module {module}. Unable to deploy.',
    'compose.noenvyaml': 'The module {module} does not contain an env.yaml file. This module will be skipped.',
    'compose.novalidmodules': 'No valid modules were found. No environments will be created.',
    'instance.processes.health': '{healthy}/{total} processes healthy.',

    # codesource
    'codesource.info': 'Configures the code source for the EB CLI to use by default.',
    'codesource.localmsg': 'Default set to use local sources',
    'restore.info': 'Restores a terminated environment.',

    # Resotre Environment
    'restore.no_env': 'No terminated environments found.\nEnvironments are available for six weeks after termination.',
    'restore.displayheader': 'Select a terminated environment to restore',

    # Log command/ Beanstalk logs
    'logs.info': 'Gets recent logs.',
    'logs.epilog': 'This command displays the last 100 lines of logs. To retrieve all logs, use the "--all" option.',
    'logs.allandzip': 'You cannot use the "--all" and "--all_zip" options together.',
    'logs.allandinstance': 'You cannot use the "--all" and "--instance" options together.',
    'logs.location': 'Logs were saved to {location}',
    'beanstalk-logs.badinstance': 'Could not find specified instance "{instance_id}" in the retrieved logs',

    # labs cloudwatch-setup command
    'cloudwatch-setup.info': 'Create .ebextensions files necessary for setting up CloudWatch used in logging instance deployment.',
    'cloudwatch-setup.alreadysetup': 'CloudWatch file {filename} is already set up.',
    'cloudwatch-setup.text': '.ebextensions created. In order to complete setup you will need\n'
                             'to check in any changes, (if applicable) and run "eb deploy".\n'
                             'You will also need the cloudwatch log permissions for this IAM User\n'
                             'as well as for the environments instance profile.\n'
                             'For more information see: http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/AWSHowTo.cloudwatchlogs.html',
    'cloudwatch-setup.removetext': 'Removed .ebextensions. In order to complete removal you\n'
                                   'will need to check in any changes, (if applicable) an run\n'
                                   '"eb deploy".',

    # Log streaming
    'cloudwatch-stream.notsetup': 'Could not find log group; CloudWatch log streaming may not enabled for this environment.\n'
                                  'Run "eb logs -cw enable" to enable log streaming.',
    'cloudwatch-logs.nostreams': 'Could not find any log streams with log group: {log_group}',
    'cloudwatch-logs.enable': 'Enabling CloudWatch log for your environment',
    'cloudwatch-logs.disable': 'Disabling CloudWatch log for your environment',

    # The link to Cloudwatch console is different for BJS:
    'cloudwatch-logs.link': 'After the environment is updated you can view your logs by following the link:\n'
                   'https://console.aws.amazon.com/cloudwatch/home?region={region}#logs:prefix=/aws/elasticbeanstalk/{env_name}/',
    'cloudwatch-logs.bjslink': 'After the environment is updated you can view your logs by following the link:\n'
                    'https://console.amazonaws.cn/cloudwatch/home?region={region}#logs:prefix=/aws/elasticbeanstalk/{env_name}/',

    'cloudwatch-logs.alreadyenabled': 'CloudWatch logs are already enabled for your environment',
    'cloudwatch-logs.alreadydisabled': 'CloudWatch logs are already disabled for your environment',

    # lifecycle
    'lifecycle.info': 'Modifying application version lifecycle policy',
    'lifecycle.epilog': 'Use this command to work with application lifecycle configuration settings. \n'
                        'To update your application directly in an interactive editor, type:\n'
                        '  eb appversion lifecycle\n',
    'lifecycle.success': 'Successfully updated application version lifecycle policy',
    'lifecycle.updatenochanges': 'No changes made; exiting',
    'lifecycle.invalidrole': 'Passed an invalid role: {role}, cannot update application',
    'lifecycle.invalidsyntax': 'The configuration settings you provided contain an error;'
                               ' The lifecycle configuration will not be updated',

    # appversion
    'appversion.create': 'Creating application version archive "{version}".',
    # When create is called, if we cant find any files, we say this
    'appversion.none': 'The current directory does not contain any source code. Elastic Beanstalk is launching the sample application instead.',
    'appversion.processfailed': 'Pre-processing of application version {app_version} has failed.',
    'appversion.cannotdeploy': 'Some application versions failed to process. Unable to continue deployment.',
    'appversion.processtimeout': 'All application versions have not reached a "Processed" state. Unable to continue with deployment.',
    'appversion.info': 'Listing and managing application versions',
    'appversion.delete.notfound': 'Application {} does not have Application Version {}.',
    'appversion.delete.deployed': 'Cannot delete Application version {} as it is deployed to Environments: {}',
    'appversion.delete.none': 'You must specify an Application version label to delete an Application version',
    'appversion.attribute.failed': 'Application Version {app_version} has failed to generate required attributes.',
    'appversion.attribute.timeout': 'Application Versions did not generated the required attributes. Unable to continue with deployment.',
    'appversion.attribute.success': 'Found attributes for application version {app_version}',

    # CodeCommit
    'codecommit.nosc': 'Cannot setup CodeCommit because there is no Source Control setup, continuing with initialization',
    'codecommit.ccwarning': 'Note: Elastic Beanstalk now supports AWS CodeCommit; a fully-managed source control service.'
                    ' To learn more, see Docs: https://aws.amazon.com/codecommit/',
    'codecommit.norepo': 'Repository does not exist in CodeCommit',
    'codecommit.nobranch': 'Branch does not exist in CodeCommit',
    'codecommit.badregion': 'AWS CodeCommit is not supported in this region; continuing initialization without CodeCommit',

    # CodeBuild
    'codebuild.noheader': 'Beanstalk configuration header \'{header}\' is missing from Buildspec file; will not use Beanstalk Code Build integration',
    'codebuild.latestplatform': 'Buildspec file is present but no image is specified; using latest image for selected platform: {platform}',
    'exit.noplatform': 'This workspace is not configured with a platform. Please select one using "eb platform use"',
    'platformstatus.upgrade': 'A more recent version of this platform is available. Type \'eb upgrade\' to uprade the platform version used by this environment.',
    'platform.nobuilderenv': 'This workspace has not yet been associated with a builder environment. One will be configured once you create a platform version.',
    'codebuild.buildlogs': 'You can find logs for the CodeBuild build here: {logs_link}',
}
prompts = {
    'events.hanging': 'Streaming new events. Use CTRL+C to exit.',
    'platform.validate': 'It appears you are using {platform}. Is this correct?',
    'platform.prompt': 'Select a platform.',
    'platform.prompt.withmodule': 'Select a platform for module: {module_name}.',
    'platformssh.nokey': 'This platform builder is not set up for SSH. Use "eb platform ssh --setup" to set up SSH for that environment.',
    'sstack.version': 'Select a platform version.',
    'init.selectdefaultenv': 'Select the default environment. \n'
                             'You can change this later by typing "eb use [environment_name]".',
    'scale.switchtoloadbalance': 'The environment is currently a single-instance. Do you want'
                                 ' to change to a load-balancing environment?',
    'scale.switchtoloadbalancewarn': 'If you choose yes, the environment and your application will be temporarily unavailable.',
    'cname.unavailable': 'The CNAME you provided is already in use.\n',
    'cleanupbuilder.confirm': 'The platform builder environment "{env-name}" and all associated instances will be terminated.',
    'cleanupbuilder.validate': 'To confirm, type the environment name',
    'cleanupplatform.confirm': 'Failed platform versions for "{platform-name}" will be removed.',
    'cleanupplatform.validate': 'To confirm, type the platform name',
    'cleanupplatform.validate-all': 'To confirm, type "all"',

    'terminate.confirm': 'The environment "{env-name}" and all associated instances will be terminated.',
    'terminate.validate': 'To confirm, type the environment name',
    'upgrade.validate': 'To continue, type the environment name',
    'platformdelete.confirm': 'The platform "{platform-arn}" and all associated resources will be deleted.',
    'platformdelete.validate': 'To confirm, type the platform arn',

    'delete.confirm': 'The application "{app-name}" and all its resources will be deleted.\n'
                      'This application currently has the following:\n'
                      'Running environments: {env-num}\n'
                      'Configuration templates: {config-num}\n'
                      'Application versions: {version-num}\n',
    'delete.validate': 'To confirm, type the application name',
    'fileopen.error1': 'EB CLI cannot open the file using the editor {editor}.',
    'fileopen.error2': 'Unable to open environment file. Try setting the EDITOR environment variable.',
    'update.invalidstate': 'The environment update cannot be complete at this time. Try again later.',
    'update.invalidsyntax': 'The configuration settings you provided contain an error. The environment will not be updated.',
    'ssh.setup': 'Do you want to set up SSH for your instances?',
    'sstack.invalid': 'You specified a platform that is not valid.',
    'sstack.invalidkey': 'The EB CLI cannot find a platform for key "{string}".',
    'keypair.prompt': 'Select a keypair.',
    'keypair.nameprompt': 'Type a keypair name.',
    'tier.prompt': 'Select an environment tier.',
    # Error given on terminate when the user input does not match name
    'terminate.nomatch': 'Names do not match. Exiting.',
    'ssh.nokey': 'This environment is not set up for SSH. Use "eb ssh --setup" to set up SSH for the environment.',
    'ssh.setupwarn': 'You are about to setup SSH for environment "{env-name}". If you continue, your existing instances will have to be **terminated** and new instances will be created. The environment will be temporarily unavailable.',
    'rds.username': 'Enter an RDS DB username (default is "ebroot")',
    'rds.password': 'Enter an RDS DB master password',
    'vpc.id': 'Enter the VPC ID',
    'vpc.publicip': 'Do you want to associate a public IP address?',
    'vpc.ec2subnets': 'Enter a comma-separated list of Amazon EC2 subnets',
    'vpc.elbsubnets': 'Enter a comma-separated list of Amazon ELB subnets',
    'vpc.securitygroups': 'Enter a comma-separated list of Amazon VPC security groups',
    'vpc.elbpublic': 'Do you want the load balencer to be public? (Select no for internal)',
    'vpc.dbsubnets': 'Enter a comma-separated list of database subnets',
    'logs.retrieving': 'Retrieving logs...',
    'swap.envprompt': 'Select the environment with which you want to swap CNAMEs.',
    'abort.envprompt': 'Select the environment you want to stop updating.',
    'clone.latest': 'There is a newer version of the platform used by the environment you are cloning.\n'
                    'Select the version of the platform that you want to use for the clone.',
    'clone.latestwarn': 'Launching environment clone on most recent platform version. Override this behavior by using the "--exact" option.',
    'upgrade.altmessage': 'You can also change your platform version by typing "eb clone" and then "eb swap".',
    'upgrade.singleinstance': 'This operation causes application downtime while Elastic Beanstalk replaces the instance.',
    'upgrade.norollingapply': 'Elastic Beanstalk will enable {0}-based rolling updates to avoid application downtime while it replaces your instances. You may cancel the upgrade after it has started by typing "eb abort". To upgrade without rolling updates, type "eb upgrade --noroll".',
    'upgrade.norollingforce': 'This operation causes application downtime while Elastic Beanstalk replaces your instances.',
    'upgrade.rollingupdate': 'This operation replaces your instances with minimal or zero downtime. You may cancel the upgrade after it has started by typing "eb abort".',
    'upgrade.infodialog': 'The environment "{0}" will be updated to use the most recent platform version.',
    'upgrade.alreadylatest': 'Environment already on most recent platform version.',
    'upgrade.applyrolling': 'Enabling {0}-based rolling updates to environment.',
    'create.dockerrunupgrade': 'Multicontainer Docker environments do not support the version number of the Dockerrun.aws.json file that you provided. Type "eb labs convert-dockerrun" to convert it to a newer format.',
    'ecs.permissions': 'The Multi-container Docker platform requires additional ECS permissions. Add the permissions to the aws-elasticbeanstalk-ec2-role or use your own instance profile by typing "-ip {profile-name}".\n'
                       'For more information see: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create_deploy_docker_ecstutorial.html#create_deploy_docker_ecstutorial_role',
    'create.servicerole.info': '2.0+ Platforms require a service role. We will attempt to create one for you. You can specify your own role using the --service-role option.',
    'create.servicerole.view': 'Type "view" to see the policy, or just press ENTER to continue',
    'create.servicerole.required': '2.0+ Platforms require a service role. You can provide one with --service-role option',
    'create.servicerole.nopermissions': 'No permissions to create a role. '
                                        'Create an IAM role called "{}" with appropriate permissions to continue, or specify a role with --service-role.\n'
                                        'See http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/concepts-roles.html for more info. \nActual error: {}',
    'general.pressenter': 'Press enter to continue',
    'compose.groupname': 'Please enter the group name to be used',

    # Restore
    'restore.prompt': 'Enter a environment # to restore. ESC to exit.',
    'restore.selectedenv': '\nSelected environment {env_id}\nApplication:   {app}\nDescription:   {desc}\nCNAME:         {cname}\n'
                           'Version:       {version}\nPlatform:      {platform}\nTerminated:    {dat_term}\n'
                           'Restore this environment? [y/n]\n',

    # codesource
    'codesource.codesourceprompt': 'Select your codesource',

    # appversion
    'appversion.redeploy.validate': 'Do you want to deploy a previous or different version? (y/n)',
    'appversion.redeploy.prompt': 'Select a version # to deploy (1 to {}).',
    'appversion.redeploy.inprogress': 'Deploying version {}.',

    'appversion.delete.validate': 'Do you want to delete the application version with label: {}? (y/n)',
    'appversion.delete.prompt': 'Select a version # to delete (1 to {}).',

    # CodeCommit
    'codecommit.usecc': 'Do you wish to continue with CodeCommit? (y/N) (default is n)',

    # CodeBuild
    'codebuild.getplatform': 'Could not determine best image for buildspec file please select from list.\n Current chosen platform: {platform}',
    'platforminit.ssh': 'Would you like to be able to log into your platform packer environment?',
}

alerts = {
    'platform.old': 'There is a newer version of the platform used by your environment. You can upgrade your environment to the most recent platform version by typing "eb upgrade".'
}

flag_text = {
    # General
    'general.env': 'environment name',
    'base.version': 'show application/version info',
    'base.verbose': 'toggle verbose output',
    'base.profile': 'use a specific profile from your credential file',
    'base.region': 'use a specific region',
    'general.timeout': 'timeout period in minutes',
    'base.noverify': 'do not verify AWS SSL certificates',

    # Clone
    'clone.env': 'name of environment to clone',
    'clone.name': 'desired name for environment clone',
    'clone.cname': 'cname prefix',
    'clone.scale': 'number of desired instances',
    'clone.tags': 'a comma separated list of tags as key=value pairs',
    'clone.nohang': 'return immediately, do not wait for clone to be completed',
    'clone.exact': 'match the platform version of the original environment',

    # Config
    'config.nohang': 'return immediately, do not wait for config to be completed',
    'config.codesource': 'configure the settings for which source the CLI will use for your code.'
                         ' Availables sources: {codecommit}. Available actions: {enable, disable}',

    # Create
    'create.name': 'desired Environment name',
    'create.cname': 'cname prefix',
    'create.itype': 'instance type i.e. t1.micro',
    'create.tier': 'environment tier type',
    'create.platform': 'platform',
    'create.single': 'environment will use a single instance with no load balancer',
    'create.sample': 'use Sample Application',
    'create.default': 'set as branches default environment',
    'create.iprofile': 'EC2 Instance profile',
    'create.servicerole': 'Service Role',
    'create.version': 'version label to deploy',
    'create.keyname': 'EC2 SSH KeyPair name',
    'create.scale': 'number of desired instances',
    'create.nohang': 'return immediately, do not wait for create to be completed',
    'create.tags': 'a comma separated list of tags as key=value pairs',
    'create.envvars': 'a comma-separated list of environment variables as key=value pairs',
    'create.database': 'create a database',
    'create.vpc': 'create environment inside a VPC',
    'create.config': 'saved configuration name',
    'create.group': 'group suffix',
    'create.modules': 'a list of modules',
    'create.elb_type': 'load balancer type',
    'create.source': 'source of code to create from directly; example source_location/repo/branch',
    'create.process': 'enable preprocessing of the application version',

    # Deploy
    'deploy.env': 'environment name',
    'deploy.modules': 'modules to deploy',
    'deploy.version': 'existing version label to deploy',
    'deploy.label': 'label name which version will be given',
    'deploy.message': 'description for version',
    'deploy.nohang': 'return immediately, do not wait for deploy to be completed',
    'deploy.staged': 'deploy files staged in git rather than the HEAD commit',
    'deploy.group_suffix': 'group suffix',
    'deploy.source': 'source of code to deploy directly; example source_location/repo/branch',
    'deploy.process': 'enable preprocessing of the application version',

    # Events
    'platformevents.version': 'version to retrieve events for',
    'events.follow': 'wait and continue to print events as they come',

    # Init
    'init.name': 'application name',
    'init.platform': 'default Platform',
    'init.keyname': 'default EC2 key name',
    'init.interactive': 'force interactive mode',

    # Platform create
    'platformcreate.instanceprofile': 'the instance profile to use when creating AMIs for custom platforms',

    # SSH
    'ssh.keyname': 'EC2 key to use with ssh',
    'init.module': 'module directory',
    'init.source': 'source of code to set as default; example source_location/repo/branch',

    # labs
    'labs.cwl.remove': 'remove .ebextensions',

    # List
    'list.all': 'show environments for all applications',

    # Local
    'local.run.envvars': 'a comma-separated list of environment variables as key=value pairs',
    'local.run.hostport': 'the host port that is exposed and mapped to the container port',
    'local.run.insecuressl': 'Allow insecure connections to the docker registry',
    'local.setenv.vars': 'space-separated list in format: VAR_NAME=KEY',

    # Logs
    'logs.all': 'retrieve all logs',
    'logs.zip': 'retrieve all logs as .zip',
    'logs.instance': 'instance id',
    'logs.log-group': 'entire log group or just the path to the file, ex: "var/log/httpd/error_log"',
    'logs.stream': 'stream deployment logs that were set up with cloudwatch',
    'logs.environment': 'environment from which to download logs',

    # Restore
    'restore.env': 'The ID of the environment to restore',

    # Scale
    'scale.number': 'number of desired instances',
    'scale.force': 'skip confirmation prompt',

    # Setenv
    'setenv.vars': 'space-separated list in format: VAR_NAME=KEY',
    'setenv.env': 'environment name',

    # SSH
    'ssh.number': 'index of instance in list',
    'ssh.instance': 'instance id',
    'ssh.keepopen': 'keep port 22 open',
    'ssh.command': 'Execute a shell command on the specified instance instead of starting an SSH session.',
    'ssh.custom': "Specify an SSH command to use instead of 'ssh -i keyfile'. Do not include the remote user and hostname.",
    'ssh.force': 'force port 22 open to 0.0.0.0',
    'ssh.setup': 'setup SSH for the environment',

    # Cleanup
    'cleanup.resources': 'Valid values include (builder, versions, all). You can specify "builder" to terminate the environment used to create this platform. You can use "versions" to clean up platform versions in the Failed state',
    'cleanup.force': 'skip confirmation prompt',

    # Delete
    'platformdelete.force': 'skip confirmation prompt',
    'platformdelete.cleanup': 'remove all platform versions in the "Failed" state',
    'platformdelete.allplatforms': 'enables cleanup for all of your platforms.',

    # terminate
    'terminate.force': 'skip confirmation prompt',
    'terminate.all': 'terminate everything',
    'terminate.nohang': 'return immediately, do not wait for terminate to be completed',
    'terminate.ignorelinks': 'terminate even if environment is linked',

    # Platform
    'platforminit.name': 'platform name',

    # Platform: Create Version
    'platformcreateversion.version': 'platform version',
    'platformcreateversion.major': 'major version increment',
    'platformcreateversion.minor': 'minor version increment',
    'platformcreateversion.patch': 'patch version increment',
    'platformcreateversion.vpc.id': 'specify id of VPC to launch Packer builder into',
    'platformcreateversion.vpc.subnets': 'specify subnets to launch Packer builder into',
    'platformcreateversion.vpc.publicip': 'associate public IPs to EC2 instances launched if specified',

    # logs
    'platformlogs.version': 'platform version to retrieve logs for',

    # Platform: Delete Version
    'platformdeleteversion.version': 'platform version',

    # Platform: Show Version
    'platformshowversion.version': 'platform version',

    'platformlist.all': 'lists the versions of all platforms owned by your account',
    'platformlist.status': 'the status that you wish to filter on (Ready, Failed, Deleting, Creating)',

    'platformworkspace.platform': 'platform name',

    # Upgrade
    'upgrade.noroll': 'do not enable rolling updates before upgrade',

    # use
    'use.env': 'environment name',
    'use.source': 'source of code to set as default; example source_location/repo/branch',
    'use.repo': 'default code commit repository',
    'use.branch': 'default code commit branch will use default repository if none is specified',

    # swap
    'swap.env': 'name of source environment',
    'swap.name': 'name of destination environment',

    # codesource
    'codesource.sourcename': 'name of the code source to set as default',

    # appversion
    'appversion.delete': 'delete the specified application version',

    # lifecycle
    'lifecycle.print': 'prints the current application version lifecycle policy',
    'lifecycle.update': 'allows an inline update to a application version lifecycle policy'
}


### The below are programmatic and are not intended to be edited unless the service response changes
responses = {
    'event.completewitherrors': 'Create environment operation is complete, but with errors.',
    'event.platformdeletesuccess': 'Successfully deleted platform version',
    'event.platformdeletefailed': 'Failed to delete platform version',
    'event.platformcreatefailed': 'Failed to create platform version',
    'event.platformcreatesuccess': 'Successfully created platform version',
    'event.redmessage': 'Environment health has been set to RED',
    'event.redtoyellowmessage': 'Environment health has transitioned '
                               'from YELLOW to RED',
    'event.yellowmessage': 'Environment health has been set to YELLOW',
    'event.greenmessage': 'Environment health has been set to GREEN',
    'event.launchsuccess': 'Successfully launched environment:',
    'event.launchbad': 'Create environment operation is CompleterController, '
                       'but with errors',
    'event.failedlaunch': 'Failed to launch environment.',
    'event.faileddeploy': 'Failed to deploy application.',
    # Event fails with 'Failed to deploy configuration.' but the the terminal event is below
    'event.failedupdate': 'The environment was reverted to the previous configuration setting.',
    'event.updatebad': 'Update environment operation is complete, but with errors.',
    'event.updatefailed': 'Failed to deploy configuration.',
    'git.norepository': 'Error: Not a git repository '
                        '(or any of the parent directories): .git',
    'health.nodescribehealth': 'DescribeEnvironmentHealth is not supported.',
    'env.updatesuccess': 'Environment update completed successfully.',
    'env.configsuccess': 'Successfully deployed new configuration to environment.',
    'env.cnamenotavailable': 'DNS name \([^ ]+\) is not available.',
    'env.nameexists': 'Environment [^ ]+ already exists.',
    'app.deletesuccess': 'The application has been deleted successfully.',
    'app.exists': 'Application {app-name} already exists.',
    'app.notexists': 'No Application named {app-name} found.',
    'logs.pulled': 'Pulled logs for environment instances.',
    'logs.successtail': 'Successfully finished tailing',
    'logs.successbundle': 'Successfully finished bundling',
    'logs.fail': 'Failed to pull logs for environment instances.',
    'env.terminated': 'terminateEnvironment completed successfully.',
    'env.invalidstate': 'Environment named {env-name} is in an invalid state for this operation. Must be Ready.',
    'loadbalancer.notfound': 'There is no ACTIVE Load Balancer named',
    'loadbalancer.targetgroup.notfound': 'Target group \'{tgarn}\' not found',
    'ec2.sshalreadyopen': 'the specified rule "peer: 0.0.0.0/0, TCP, from port: 22, to port: 22,',
    'swap.success': 'Completed swapping CNAMEs for environments',
    'cfg.nameexists': 'Configuration Template {name} already exists.',
    'create.noplatform': 'Unable to determine base for template pack (no solution stack)',
    'create.ecsdockerrun1': 'ECS Application sourcebundle validation error: Unsupported AWSEBDockerrunVersion:',
    'appversion.finished': 'Finished processing application version',

    # Env Restore display table
    'restore.norestore': 'Environment will not be restored'
}
git_ignore = [
    '# Elastic Beanstalk Files',        # comment line
    '.elasticbeanstalk/*',              # ignore eb files
    '!.elasticbeanstalk/*.cfg.yml',       # don't ignore configuration templates
    '!.elasticbeanstalk/*.global.yml',    # don't ignore global configurations
]

docker_ignore = git_ignore[:2] + ['.git', '.gitignore']
