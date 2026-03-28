from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.repositories.model_repo import ModelRepository
from app.services.model_service import ModelService

router = APIRouter(prefix="/generate", tags=["Inference"])

@router.post("/{model_id}")
def generate(model_id: str, prompt: str, db: Session = Depends(get_db)):

    model_record = ModelRepository.get_by_id(db, model_id)
    
    if not model_record:
        return {"error": "Model not strictly registered internally!"}

    model, tokenizer = ModelService.load_model(model_record)

    inputs = tokenizer(prompt, return_tensors="pt")

    # Prevent token loops (like 'stairs stairs stairs') and add dynamic sampling
    outputs = model.generate(
        **inputs, 
        max_length=100,
        do_sample=True,
        temperature=0.7,
        top_k=50,
        top_p=0.95,
        repetition_penalty=1.2,
        pad_token_id=tokenizer.eos_token_id
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return {"response": response}
