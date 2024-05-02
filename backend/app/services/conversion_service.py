import requests
import os
import boto3
from typing import List
from ..schemas import FileIDModel, ConversionStatusModel
from .s3_service import generate_presigned_url, save_file_to_s3
from ..config import settings

def convert_files(file_ids: List[FileIDModel]) -> List[ConversionStatusModel]:
    conversion_statuses = []
    temp_dir = "./temp_downloads"
    os.makedirs(temp_dir, exist_ok=True)
    
    s3 = boto3.client(
        's3',
        region_name=settings.aws_access_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key
    )

    for file_info in file_ids:
        input_file_key = file_info.filename
        output_file_key = f"output/{file_info.file_id}.pdf"
        status = "pending"  # Default to pending

        try:
            presigned_url = generate_presigned_url(s3, settings.bucket_name, input_file_key)
            if not presigned_url:
                continue

            # Download the file to convert
            file_response = requests.get(presigned_url)
            temp_file_path = os.path.join(temp_dir, f"{file_info.file_id}")
            with open(temp_file_path, 'wb') as temp_file:
                temp_file.write(file_response.content)

            # Convert the file by sending it to the unoserver
            with open(temp_file_path, 'rb') as file_to_convert:
                files = {
                    "file": (input_file_key, file_to_convert),
                    "convert-to": (None, "pdf"),
                }
                response = requests.post(settings.unoserver_url + "/request", files=files)

            os.remove(temp_file_path)  # Cleanup the temporary file

            # If conversion successful, save to S3
            if response.status_code == 200:
                save_file_to_s3(s3, settings.bucket_name, output_file_key, response.content)
                status = "done"
            else:
                status = "failed"

        except requests.RequestException as e:
            print(f"Request to unoserver failed: {e}")
            status = "failed"

        conversion_statuses.append(ConversionStatusModel(file_id=file_info.file_id, status=status))

    return conversion_statuses