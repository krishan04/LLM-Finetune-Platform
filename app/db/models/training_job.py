import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base_class import Base

class TrainingJob(Base):
    __tablename__ = "training_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiments.id"))

    gpu_type = Column(String)
    instance_id = Column(String)
    status = Column(String)
    logs = Column(String)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
