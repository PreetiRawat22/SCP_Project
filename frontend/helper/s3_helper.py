import sys
import boto3
from botocore.exceptions import ClientError

class Upload_File(object):
    def __init__(self):
        self.s3=boto3.resource('s3', region_name='us-east-1')
        
    def create_bucket(self, bucket_name):
         
         if((self.s3.Bucket(bucket_name) in self.s3.buckets.all())==False):
            try:
                
                bucket = self.s3.create_bucket(Bucket=bucket_name)
            except ClientError as ex:
                print(ex)
                sys.exit('error while bucket creation')
                return False
            bucket.wait_until_exists()
            return True
         else:
             print('bucket already exists.')
             return True
            
    def upload_file(self, bucket_name, file_content, file_name):
        try:
            object = self.s3.Object(bucket_name, file_name)
            result = object.put(Body=file_content)
            
        except ClientError as ex:
            print(ex)
            return False
        return True
        
    def download_file(self, bucket_name, file_name):
        s3=boto3.client('s3', region_name='us-east-1')
        try:
            response = s3.download_file(bucket_name, file_name, "attachments")
            return response
            
        except ClientError as ex:
            print(ex)
        return response
        
    def get_object_access_url(self, bucket_name, file_name):
        s3=boto3.client('s3', region_name='us-east-1')
        # Generate the URL to get 'key-name' from 'bucket-name'
        url = s3.generate_presigned_url(
        ClientMethod='get_object',
        
        Params={
        'Bucket': bucket_name,
        'Key': file_name
        })
        return url
