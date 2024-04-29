from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import uuid
import boto3
import requests

app = FastAPI()

# Environment variables
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_ACCESS_REGION = os.getenv('AWS_ACCESS_REGION')
BUCKET_NAME = os.getenv('BUCKET_NAME')
UNOSERVER_URL = os.getenv('UNOSERVER_URL', 'http://unoserver:2002')
CORS_ORIGINS = os.getenv('CORS_ORIGINS', "http://localhost:3000")

# Configure CORS
allowed_origins = [origin.strip() for origin in CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# S3 client setup
s3 = boto3.client(
    's3',
    region_name=AWS_ACCESS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

@app.post("/upload_files")
async def upload_files(files: List[UploadFile] = File(...)):
    file_ids = []
    for file in files:
        file_id = str(uuid.uuid4())
        file_object = file.file
        file_name = f"input/{file_id}/{file.filename}"

        s3.upload_fileobj(file_object, BUCKET_NAME, file_name)
        file_ids.append({"file_id": file_id, "filename": file_name})
    
    return {"file_ids": file_ids}


@app.post("/convert_files")
async def convert_files(file_ids: List[str]):
    conversion_statuses = []

    for file_id in file_ids:
        # Construct S3 file key and download the file
        input_file_key = f"input/{file_id}/{file_id}.pptx"
        output_file_key = f"output/{file_id}.pdf"
        try:
            # Using S3 presigned URL for upload to unoserver
            presigned_url = s3.generate_presigned_url('get_object',
                                                      Params={'Bucket': BUCKET_NAME,
                                                              'Key': input_file_key},
                                                      ExpiresIn=3600)

            # Make a conversion request to unoserver (assumed interface)
            response = requests.post(f"{UNOSERVER_URL}/convert", json={
                'file_url': presigned_url, 
                'output_format': 'pdf'
            })

            if response.status_code == 200:
                # Upload the converted file back to S3
                s3.put_object(Bucket=BUCKET_NAME, Key=output_file_key, Body=response.content)
                status = "done"
            else:
                status = "failed"
        except requests.RequestException:
            status = "failed"
        
        conversion_statuses.append({"file_id": file_id, "status": status})

    return {"conversion_statuses": conversion_statuses}


@app.get("/get_conversion_status/{file_id}")
async def get_conversion_status(file_id: str):
    output_file_key = f"output/{file_id}.pdf"
    try:
        s3_response = s3.head_object(Bucket=BUCKET_NAME, Key=output_file_key)
        if s3_response:
            return {"status": "done", "file_id": file_id}
        else:
            return {"status": "pending", "file_id": file_id}
    except s3.exceptions.NoSuchKey:
        return {"status": "pending", "file_id": file_id}
    except Exception:
        raise HTTPException(status_code=500, detail="Error checking file status")


@app.get("/get_converted_file/{file_id}")
async def get_converted_file(file_id: str):
    output_file_key = f"output/{file_id}.pdf"
    try:
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=output_file_key)
        return StreamingResponse(obj['Body'], media_type="application/pdf")
    except s3.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="File not found")