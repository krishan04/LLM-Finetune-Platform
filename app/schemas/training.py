from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Any

class TrainRequest(BaseModel):
    dataset_id: UUID
    base_model: str
    lora_r: int = 8
    learning_rate: float = 2e-4

class ExperimentResponse(BaseModel):
    id: UUID
    user_id: UUID
    dataset_id: UUID
    model_id: Optional[UUID] = None
    status: str
    hyperparameters: dict[str, Any]
    training_logs: Optional[str] = None
    loss: Optional[float] = None
    accuracy: Optional[float] = None
    eval_metrics: Optional[dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

