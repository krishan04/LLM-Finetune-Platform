from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class DatasetResponse(BaseModel):
    id: UUID
    name: str
    format: str
    status: str
    size_mb: float
    created_at: datetime

    class Config:
        from_attributes = True
