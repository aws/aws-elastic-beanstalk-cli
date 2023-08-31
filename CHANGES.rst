
Changelog
=========
-------------------
3.20.9 (2023-08-31)
-------------------
- Updated botocore requirement to `>1.23.41,<1.32.0`
- Updated six requirement to `>=1.11.0,<1.17.0`
- Update dependabot configuration to only update minor version
- Bug fix for Cloudformation pagination token  

-------------------
3.20.8 (2023-08-15)
-------------------
- Updated botocore requirement to `>1.23.41,<1.31.27`
- Updated urllib3 requirement to `>=1.26.5,<2`
- Updated docker-compose requirement to `>= 1.25.2, <= 1.29.2`
- Updated PyYAML requirement to `>=5.3.1,<6.1`

-------------------
3.20.7 (2023-06-21)
-------------------
- Updated botocore requirement to `>1.23.41,<1.29.159`
- Updated requests requirement to `>2.31`
- Updated .gitignore
- Updated LauchedAt Attribute for DescribeInstancesHealth

-------------------
3.20.6 (2023-04-11)
-------------------
- Updated botocore requirement to `>1.23.41,<1.29.100`
- Fixed platforms bug
- Fixed Codebuild bug
- Fixed Symlink and Performance Issues

-------------------
3.20.5 (2023-02-28)
-------------------
- Updated botocore requirement to `>1.23.41,<1.29.82`
- Include requirements.txt into pypi distribution tarball

-------------------
3.20.4 (2023-02-27)
-------------------
- Updated botocore requirement to `>1.23.41,<1.29.81`
- Removed usage of future package
- Opened new regions (ap-southeast-3 and ap-northeast-3)
- Fixed symlinked files related issues
- Fixed modules related issues
- Fixed several unit tests
- Fixed Docker AL2 platform Notfound bug
- Integrated codecommit in new regions (eu-south-1,ap-northeast-3, af-south-1)
- Updated eb create command to create application elb as default
- Updated to display full results when --version flag is specified

-------------------
3.20.3 (2022-01-21)
-------------------
- Updated botocore requirement to `>1.23.41,<1.24.0`
- Updated pathspec requirement to `==0.9.0`
- Increased timestamp precision of version label
- Fix ssh bugs

-------------------
3.20.2 (2021-08-30)
-------------------
- Updated urllib3 requirement to `>=1.26.5`

-------------------
3.20.1 (2021-07-13)
-------------------
- Changed IAM document for China region
- Updated botocore requirement to `>=1.21.0,<1.22.0`

-------------------
3.20.0 (2021-06-09)
-------------------
- Updated PyYAML requirement to `>=5.3.1,<5.5`
- Updated default log group for AL2 platforms
- Added two new options for config command
- Added a new command appversion to create application versions without deployment
- Replaced default service role policy

-------------------
3.19.4 (2021-03-11)
-------------------
- Updated botocore requirement to `>=1.19.0,<1.21.0`
- Updated requests requirement to `>=2.20.1,<=2.26`
- Updated semantic_version requirement to `2.8.5`
- Updated six requirement to `>=1.11.0,<1.15.0`
- Updated platform lookup logic for `eb config put` command
- Updated docker build command to use tags

-------------------
3.19.3 (2021-01-15)
-------------------
- Fixed UnicodeDecode error causing `eb logs` and `eb appversion` command to fail
- Updated success event look up logic for `eb logs` command

-------------------
3.19.2 (2020-10-26)
-------------------
- Updated botocore requirement to `>=1.19.0,<1.20.0`
- Updated coloroma requirement to `>=0.2.5,<0.4.4`
- Updated python-dateutil requirement to `>=2.1,<3.0.0`
- Updated requests requirement to `>=2.20.1,<=2.24`
- Updated six requirement to `>=1.12.0,<=1.15.0`
- Updated urllib3 requirement to `>=1.25.4,<1.25.8/1.26`

-------------------
3.19.1 (2020-10-15)
-------------------
- Fixed bug that caused `eb logs --all/--zip` to fail for AL2 platforms

-------------------
3.19.0 (2020-09-08)
-------------------
- Added support for shared application load balancer during environment creation
- Added `--shared-lb` and `--shared-lb-port` arguments to the `eb create` command
- Removed default value of elb-type for non-interactive create environment flow
- Updated botocore requirement to `>=1.17,<1.18`
- Updated pytest-cov requirement to `<=2.9`

-------------------
3.18.2 (2020-07-06)
-------------------
- Ignore socket files during app version creation
- Add platform branch support to eb local run
- Set default value of elb-type to "application"
- Check for security-group ssh rule before attempting to create one
- Fix fetch logic for CodeCommit branches
- Add fallback for regions with unknown CodeCommit support
- Unify boolean prompts to use a single implementation

-------------------
3.18.1 (2020-04-28)
-------------------
- Added af-south-1 (Cape Town) region
- Added eu-south-1 (Milano) region
- Fixed bug causing `eb logs` command to fail when logs contain unicode characters
- Fixed bug that caused `eb platform` list to fail in un-initialized directory

-------------------
3.18.0 (2020-04-09)
-------------------
- Updated eb init command's --platform option to accept platform branch names
- Updated eb init command's interactive platform menus to derive menu items from platform branches
- Updated eb init command to display platform end-of-life alerts based on platform branch lifecycle state
- Updated eb create --platform option to accept platform branch names
- Updated eb create command to display platform end-of-life alerts based on platform branch lifecycle state
- Updated eb platform select command's interactive menus to derive menu items from platform branches
- Updated eb platform select command to display platform end-of-life alerts based on platform branch lifecycle state
- Updated eb deploy command to display platform end-of-life alerts based on platform branch lifecycle state
- Updated eb status command to display platform end-of-life alerts based on platform branch lifecycle state
- Improving performance of .ebignore lookup
- Upgrading botocore requirement to resolve awscli conflict
- Upgrading pyyaml requirement to resolve awscli conflict
- Upgrading colorama requirement to resolve awscli conflict

-------------------
3.17.1 (2020-01-22)
-------------------
- Updated botocore requirement to `>=1.14.0,<1.15`
- Updated PyYAML requirement to `>=5.2,<5.3`
- Updated docker-compose requirement to `>=1.25.2,<1.26.0`

-------------------
3.17.0 (2019-12-20)
-------------------
- Added `--on-demand-base-capacity` and `--on-demand-above-base-capacity` arguments to the `eb create` command
- Added `--min-instances` and `--max-instances` arguments to the `eb create` command
- Added ability to create a single instance spot environment

-------------------
3.16.0 (2019-11-22)
-------------------
- Added support for spot fleet requests during environment creation
- Updated `botocore` requirement to `>1.13.0,<1.14`
- Updated `python-dateutil` requirement to `>=2.1,<2.8.1`

-------------------
3.15.3 (2019-07-18)
-------------------
- Added me-south-1 Middle East (Bahrain) region
- Added `--timeout` argument to the `eb restore` command

-------------------
3.15.2 (2019-05-22)
-------------------
- Added ap-east-1 China (Hong Kong) region

--------------------
3.15.1 (2019-05-15)
--------------------
- Fixed bug that rejected the `eb platform list --region ...` command in an un-initialized directory

--------------------
3.15.0 (2019-04-04)
--------------------
- Added ability to tag applications through `eb init`
- Added ability to tag configuration templates through `eb config save`
- Added ability to tag custom platforms through `eb platform create`
- Added support to tag resources with ARNs through the `--resource` argument of `eb tags`

--------------------
3.14.13 (2019-02-22)
--------------------
- Fix Python 2.7 EBCLI breakage

--------------------
3.14.12 (2019-02-22)
--------------------
- Fixed `eb init` behaviour so that AWS credentials environment variables are checked before assuming "eb-cli" profile
- Updated `pathspec` requirement to `0.5.9`
- Introduced direct dependency on `wcwidth>=0.1.7,<0.2.0`

--------------------
3.14.11 (2019-02-07)
--------------------
- Fixed behaviour of `eb` commands whereby error events were being classified as successful
- Fixed bug that rejected `--profile` argument in favor of environment variables representing credentials
- Fixed bug that caused `eb create/deploy` to abort following failure to delete temporary application versions directory

--------------------
3.14.10 (2019-01-21)
--------------------
- Introduced direct dependency on `requests>=2.20.1,<2.21`
- Fixed bug that failed `--source` arguments with '/'s in the branch name

-------------------
3.14.9 (2019-01-09)
-------------------
- Updated `urllib3` requirement to `>=1.24.1,<1.25`
- Updated `docker-compose` requirement to `>=1.23.2,<1.24`
- Updated `botocore` requirement to `>=1.12.29,<1.13`
- Updated `six` requirement to `>=1.11.0,<1.12.0`
- Added ability to reference CodeCommit branch names containing '/'s

-------------------
3.14.8 (2018-12-12)
-------------------
- Added eu-north-1 EU (Stockholm) region

-------------------
3.14.7 (2018-12-03)
-------------------
- Fixed Python 2.7 Unicode tag deletion bug
- Fixed bug that suggests unavailable CNAME to customers
- Fixed logic to handle exceptions without error messages
- Fixed bug that avoids showing region list during `eb init`
- Fixed bug that fails to invoke CodeCommit credential helper on Windows
- Fixed failure to create empty README file in CodeCommit Git repository on Windows
- Modified ALB to be the default load balancer during `eb create`
- Modified NLB to be available in the China regions
- Modified `eb ssh` logic to use `PrivateIpAddress` rather than `PrivateDnsName`


-------------------
3.14.6 (2018-09-11)
-------------------
- Added `--timeout` argument to the `eb platform create` command
- Added `--timeout` argument to the `eb ssh --setup` command
- Passed `serviceId` as a parameter to the `botocore`-managed service models patched by the EBCLI
- Removed dependency on `tabulate`
- Restricted `urllib3` requirement to range `>1.21,<1.23` to resolve dependency incompatibility between `botocore` and `requests`
- Updated `botocore` requirement to `>=1.12.1,<1.13`

-------------------
3.14.5 (2018-09-07)
-------------------
- Restricted `botocore` version to the range `<1.12` to avoid incompatibility with the EBCLI

-------------------
3.14.4 (2018-08-16)
-------------------
- Fixed `eb platform --help` and `ebp --help` usage texts to show all available commands and subcommands regardless of workspace type
- Fixed `eb create` and `eb deploy` behavior in cases where customer-specified timeout values are rejected

-------------------
3.14.3 (2018-07-18)
-------------------
- Changed `eb health` table on non-Windows platforms to use Unicode U+25C4 and U+25BA for left and right arrow characters rather than U+25C0 and U+25B6 respectively
- Updated `pyyaml` version requirement to the range >=3.10,<=3.13 to enable usage of the EBCLI with Python 3.7.0
- Added logic to show UTC timestamps for all event text output of all `eb` commands which wait on the Beanstalk service
- Fixed bug in the interactive flow of `eb create` requiring customers to specify `vpc.publicip`, `vpc.elbsubnets` and `vpc.elbpublic` arguments for `--tier` type "worker"
- Fixed bug in the interactive flow of `eb create` requiring customers to specify `vpc.elbsubnets` and `vpc.elbpublic` arguments for single-instance environments

-------------------
3.14.2 (2018-07-03)
-------------------
- Amended solution stack precedence logic to prefer Amazon GlassFish to equivalent Debian GlassFish platforms
- Fixed exceptions not inheriting from `EBCLIException` to force `eb` to exit with return code 4
- Fixed ability to create application versions from directories greater than 4GB in size
- Fixed `eb health` on Windows
- Fixed `eb swap` failure which occurs when executing without arguments
- Removed support for usage of the EBCLI through `py2exe`
- Restricted `pyyaml` version to the range `>=3.10,<=3.12` to be compatible with `docker-compose` and `aws`

-------------------
3.14.1 (2018-06-11)
-------------------
- Added eu-west-3 (Paris) CodeCommit support
- Prevented selection of ELB type in the interactive mode of `eb create` for worker-tier environments
- Updated version of `colorama`

-------------------
3.14.0 (2018-06-04)
-------------------
- Added `docker-compose` as a dependency
- Added `python-dateutil` as a dependency
- Removed direct dependencies on `docker`, `dockerpty`, `docopt`, `requests`, and `websocket-client`
- Added logic to poll `logs#describe_log_groups` to wait for Custom Platform Builder log-group creation
- Fixed `eb clone` bug which occurs while setting CNAME of cloned environment
- Fixed `eb deploy --modules ...` bug which occurs when attempting to print failure message of `elasticbeanstalk#compose_environments`

-------------------
3.13.0 (2018-05-15)
-------------------
- Added ability to enable streaming environment-health logs to CloudWatch
- Added explicit dependency on Python package `docker`
- Fixed environment variables parsing logic during `eb create`
- Fixed `eb health` for environments using basic health and an ELBV2 load balancer
- Fixed `eb logs` behavior to choose an incorrect default log group for Windows platforms
- Fixed `eb platform delete`'s inability to delete custom platforms in some situations
- Fixed `eb tags --list` failure occurring when the default branch environment is absent
- Fixed .gitignore problem on Windows whereby files specified for omission could also be staged
- Prevented attempts to create convenience symlinks to latest logs when executing with Python 2.7 on Windows
- Removed code that installs Python package `docker` on the customer's behalf

-------------------
3.12.4 (2018-03-07)
-------------------
- Fixed `DescribeEvents` polling logic to use `datetime.utcnow()` instead of `datetime.now()`
- Fixed `TimeoutError`s to force `eb` to exit with return code 4
- Fixed `eb deploy --modules ...` bug preventing it from finding project root
- Fixed `eb platform list --verbose` bug preventing it from listing all custom platform ARNs
- Fixed `eb init --source` bug by enforcing association with remote CodeCommit repository
- Modified `eb` to retry after `botocore.parsers.ResponseParserErrors`

-------------------
3.12.3 (2018-02-15)
-------------------
- Fixed CodeCommit integration problem when there are multiple remotes
- Fixed bug involving `eb init` using preexisting app

-------------------
3.12.2 (2018-02-06)
-------------------
- Added eu-west-3 EU (Paris) and cn-northwest-1 China (Ningxia) regions
- Added support for `eb local run` with major versions 2 of Python package `docker-py`
- Fixed `--platform` option to take language name as argument
- Fixed behavior of `--platform` flag to pick the latest version of solution stack when input is ambiguous
- Fixed .ebignore logic to recognize files with Unicode characters
- Fixed redundant downloading of Packer events published by CloudWatch
- Fixed silent rescues of `UnicodeEncodeError`\s when printing Packer events
- Fixed `DescribeEvents` polling in the context of custom platforms
- Fixed `eb local run` to work with `PlatformArn`\s
- Fixed local-remote inconsistency observed after deployments using CodeCommit
- Fixed misspelling in the prompt for whether VPC ELB should be public

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
