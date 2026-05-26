from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.training import TrainRequest, ExperimentResponse
from app.services.training_service import TrainingService

router = APIRouter(prefix="/train", tags=["Training"])

FAKE_USER_ID = "11111111-1111-1111-1111-111111111111"


@router.post("/", response_model=ExperimentResponse)
def start_training(request: TrainRequest, db: Session = Depends(get_db)):
    return TrainingService.start_training(db, FAKE_USER_ID, request)


@router.get("/", response_model=list[ExperimentResponse])
def list_experiments(db: Session = Depends(get_db)):
    return TrainingService.list_experiments(db)


@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(experiment_id: str, db: Session = Depends(get_db)):
    experiment = TrainingService.get_experiment(db, experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment

