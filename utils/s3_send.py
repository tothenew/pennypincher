import boto3
import os
s3_client = boto3.client('s3')    

def uploadDirectory(path,bucketname,current_datetime):
        s3_client = boto3.client('s3')    
        print(f"Sending report to S3 {bucketname}")
        for root,dirs,files in os.walk(path):
            for file in files:
                s3_client.upload_file(os.path.join(root,file),bucketname,f"{current_datetime}/{file}")