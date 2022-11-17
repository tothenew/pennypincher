import logging
import boto3
from botocore.exceptions import ClientError
import os



def s3_upload_html(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True       

s3_client = boto3.client('s3')    

def uploadDirectory(path,bucketname,current_datetime):
        print("csv"+path)
        print("csv_bucket"+bucketname)
        path="/home/riya/pennypicher/pennypincher/pennypincher_csv_report"
        for root,dirs,files in os.walk(path):
            for file in files:
                s3_client.upload_file(os.path.join(root,file),bucketname,f"{current_datetime}/{file}")

#uploadDirectory(path,bucketname)

