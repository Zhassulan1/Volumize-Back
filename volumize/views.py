import os
import boto3
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from datetime import datetime
from random import randint

from volumize.generate_mesh import gen, preprocess

def s3_upload_obj(file_obj, key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    s3.upload_fileobj(
        file_obj, 
        bucket_name, 
        key,
        ExtraArgs={'ACL': 'public-read'}  # Setting ACL to public-read
    )

    file_url = f'https://{bucket_name}.s3.amazonaws.com/{key}'
    return file_url


def s3_upload_file(file_name, key):
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



def generate_key(author_role, _type, name):
    return author_role + _type + f'_{randint(0, 10000000)}_' + f'{datetime.timestamp(datetime.now())}_' + name


@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        image_key = generate_key('user', "image", image.name)
        image_url = s3_upload_obj(image, image_key)

        obj_path = gen(image_url)
        # obj_path = preprocess(image_url, foreground_ratio=0.5)

        # print()
        # print("Path to object in local", obj_path)

        obj_key = generate_key('user', "obj", os.path.basename(obj_path))
        obj_url = s3_upload_file(obj_path, obj_key)
        
        # print()
        # print("Path to object in s3", obj_url)
        
        return JsonResponse({'obj_url': obj_url})
    
    return JsonResponse({'error': 'No file uploaded'}, status=400)