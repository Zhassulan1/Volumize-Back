from django.conf import settings

from datetime import datetime
from random import randint

import boto3


def generate_key(author_role, _type, name):
    return author_role + "_"  + _type + f'_{randint(0, 10000000)}_' + f'{datetime.timestamp(datetime.now())}_' + name


def upload_bytes(bytes_, key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    s3.upload_fileobj(
        bytes_, 
        bucket_name, 
        key,
        ExtraArgs={'ACL': 'public-read'}  # Setting ACL to public-read
    )

    file_url = f'https://{bucket_name}.s3.amazonaws.com/{key}'
    return file_url


def upload_file(file_name, key):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param key: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    # Upload the file
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    try:
        response = s3_client.upload_file(
            file_name,
            bucket,
            key,
            ExtraArgs={'ACL': 'public-read'},
        )
        print("Response: ", response)
    except Exception as e:
        print(e)
        return
    
    file_url = f'https://{bucket}.s3.amazonaws.com/{key}'
    return file_url
