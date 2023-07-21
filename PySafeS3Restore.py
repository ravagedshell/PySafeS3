#!/usr/bin/env python



# PySafeS3Restore is a tool to help downlaod and decrypt
# data backed up with the PySafeS3Backup tool.

# Author: ravagedshell <github.com/ravagedshell>

# Some inspiration from
# https://github.com/sadsfae/misc-scripts/blob/master/python/backup-file.py
# On AWS Credentials
# If passing custom credentials file it must be a text file with no formatting, and only have two lines.
# The first line should contain ontain the AWS Acces Key ID and nothing else.
# The second line should contain only the AWS Access Key Secret and nothing else.
# If you fail to provide credentials it will fallback to ~/.aws/credentials

import argparse, sys, datetime, boto3, PySafeS3Core, argcomplete, base64
from botocore.config import Config
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig

# Define Script Arguments and setup Auto-tab completion
parser = argparse.ArgumentParser()
argcomplete.autocomplete(parser)

# Define Required Arguments
requiredArgs=parser.add_argument_group('Required Arguments')
requiredArgs.add_argument('--passphrase', required=True, help="Passphrase used to encrypt/decrypt the data")
requiredArgs.add_argument('--restorePath', required=True, help="Absolute path (i.g /path/to/file.txt) of file/directory to backup")
requiredArgs.add_argument('--s3BucketName', required=True, help="Name of the S3 Bucket the data will be backed up to")
requiredArgs.add_argument('--s3BucketRegion', required=True, help="Region where the backup S3 Bucket is located")
requiredArgs.add_argument('--manifestFile', required=True, help="Manifest file of files to restore")

# Define Optional Arguments
parser.add_argument('--verbosity', default='ALL', help="Define the level of ouput; i.g full, quiet, core")
parser.add_argument('--awsCredentials', help="Define location of AWS credentials file if different from ~/.aws/credentials")
parser.add_argument('--maxBandwidthSize', type=float, default=1.5, help="Define the maximum bandiwdth to use for this download (default in MB/s)")
parser.add_argument('--maxBandwidthUnits', default='MB', help="Define the units of the bandwidth, i.e MB, KB, or GB; default is MB. Used to calculate bytes (maxBandwidthValue * maxBandwidthSize)")


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



if args.manifestOutputFile is not None:
    manifestFile = open(args.manifestOutPutFile,"x")
else:
    manifestFileUUID = uuid.uuid4()
    manifestFileUUIDString = str(manifestFileUUID)
    manifestFileName = 'manifestFile-' + manifestFileUUIDString + ".json"
    manifestFile = open(manifestFileName, "x")
manifestFile.write(json.dumps(manifest,indent=1))
manifestFile.close()

