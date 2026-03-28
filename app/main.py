from fastapi import FastAPI, Depends
import app.db.base # Loads all models to the SQLAlchemy MetaData registry
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.deps import get_db
from app.api.routes import datasets, training, models, inference

app = FastAPI(title="LLM Finetune Platform API", version="0.1.0")

app.include_router(datasets.router)
app.include_router(training.router)
app.include_router(models.router)
app.include_router(inference.router)

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "DB connected ✅"}