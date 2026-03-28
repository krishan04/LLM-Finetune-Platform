from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.repositories.model_repo import ModelRepository

router = APIRouter(prefix="/models", tags=["Models"])

@router.get("/")
def list_models(db: Session = Depends(get_db)):
    return ModelRepository.get_all(db)
