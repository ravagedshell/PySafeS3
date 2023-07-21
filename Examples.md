
# PySafeS3 S3 Client Examples
Here are some examples of utilizes the PySafeS3 Client to backup or restore data.

**Return to [README.md](README.md)**

## Basic Example
The bare minimums.
```bash
python PySafeS3Backup.py --path /home/user/ebooks \
--passphrase 'asimplepassword123' \
--s3BucketName 'myamazons3bucketrandom' \
--s3BucketRegion 'us-east-1' \
```

## Custom S3 Key Prefix and Local Backup Folder
Use a custom local backup folder and append a prefix to the files in S3.
```bash
python PySafeS3Backup.py --path /home/user/ebooks \
--passphrase 'asimplepassword123' \
--s3BucketName 'myamazons3bucketrandom' \
--s3BucketRegion 'us-east-1' \
--s3KeyPrefix 'myprefix' \
--localBackupPath /home/user/ebooks/custombackup
```

## Overwrite on Upload Complete
Overwrite the local backup file 3 times using /udev/random before deleting.
```bash
python PySafeS3Backup.py --path /home/user/ebooks \
--passphrase 'asimplepassword123' \
--s3BucketName 'myamazons3bucketrandom' \
--s3BucketRegion 'us-east-1' \
--deleteAfterUpload True \
--deletionParanoiaLevel 3 \
--deletionParanoiaMethod 'random'
```

## Set Max Bandwidth
This example sets the max bandwidth for uploads/downloads to 100MB/s
```bash
python PySafeS3Backup.py --path /home/user/ebooks \
--passphrase 'asimplepassword123' \
--s3BucketName 'myamazons3bucketrandom' \
--s3BucketRegion 'us-east-1' \
--maxBandwidthSize 100 \
--maxBandwidthUnits 'MB'
```

## Use Different AWS Credentials
This example uses a seperate AWS credentials file (other than ~/.aws/aws_credentials)
```bash
python PySafeS3Backup.py --path /home/user/ebooks \
--passphrase 'asimplepassword123' \
--s3BucketName 'myamazons3bucketrandom' \
--s3BucketRegion 'us-east-1' \
--awsCredentials '/home/user/other/aws_credentials'
```

Other examples coming soon.
