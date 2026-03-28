from sqlalchemy.orm import Session
from app.db.models.experiment import Experiment

class ExperimentRepository:

    @staticmethod
    def create(db: Session, data: dict):
        exp = Experiment(**data)
        db.add(exp)
        db.commit()
        db.refresh(exp)
        return exp

    @staticmethod
    def update_status(db: Session, exp_id, status):
        exp = db.query(Experiment).filter(Experiment.id == exp_id).first()
        exp.status = status
        db.commit()
        return exp
