from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
from ..schemas import FileIDsResponse, FileIDsRequest, ConversionStatusesResponse
from ..services import s3_service, conversion_service

router = APIRouter()

@router.post("/upload_files", response_model=FileIDsResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    try:
        file_ids = s3_service.upload_files(files)
        return FileIDsResponse(file_ids=file_ids)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.post("/convert_files", response_model=ConversionStatusesResponse)
async def convert_files(request: FileIDsRequest):
    try:
        conversion_statuses = conversion_service.convert_files(request.file_ids)
        return ConversionStatusesResponse(conversion_statuses=conversion_statuses)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))