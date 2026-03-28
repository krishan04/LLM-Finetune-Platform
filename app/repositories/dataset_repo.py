from sqlalchemy.orm import Session
from app.db.models.dataset import Dataset

class DatasetRepository:

    @staticmethod
    def create(db: Session, data: dict):
        dataset = Dataset(**data)
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset

    @staticmethod
    def get_all(db: Session):
        return db.query(Dataset).all()
