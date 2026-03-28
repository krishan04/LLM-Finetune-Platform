from celery import Celery
import app.db.base # Load all models into memory to fix NoReferencedTableError!

celery_app = Celery(
    "llm_finetune",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.workers.training_worker"]
)
