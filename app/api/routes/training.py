from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.training import TrainRequest
from app.services.training_service import TrainingService

router = APIRouter(prefix="/train", tags=["Training"])

FAKE_USER_ID = "11111111-1111-1111-1111-111111111111"


@router.post("/")
def start_training(request: TrainRequest, db: Session = Depends(get_db)):
    return TrainingService.start_training(db, FAKE_USER_ID, request)
