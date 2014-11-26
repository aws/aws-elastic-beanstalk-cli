
=========
Changelog
=========

-------------------
3.0.10 (2014-11-24)
-------------------
- Fixed parsing error for uploads in a s3 bucket with auto-deletion policy
- Fixed terminated environment issues
- No longer uploads application if the application version already exists in s3
- Default database username changed from admin to ebroot
- Trim application version description if it is too long
- Application version no longer includes git hash