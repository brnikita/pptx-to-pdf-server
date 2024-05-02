import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import uuid
from ..config import settings

# Initialize the S3 client within the function to avoid issues during imports
def get_s3_client(): 
    return boto3.client(
        's3',
        region_name=settings.aws_access_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key
    )

def upload_files(files):
    s3 = get_s3_client()
    file_ids = []
    for file in files:
        file_id, file_name = upload_file_to_s3(s3, file.file, file.filename)
        file_ids.append({"file_id": file_id, "filename": file_name})
    return file_ids

def upload_file_to_s3(s3, file_object, file_name):
    file_id = str(uuid.uuid4())
    full_file_name = f"input/{file_id}/{file_name}"
    s3.upload_fileobj(Fileobj=file_object, Bucket=settings.bucket_name, Key=full_file_name)
    return file_id, full_file_name

def generate_presigned_url(s3, bucket_name, object_name):
    try:
        response = s3.generate_presigned_url('get_object',
                                             Params={'Bucket': bucket_name, 'Key': object_name},
                                             ExpiresIn=3600)
    except NoCredentialsError:
        print("Credentials not available")
        return None
    return response

def save_file_to_s3(s3, bucket_name, object_name, content):
    try:
        s3.put_object(Bucket=bucket_name, Key=object_name, Body=content)
    except NoCredentialsError:
        print("Credentials not available")

def check_conversion_status(file_id):
    s3 = get_s3_client()
    object_name = f"output/{file_id}.pdf"
    try:
        s3.head_object(Bucket=settings.bucket_name, Key=object_name)
        return "done"
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return "pending"
        else:
            return "error"

def fetch_converted_file(file_id):
    s3 = get_s3_client()
    output_file_key = f"output/{file_id}.pdf"
    try:
        response = s3.get_object(Bucket=settings.bucket_name, Key=output_file_key)
        return response['Body']
    except ClientError as e:
        if e.response['Error']['Code'] == "NoSuchKey":
            return "File not found"
        raise