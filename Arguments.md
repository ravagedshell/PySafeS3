
# PySafeS3 Arguments
Here are explanations of available arguments for use with the PySafeS3 Client

**Return to [README.md](README.md)**

# PySafeS3Backup Client:
PySafeS3Backup.py is the part of this client that backs the contents up to S3. It leverages PySafeS3Core.py, boto3, and various open-source python packages.

## Required
The following is a list of bare minimum arguments that must be specified for the script to work propery.
### passphrase
```
--passphrase [string passphrase]
```
The passphrase is the secret used to encrypt or decrypt documents. For now, we'll accept a plaintext entry, but we're working on migrating this to a more secure method.
### path
```
--path [string /path/to/files]
```
The path is used to determine and generate a manifest of all the files to be backed up. This should be a local filesystem path.
### s3BucketName
```
--s3BucketName [string yours3bucketname]
```
The s3BucketName is used to determine where to upload files to. This must be a bucket within your AWS Credentials scope of management; you must have read/write permissions on this bucket.
### s3BucketRegion
```
--s3BucketRegion [string region]
```
The s3BucketRegion is used to define the region the bucket identified in --s3BucketName is located. This is used to generate the Config for boto3 connections.


## Optional
The below is a list of option arguments you can use to help select needed functionality in your script.
### s3KeyPrefix
```
--s3KeyPrefix [string prefix]
```
If you want to upload the files in a separate root folder such that they appear as __hostname__/path/to/files instead of just path/to/files, use this option.
### s3StorageClass
```
--s3StorageClass [int (0-6) default=0]

Accepted Values:
0 - Standard
1 - Standard Infrequent Access
2 - Standard Intelligent Tiering
3 - One Zone Infrequent Access
4 - Glacier Instant Retreival
5 - Glacier Flexible Retreival
6 - Glacier Deep Archive
```
Not yet implemented; but this will enable you to upload to a specific storage tier from the start rather than having to configure S3 Lifecycle policies and wait for them to kick in.

See [https://aws.amazon.com/s3/storage-classes](https://aws.amazon.com/s3/storage-classes/) for most recent storage tier details.
### localBackupPath
```
--localBackupPath [string /path/to/backups]
```
This option is the local filesystem path the the .tar.gz.gpg/.gpg files will be written and stored in.
### obfuscateBackup
```
--obfuscateBackup [bool default=False]
```
Not yet implemented. Setting this option to 'True' will utilize the UUID of each encrypted file found in the manifest so that the name of a document does not give hints to it's contents. For Paranoid users.
### encryptManifest
```
--encryptManifest [bool default=False]
```
Not yet implemented. Setting this option to 'True' will encrypt the manifest file to protect the confidentiality of its contents. If you're obfuscating the backups, you should be encrypting the manifest as well. For Paranoid users.
### base64Encoding
```
--base64Encoding [bool default=False]
```
This method determines whether to output the GPG document in base64 encoded format, which could be useful for sending over email or some other form of communications that validates/sanitizes unsafe characters.
### deleteAfterUpload
```
--deleteAfterUpload [bool default=False]
```
Setting this option to 'True' will delete the local .tar.gz.gpg / .gpg variant of the file after it has been sucesfully uploaded to S3.
### deletionParanoiaLevel
```
--deletionParanoiaLevel [int default=0]
```
Setting this option determines how many times a file will be overwritten if the deleteAfterUpload option is set to True. The default is 0, meaning that by default the file will not be overwritten. Avoid if you're on an SSD. If overwriting, I recommend overwriting a minimum of 3 times using /udev/random
### deletionParanoiaMethod
```
--deletionParanoiaMethod [string (random | zero) default=random]
```
This option selects what method to use when overwriting the document. The default is random, which selects /udev/random as the dd input file. Setting 'zero' sets dd to utilize /udev/zero instead. The more secure method is /udev/random.
### skipCompression
```
--skipCompression [bool default=False]
```
Not implemented yet. If set to 'True', this method will bypass the gzip compression of a document and just encrypti it.
### verbosity
```
--verbosity [string (ALL|PARTIAL|NONE) default=ALL]
```
Not implemented yet. This option will set the output verbosity of the script.
### awsCredentials
```
--awsCredentials [string /path/to/credentials]
```
this option indciates the path of the file containing your AWS Access ID and Secret. If not utilized, it defaults to ~/.aws/aws_credentials.
### maxBandwidthSize
```
--maxBandwidthSize [float default=1.5]
```
This option sets the amount of bandwidth you're to utilize for uploads/downloads. I left the default at 1.5 since I'm in rural America and we have attrocious network options.
### maxBandwidthUnits
```
--maxBandwidthUnits [string (KB | MB | GB | TB) default=MB]
```
Select the unit type to calculate your bandwidth in. The default is MB. This is used to convert maxBandwidthSize into bytes.
### multiPartUploadSize
```
--multiPartUploadSize [int default=2]
```
Select the threshold for when to utilize the multi-part upload method. The multi-part upload method is good for large files or if you're on a slower connection as it has methods for stopping/restarting. Measured in GB.
### manifestOutputFile
```
--manifestOutputFile [string /path/to/manifest]
```
Select the local path to output your manifest file to. By default a manifest file called manifest-{UUID}.json will be placed in your current working directory when the script completed.

# PySafeS3Restore Client:

## Required

## Optional

