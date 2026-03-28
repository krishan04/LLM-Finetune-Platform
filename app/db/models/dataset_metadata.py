import uuid
from sqlalchemy import Column, Integer, Float, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base_class import Base

class DatasetMetadata(Base):
    __tablename__ = "dataset_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"))

    num_samples = Column(Integer)
    avg_length = Column(Integer)
    validation_split = Column(Float)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
