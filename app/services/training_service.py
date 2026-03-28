from sqlalchemy.orm import Session
from datetime import datetime
from app.repositories.experiment_repo import ExperimentRepository
from app.workers.training_worker import run_training_job

class TrainingService:

    @staticmethod
    def start_training(db: Session, user_id, request):
        
        exp_data = {
            "user_id": user_id,
            "dataset_id": request.dataset_id,
            "model_id": None,
            "status": "queued",
            "hyperparameters": {
                "base_model": request.base_model,
                "lora_r": request.lora_r,
                "learning_rate": request.learning_rate
            },
            "started_at": datetime.utcnow()
        }

        experiment = ExperimentRepository.create(db, exp_data)

        # push async job
        run_training_job.delay(str(experiment.id))

        return experiment
