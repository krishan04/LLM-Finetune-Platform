import uuid
from sqlalchemy import Column, String, TIMESTAMP, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base_class import Base

class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"))
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"))

    status = Column(String)

    hyperparameters = Column(JSON)
    training_logs = Column(String)

    loss = Column(Float)
    accuracy = Column(Float)
    eval_metrics = Column(JSON)

    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)
