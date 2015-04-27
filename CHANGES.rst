=========
Changelog
=========

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