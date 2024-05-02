from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..schemas import ConversionStatusCheckResponse
from ..services import s3_service

router = APIRouter()

@router.get("/get_conversion_status/{file_id}", response_model=ConversionStatusCheckResponse)
async def get_conversion_status(file_id: str):
    try:
        status = s3_service.check_conversion_status(file_id)
        return ConversionStatusCheckResponse(status=status, file_id=file_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_converted_file/{file_id}")
async def get_converted_file(file_id: str):
    try:
        file_response = s3_service.fetch_converted_file(file_id)
        return StreamingResponse(file_response, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))