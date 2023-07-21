#!/usr/bin/env python

# PySafeS3 is a tool to encrypt data and upload it to S3.
# 1. Archives data in tar.gz format
# 2. Encrypts data using given GnuPG key
# 3. Uploads data to S3

# Author: ravagedshell <github.com/ravagedshell>

# Some inspiration from:
# https://github.com/sadsfae/misc-scripts/blob/master/python/backup-file.py

# ### IMPORTANT NOTES ###

# On AWS Credentials:
# If passing custom credentials file it must be a text file with no formatting, and only have two lines.
# The first line should contain ontain the AWS Acces Key ID and nothing else.
# The second line should contain only the AWS Access Key Secret and nothing else.
# If you fail to provide credentials it will fallback to ~/.aws/credentials


import argparse, sys, datetime, boto3, PySafeS3Core, argcomplete, base64, uuid, time, json
from datetime import timedelta
from botocore.config import Config
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig


# Define Script Arguments and setup Auto-tab completion
parser = argparse.ArgumentParser()
argcomplete.autocomplete(parser)

# Define Required Arguments
requiredArgs=parser.add_argument_group('Required Arguments')
requiredArgs.add_argument('--passphrase', required=True, help="Passphrase used to encrypt/decrypt the data")
requiredArgs.add_argument('--path', required=True, help="Absolute path (i.g /path/to/file.txt) of file/directory to backup")
requiredArgs.add_argument('--s3BucketName', required=True, help="Name of the S3 Bucket the data will be backed up to")
requiredArgs.add_argument('--s3BucketRegion', required=True, help="Region where the backup S3 Bucket is located")

# Define Optional Arguments
parser.add_argument('--s3KeyPrefix', help="Add a prefix to the uploads so that uploads appear as [key]/fullpath")
parser.add_argument('--s3StorageClass', help="Define the storage class to place these files in; default is Glacier Immediate Access")
parser.add_argument('--localBackupPath', help="Define the local path to use for backups")
parser.add_argument('--obfuscateBackup', default=False, type=bool, help="FOR PARANOIA: set to True to obfuscate uploaded file names and include a mapping in the local manifest")
parser.add_argument('--encryptManifest', default=False, type=bool, help="FOR PARANOIA: set to True to encrypt the local manifest which includes unencrypted hashes and filename mappings; encrypted using passphrase define in --passphrase")
parser.add_argument('--base64Encoding', default=False, type=bool, help="Set to true to output GPG encryption in base64 format for sharing via email, etc. (--armor)")
parser.add_argument('--deleteAfterUpload', default=False, type=bool, help="Set to true to delete local copy after upload to S3.")
parser.add_argument('--deletionParanoiaLevel', default=0, type=int, help="FOR PARANOIA: set the number of times you want to overwrite a file before deleting it from local disk.")
parser.add_argument('--deletionParanoiaMethod', default="random", help="FOR PARANOIA: set the method of overwrite for your file. Options are 'random' or 'zero'.")
parser.add_argument('--verbosity', default='ALL', help="Define the level of ouput; i.g full, quiet, core")
parser.add_argument('--awsCredentials', help="Define location of AWS credentials file if different from ~/.aws/credentials")
parser.add_argument('--maxBandwidthSize', type=float, default=1.5, help="Define the maximum bandiwdth to use for this upload (default in MB/s)")
parser.add_argument('--maxBandwidthUnits', default='MB', help="Define the units of the bandwidth, i.e MB, KB, or GB; default is MB. Used to calculate bytes (maxBandwidthValue * maxBandwidthSize)")
parser.add_argument('--multiPartUploadSize', type=int, default=2, help="Define the size in that we will begin uploading files as multi-part uplods. Default: 2")
parser.add_argument('--manifestOutputFile', help="Define the path to write the output Manifest file to")

# Uncomment when its time to add reading settings from a config file
# parser.add_argument('--configFilePath', default='./configs/config.yml' help="Define the path that contains all the configuration options")

# Parse Arguments
args = parser.parse_args()

# Config general AWS Settings
aws_config = Config(
    region_name = args.s3BucketRegion,
    retries = {
        'max_attempts' : 5,
        'mode' : 'standard'
    }
)

# Max concurrent uploads = 5
# Start multiparts at 2 GB
# Max upload bandwidth = 15Mbps or 1.5MB/s
transfer_config = TransferConfig(
    max_concurrency=5,
    multipart_threshold=PySafeS3Core.getUnitSizeInBytes(args.multiPartUploadSize,'GB'),
    max_bandwidth=PySafeS3Core.getUnitSizeInBytes(args.maxBandwidthSize,args.maxBandwidthUnits)
)

# Select AWS Credentials and Open the S3 Resource Connection
if args.awsCredentials is not None:
    try:
        with open(args.awsCredentials) as openfile:
            secrets = openfile.readlines()
            awsaccesskeyid = (secrets[0]).rstrip('\n')
            awssecretkey = (secrets[1]).rstrip('\n')
    except IOError as Error:
        print("Unable to open the listed credentials file, please check full path. If you are positive the file exists, please check permissions. FullError: ", Error)
    s3 = boto3.resource(
        's3',
        aws_access_key_id=awsaccesskeyid,
        aws_secret_access_key=awssecretkey,
        config=aws_config
    )
else:
    print("Credentials file not loaded, defaulting to ~/.aws/credentials")
    s3 = boto3.resource('s3',config=aws_config)

# Validate that the bucket actually exists
if s3.Bucket(args.s3BucketName).creation_date is not None:
    print("The bucket exists...we can continue")
else:
    print("The bucket does not exist...exiting")

# Decode Secret
secret = base64.b64encode(str.encode(args.passphrase))

# Generate list of files to backup
filesToBackup = PySafeS3Core.generateManifest(args.path)

# Function to upload file to S3 and return dict
# contianing data about the transfer
#
# TODO:
# + S3 Storage Class as s3StorageClass
def uploadFile(s3BucketName,s3Key,localFileName,localFilePath,s3KeyPrefix=None):
    if s3KeyPrefix is not None:
        s3Prefix = str(s3KeyPrefix).rstrip('/')
        s3Location = s3Prefix + '/' + s3Key + localFileName
    else:
        s3Location = s3Key + localFileName
    uploadStatus = dict([
            ('S3_LOCATION', s3Location),
            ('S3_KEY',s3Prefix)
        ])
    try:
        uploadResponse = s3.meta.client.upload_file(
            localFilePath,
            s3BucketName,
            s3Location,
            Config=transfer_config)
    except ClientError as UploadError:
        uploadStatus['BACKUP_STATE'] = False
        uploadStatus['BASIC_ERROR'] = 'Failed to upload file: ' + localFilePath + ' | Received exception from boto3.'
        uploadStatus['FULL_ERROR']  = 'Failed to upload file: ' + localFilePath + '| Received exception from boto3: ' + UploadError 
        return uploadStatus
    uploadStatus['BACKUP_STATE'] = True
    return uploadStatus


# This will need to be reworked so that we append a new entry every
# time a file is sucessfully uploaded. Right now all files must 
# completed before it is complete. We could optionally re-write
# the entire file every time, but that could lead to alot of disk
# i/o, be slow, and really isn't the best way to attack the problem
# if args.manifestOutputFile is not None:
#     manifestFile = open(args.manifestOutPutFile,"x")
# else:
#     manifestFile = open('manifestFile-' + (str(uuid(uuid.uuid4),'UTF-8')) + '.json', "x")
manifest = []
for file in filesToBackup:
    # Time creation of archive 
    archiveCreateStart = time.monotonic()
    data = PySafeS3Core.createArchive(
        file=file,
        base64secret=secret,
        backupdirectory=args.localBackupPath)
    archiveCreateEnd = time.monotonic()
    # Time upload
    s3UploadStart = time.monotonic()
    uploadData = uploadFile(
        s3BucketName=args.s3BucketName,
        s3KeyPrefix=args.s3KeyPrefix,
        s3Key=file['S3_KEY'],
        localFileName=file['BACKUP_FILENAME'],
        localFilePath=file['BACKUP_FULL_PATH'])
    s3UploadEnd = time.monotonic()
    # Add upload data to data
    if uploadData['BACKUP_STATE']:
        data['BACKUP_STATE'] = True
        data['BASIC_ERROR'] = None
        data['FULL_ERROR'] = None
        if args.deleteAfterUpload:
            PySafeS3Core.wipeFile(
                path=file['BACKUP_FULL_PATH'],
                overwrite=args.deletionParanoiaLevel,
                overwritemethod=args.deletionParanoiaMethod
            )
    else:
        data['BACKUP_STATE'] = False
        data['BASIC_ERROR'] = uploadData['BASIC_ERROR']
        data['FULL_ERROR'] = uploadData['FULL_ERROR']
    # Calculate deltas
    archiveDuration = timedelta(seconds=archiveCreateEnd - archiveCreateStart)
    uploadDuration = timedelta(seconds=s3UploadEnd - s3UploadStart)
    # Convert deltas to string
    archiveDurationString = str(archiveDuration)
    uploadDurationString = str(uploadDuration)
    data['ARCHIVE_CREATE_DURATION'] = archiveDurationString
    data['S3_UPLOAD_DURATION'] = uploadDurationString
    # Write results to manfiest list
    manifest.append(data)

if args.manifestOutputFile is not None:
    smanifestFile = open(args.manifestOutPutFile,"x")
else:
    manifestFileUUID = uuid.uuid4()
    manifestFileUUIDString = str(manifestFileUUID)
    manifestFileName = 'manifestFile-' + manifestFileUUIDString + ".json"
    manifestFile = open(manifestFileName, "x")
manifestFile.write(json.dumps(manifest,indent=1))
manifestFile.close()



    