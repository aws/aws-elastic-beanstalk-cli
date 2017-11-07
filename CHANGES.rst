=========
Changelog
=========
-------------------
3.12.1 (2017-11-08)
-------------------
- Added ability for customers to download sample application during `eb create` if using one
- Added graceful handling of errors when operating `ebp` commands in `eb` workspaces
- Fixed hyperlink to page describing ECS permissions necessary to create multi-container docker environments
- Fixed `DescribeEvents` polling logic for environment creation after ASG per-region quota is reached
- Fixed `DescribeEvents` polling logic by filtering events returned accurately
- Fixed `eb list`'s usage text by removing mention of environment name as a positional argument
- Increased default timeout for `eb create` when the `-db` flag is specified
- Modified `eb ssh` logic to use private IP address rather than private DNS when a public IP/DNS is not available
- Modified generic EBCLI timeout message to prompt customers to view the result of `eb events -f`
- Removed `eb ssh --custom`'s dependency on SSH private key in `~/.ssh`

-------------------
3.12.0 (2017-10-10)
-------------------
- Added support for tagging Environments

-------------------
3.11.0 (2017-09-26)
-------------------
- Added support for creation of environments with Network Load Balancers
- Fixed bug that caused `eb restore` to fail to begin

-------------------
3.10.6 (2017-08-21)
-------------------
- Fixed 5-minute timeout bug involving CLI giving up on CodeBuild despite server-side success
- Fixed module-creation bug where `eb create` exits because it cannot find the .elasticbeanstalk directory
- Increased limit on the number of tags that can be created during environment creation to 47
- Fixed environment creation failures when platform names specified are from the list retrieved by `eb platform list`.

-------------------
3.10.5 (2017-07-28)
-------------------
- Added ca-central-1 (Canada-Central), and ap-south-1 (Mumbai) CodeCommit support
- Made .elasticbeanstalk/logs/local directory writable by all thorough 'eb local run'
- Fixed Python 2.x character encoding bug that prevents 'eb appversion' from displaying

-------------------
3.10.4 (2017-07-14)
-------------------
- Fixed bug in solution stack determination logic for Multi-Container Docker 17.03.1-ce platform version

-------------------
3.10.3 (2017-06-27)
-------------------
- Added ability to zip git submodules for application versions
- Added us-west-1 (N. California), eu-west-2 (London), ap-northeast-2 (Seoul), and sa-east-1 (São Paulo) CodeCommit support
- Added exception handling for TooManyConfigurationTemplatesException

-------------------
3.10.2 (2017-06-09)
-------------------
- Improved eb and ebp create default instance profile creation logic.
- Added eu-central-1 (Frankfurt), ap-northeast-1 (Tokyo), ap-southeast-1 (Singapore) and ap-southeast-2 (Sydney) CodeCommit support
- Added additional logging for 5xx retry messages

-------------------
3.10.1 (2017-03-30)
-------------------
- Fixed python 3.x bug for eb local run
- Fixed eb local docker version check failure for leading zeros
- Fixed eb init to not create an application when picking an existing app
- Fixed eb local run to accept volumes defined that are not prefixed with /var/app/current/

-------------------
3.10.0 (2017-02-21)
-------------------
- Support for custom elastic beanstalk platforms
- Fixed CodeBuild integration pulling CloudWatch URL link

------------------
3.9.1 (2017-02-08)
------------------
- Changed Beanstalk CodeBuild integration to be optional by not specifying the header in buildspec
- Fixed 'eb config put' to update DateModified field
- Fixed 'eb config put' full path failure
- Fixed exit codes to return correctly
- Removed CodeCommit failed prompt in eb init to avoid confusion
- Added 'process' flag for eb create/deploy for preprocessing application versions

------------------
3.9.0 (2016-12-22)
------------------
- Added native support in 'eb logs' for log streaming.
- Added '--log-group' and '--cloudwatch-logs' flags in 'eb logs'
- Added 'appversion' command to managed application versions
- Added 'appversion lifecycle' sub command to manage application lifecycle configurations

-------------------
3.8.10 (2016-12-19)
-------------------
- Fixed install bug for python 3.x

------------------
3.8.9 (2016-12-16)
------------------
- Added 'eb restore' command, used to restore terminated environments

------------------
3.8.8 (2016-12-13)
------------------
- Added eu-west-2 EU (London) region

------------------
3.8.7 (2016-12-08)
------------------
- Fixed Windows installation bug

------------------
3.8.6 (2016-12-08)
------------------
- Added support for working directories containing white-spaces
- Added ca-central-1 Canada (Central) support

------------------
3.8.5 (2016-12-01)
------------------
- Added support for CodeBuild by autodetecting a buildspec file and deploying with settings from that

------------------
3.8.4 (2016-11-16)
------------------
- Added '--source' flag to create, deploy, init and use to directly use source from CodeCommit repositories
- Added us-west-2 (Oregon) and eu-west-1 (Ireland) CodeCommit support

------------------
3.8.3 (2016-10-17)
------------------
- Added us-east-2 (Ohio) CodeCommit support

------------------
3.8.2 (2016-10-17)
------------------
- Added us-east-2 (Ohio) region

------------------
3.8.1 (2016-10-13)
------------------
- CodeCommit bug fixes

------------------
3.8.0 (2016-10-13)
------------------
- Fixed elb prompt for single instance creations
- Fixed eb init to no longer call CreateApplication when a preexisting application is chosen
- Allowing eb ssh to attempt to access private ip address if public ip is not available
- Added support for CodeCommit deployment and integration

------------------
3.7.8 (2016-08-22)
------------------
- Fixed 'eb setenv --timeout' problem
- Updated 'eb config' inline doc to be clearer on functionality
- Fixed 'eb deploy --nohang' problem
- Added commands '--command' and '--custom' to 'eb ssh'
- Added support for Application Load Balancer with 'create', 'health' and 'status'

------------------
3.7.7 (2016-06-27)
------------------
- Added "ap-south-1" to region list
- Checking for existing app versions in application, local or in their account, before creating one when label is specified.
- Updating environment name length constraints to 40 char max.

------------------
3.7.6 (2016-04-14)
------------------
- The Elastic Beanstalk Service role will now also be created during non-interactive environment creates
- Added the AWSElasticBeanstalkService managed policy to the Elastic Beanstalk Service role

------------------
3.7.5 (2016-04-01)
------------------
- Support new Enhanced Health features
- Fix bug in "eb health" for basic health environments
- Fix bug in "eb health" that causes a date parsing error for some locale settings
- Roles created by the CLI now make use of AWS Managed Policies

------------------
3.7.4 (2016-03-10)
------------------
- Fix an issue that prevents "`eb local <http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb3-local.html>`_" subcommands from working with Docker 1.10
- Fix an issue that causes the EB CLI to crash when deploying multiple modules with `compose environments <http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/ebcli-compose.html>`_

------------------
3.7.3 (2016-01-28)
------------------
- Fix bug with application version processing
- Fix bug in "eb config delete"

------------------
3.7.2 (2016-01-08)
------------------
- Fix bug where symlinks in application versions were not in their original locations

------------------
3.7.1 (2016-01-07)
------------------
- Fix long type incompatibility bug with Python 3

----------------
3.7 (2016-01-06)
----------------
- Add "ap-northeast-2" to region list
- Fix bug with symlinks on Unix systems

------------------
3.6.2 (2015-12-14)
------------------
- Improved logic related to waiting for application version processing
- Change tag behavior to allow for '=' in tag values
- Prompt for EnvironmentName when not present in env.yaml

------------------
3.6.1 (2015-11-23)
------------------
- Remove pre-processing of application versions when no env.yaml file is present
- Fix bug with 'eb logs'

------------------
3.6 (2015-11-23)
------------------
- Support for Composable Applications

------------------
3.5.6 (2015-11-20)
------------------
- Fix bug in 'eb health' causing errors in some locales
- Change the naming scheme of app versions when using Git
- Change strings related to timeout errors to indicate the presence of the timeout option

------------------
3.5.5 (2015-10-27)
------------------
- Fix bug in "eb swap"
- Fix typo in string resource

------------------
3.5.4 (2015-09-22)
------------------
- Add "cn-north-1" to region list
- Adjust client default ELB Healthcheck Interval to use service default

------------------
3.5.3 (2015-09-14)
------------------
- Change contact details
- Fix bug in "eb labs setup-ssl" which occurred on some versions of Python

------------------
3.5.2 (2015-08-26)
------------------
- Fix bug in "eb health" command preventing it from running.

------------------
3.5.1 (2015-08-25)
------------------
- Fix az column clipping.
- Unhide labs setup-cwl feature as well as logs --stream.
- Add pip install command when a new version is available.

------------------
3.5 (2015-08-11)
------------------
- Add command "eb labs setup-ssl"
- Add command "eb labs cloudwatchlogs-setup"
- Change `eb open` to now open https if load balancer http port is OFF
- Add support for enhanced health with `eb health`
- Other minor changes

------------------
3.4.7 (2015-07-28)
------------------
- Fix issue with .gitignore being included on deploy
- Fix issue with streaming unicode events

------------------
3.4.6 (2015-07-10)
------------------
- Fix issue with "eb labs download"
- Fix issue where folders in .ebignore were incorrectly being uploaded.

------------------
3.4.5 (2015-06-08)
------------------
- SSH no longer attempts to open port 22 if a Source restriction is in place
- Added --force flag to override above behavior
- SSH errors now show properly with the -o option
- Environment variables are less strict and can now contain the '=' sign

------------------
3.4.4 (2015-05-18)
------------------
- Changed how Sample Application is handled internally

------------------
3.4.3 (2015-05-12)
------------------
- Fix issue with "eb config" when adding new option settings
- Update golang local container file
- Fix issue with overwriting docker environment variables during local

------------------
3.4.2 (2015-05-09)
------------------
- Fix issue with installation for eb local files

----------------
3.4 (2015-05-07)
----------------
- Added 'localContainerDefinitions' section for multi-continer docker
- Multi-container docker containers now correctly read 'environment'
- Added printenv/setenv commands to eb local
- t2.micro is now default instance type for accounts with a default vpc
- add --staged option to eb deploy for deploying git stage rather then commit
- Fix config file path resolution

------------------
3.3.2 (2015-04-30)
------------------
- Fix "eb open" for windows

------------------
3.3.1 (2015-04-28)
------------------
- Fix --force option on "eb labs cleanup-versions"

----------------
3.3 (2015-04-28)
----------------
- Added "local" commands
- Added "eb labs cleanup-versions" for cleaning up old app versions
- Added support for an .ebignore file
- using "eb terminate --all" now removes application bundles from s3
- Add support for branch specific defaults in config.yml
- Fix interactive vpc bug
- Fix "eb open" race condition
- Incomplete credentials errors are now more verbose

------------------
3.2.2 (2015-04-06)
------------------
- Fix issue with creating single instance environments

------------------
3.2.1 (2015-04-02)
------------------
- Added warning string for Multi-container permissions on "create"

----------------
3.2 (2015-03-30)
----------------
- Added "platform" commands
- Added "upgrade" command
- Added "abort" command
- Added "labs" commands
- Printed events now look nicer
- Logs and events are automatically paged.
- Health based rolling updates are now default for new environments.

------------------
3.1.3 (2015-03-13)
------------------
- Added option on create for specifying database version (--database.version)

------------------
3.1.2 (2015-02-26)
------------------
- Fix multithreaded issue on python 3.4.3
- Fix environment names printing in columns
- Update botocore to 0.93.0

------------------
3.1.1 (2015-02-24)
------------------
- Fix git issue on windows
- Support older versions of git
- Saved Configurations now work with Worker tier

----------------
3.1 (2015-02-17)
----------------
- Editor backup files (file.txt~) no longer included in application zip
- Added commands for Saved Configurations (eb config --help)
- Now receive alerts for an outdated cli and outdated environment platform.
- Deploy now works in subdirectories
- Config now works in subdirectories
- Can now specify your own timeout period with "--timeout x"
- Can now specify environment variables on environment create with "--envvars"
- Can now get the latest platform version when you clone an environment. "eb clone"
- Application Bundle uploads now show status
- Large file uploads are now multi-threaded
- Added warning on deploy if unstaged git changes exist
- Can now swap environment CNAME's using "eb swap"
- Exposed --vpc option on create
- Added --no-verify-ssl option
- Updated Botocore to 0.88.0

-------------------
3.0.11 (2015-02-09)
-------------------
- Fixed Zipping issue for Windows Containers

-------------------
3.0.10 (2014-11-24)
-------------------
- Fixed parsing error for uploads in a s3 bucket with auto-deletion policy
- Fixed terminated environment issues
- No longer uploads application if the application version already exists in s3
- Default database username changed from admin to ebroot
- Trim application version description if it is too long
- Application version no longer includes git hash
