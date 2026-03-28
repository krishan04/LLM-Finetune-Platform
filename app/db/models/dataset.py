import uuid
from sqlalchemy import Column, String, TIMESTAMP, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base_class import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    name = Column(String)
    file_path = Column(String)
    format = Column(String)
    status = Column(String)

    size_mb = Column(Float)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
