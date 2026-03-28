from sqlalchemy.orm import Session
from app.db.models.model import Model

class ModelRepository:

    @staticmethod
    def create(db: Session, data: dict):
        model = Model(**data)
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    @staticmethod
    def get_all(db: Session):
        return db.query(Model).all()

    @staticmethod
    def get_by_id(db: Session, model_id):
        return db.query(Model).filter(Model.id == model_id).first()
