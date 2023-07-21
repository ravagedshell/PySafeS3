
# PySafeS3 S3 Client
PySafeS3 S3 Client is a python script (or set of scripts) that enables you to archive, encrypt, and backup your documents to the cloud using GNU Privacy Guard Symmetric Encryption. 

## Why?
Learning, really. Though it does serve as my main backup server for my home-lab environment. I can go into it more - you can look back at previous commits to see my full explanation.

# Basic Feature List:
- [X] - Create a manifest of files, given a directory.
- [X] - Calculate file hashes (pre-encryption), given a file path.
- [X] - Generate file properties list, given a file path.
- [X] - Create a tar archive given a hash table of file properties.
- [X] - Create a gpg encrypted variant of the previously created tar archive and remove unencrypted tarball.
- [X] - Upload gpg encrypted variant to S3 Bucket of choice. *Added 5/11/22*
- [X] - Ability to delete or overwrite file on upload completion.
- [X] - Encryption using AES256 and Hashing using SHA384
- [ ] - Ask for passphrase in secure popup window
- [ ] - Option to utilize Python Crypto Libraries and Bypass GPG
- [ ] - S3 Storage Tier Choices (Standard, IA, Glacier, Intelligent).
- [ ] - Ability to generate manifest given an S3 bucket.
- [ ] - Option to obfuscate or hide file names in S3 but retain originals in manifest.
- [ ] - Encrypting and archiving of the manifest.
- [ ] - Adding pre-encryption hashes as part of archives in S3 rather than in manfiest.
- [ ] - Ability to skip hashing or archiving, or both (speed demon mode).
- [ ] - Incremental archiving, given a manifest. Ignore and only upload files that have changes or not been uploaded since last run.
- [ ] - Single file restore, including pre-encryption hash verification.
- [ ] - Bulk restore, given a manifest file.
- [ ] - Kill switch for S3 files.
- [ ] - Integration for AWS Secrets Manager.
- [ ] - Integration with pass, a lightweight password manager for Linux [https://www.passwordstore.org/].
- [ ] - Integration with Tomb, an easier way to manage LUKS Containers [https://www.dyne.org/software/tomb/].
- [ ] - Support for Windows Operating Systems {relies on ability to bypass GPG}

# PySafeS3Backup Basic Use

You can backup a folder or file by running PySafeS3Backup:

```bash
    PySafeS3Backup.py --s3BucketName '<yourS3bucket>' \
    --s3BucketRegion '<bucket-region>' \
    --passphrase '<somePassPhrase>' \
    --path '<pathToBackup>'
```
## Additional Arguments:
**Refer to [Arguments.md](Arguments.md) for information about available arguments and use cases.**


# Decrypting a File
For now, since I haven't worked on the restore part, you would simply run the following and enter your encryption passphrase when prompted:
```bash
    gpg -d <filename>.tar.gz.gpg | tar -xvzf -
```

# Examples
**Please visit [Examples.md](Examples.md) to view some example uses of this script.**

# Contributing
Don't. 