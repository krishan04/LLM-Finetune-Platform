from app.repositories.model_repo import ModelRepository
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import sys

is_mac = sys.platform == "darwin"

class ModelService:

    @staticmethod
    def register_model(db, user_id, base_model, adapter_path):
        data = {
            "user_id": user_id,
            "base_model": base_model,
            "version": "v1",
            "adapter_path": adapter_path,
            "quantization": "None" if is_mac else "4bit"
        }
        return ModelRepository.create(db, data)

    @staticmethod
    def load_model(model_record):
        base_model = model_record.base_model
        adapter_path = model_record.adapter_path

        tokenizer = AutoTokenizer.from_pretrained(base_model)

        # Mac aborts when pushing generic loads into MPS natively on fork tests. Lock explicit map constraint
        base = AutoModelForCausalLM.from_pretrained(
            base_model,
            device_map="cpu" if is_mac else "auto"
        )

        model = PeftModel.from_pretrained(base, adapter_path)

        return model, tokenizer
