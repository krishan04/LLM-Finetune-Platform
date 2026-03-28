from pydantic import BaseModel
from uuid import UUID

class TrainRequest(BaseModel):
    dataset_id: UUID
    base_model: str
    lora_r: int = 8
    learning_rate: float = 2e-4
