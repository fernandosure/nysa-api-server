import boto3
import botocore
from flask import current_app
s3 = boto3.resource('s3')


def s3_object(key):
    return s3.Object(current_app.config['AWS_S3_BUCKET'], key)


def s3_get_object_contents(key):
    try:
        return s3.Object(current_app.config['AWS_S3_BUCKET'], key).get()
    except botocore.exceptions.ClientError as ex:
        if ex.response['Error']['Code'] == 'NoSuchKey':
            return None


def s3_get_list_of_objects():
    try:
        bucket = s3.Bucket(current_app.config['AWS_S3_BUCKET'])
        return bucket.objects.all()
    except:
        return []
