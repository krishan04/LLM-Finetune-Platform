from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db
from app.services.dataset_service import DatasetService
from app.schemas.dataset import DatasetResponse

router = APIRouter(prefix="/datasets", tags=["Datasets"])


# TEMP: static user_id (we add auth later)
FAKE_USER_ID = "11111111-1111-1111-1111-111111111111"


@router.post("/upload", response_model=DatasetResponse)
def upload_dataset(file: UploadFile, db: Session = Depends(get_db)):
    dataset = DatasetService.upload_dataset(db, file, FAKE_USER_ID)
    return dataset


@router.get("/", response_model=list[DatasetResponse])
def list_datasets(db: Session = Depends(get_db)):
    return DatasetService.list_datasets(db)
