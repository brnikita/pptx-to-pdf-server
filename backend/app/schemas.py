from pydantic import BaseModel
from typing import List

# Pydantic models
class FileIDModel(BaseModel):
    file_id: str
    filename: str

class FileIDsResponse(BaseModel):
    file_ids: List[FileIDModel]

class FileIDsRequest(BaseModel):
    file_ids: List[FileIDModel]

class ConversionStatusModel(BaseModel):
    file_id: str
    status: str

class ConversionStatusesResponse(BaseModel):
    conversion_statuses: List[ConversionStatusModel]

class ConversionStatusCheckResponse(BaseModel):
    status: str
    file_id: str