#!/bin/bash
bucketname=$1
serviceaccountname=$2


# Parse variables to make sure they're set
if [ -z "$1" ]
then
    echo "S3 Bucket Name was not set...exiting. Please retry..."
    exit 0
fi
if [ -z "$2" ]
then
    echo "IAM User Name for Service Account was not specific. Please retry..."
    exit 0
fi

# Write IAM Policy to configs directory
tee ./configs/iam-policy-$bucketname.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowListBuckets",
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AllowAllOnArchiveBucket",
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::$bucketname",
                "arn:aws:s3:::$bucketname/*"
            ]
        }
    ]
}
EOF

echo "Created IAM Policy Document ./configs/iam-policy-$bucketname.json"

policy=$(aws iam create-policy --policy-name "Customer-IAMPolicy-PySafeS3SvcAcct-$bucketname" --policy-document file://./configs/iam-policy-$bucketname.json --profile personal_prod | grep 'arn')
arn=$(echo $policy | grep -E -o "arn:aws:iam::[0-9]{1,}:policy/(([a-zA-Z0-9\-])|([\.])){1,}")
echo "Succesfully created IAM Policy in AWS with ARN: $arn"

aws iam create-user --user-name $serviceaccountname --profile personal_prod >/dev/null
echo "Succesfully created User with username: $serviceaccountname"

aws iam attach-user-policy --policy-arn $arn --user-name $serviceaccountname --profile personal_prod >/dev/null
echo "Succesfully attached Policy with ARN: $arn to User: $serviceaccountname"

credentials=$(aws iam create-access-key --user-name $serviceaccountname --profile personal_prod)

echo "Generated Access Keys for User: $serviceaccountname"
echo "Your access key ID is:"
echo $credentials | grep -E -o '(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}'

echo "Your secret key is:"
echo $credentials | grep -E -o '([a-zA-Z0-9+/]{40})'