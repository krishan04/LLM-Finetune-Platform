from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model
from datasets import load_dataset
import os


def run_training_pipeline(config):

    dataset_path = config["dataset_path"]
    base_model = config["base_model"]
    output_dir = config["output_dir"]

    # 1. Load dataset
    dataset = load_dataset("json", data_files=dataset_path)["train"]

    # 2. Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    tokenizer.pad_token = tokenizer.eos_token

    def tokenize(example):
        # Dynamically support both {"text": ...} and {"instruction": ..., "output": ...} formats
        if "text" in example:
            content = example["text"]
        else:
            content = f"{example.get('instruction', '')}\n"
            if example.get("input"):
                content += f"{example['input']}\n"
            content += example.get("output", "")
            
        tokenized = tokenizer(
            content,
            truncation=True,
            padding="max_length",
            max_length=512
        )
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized

    dataset = dataset.map(tokenize)

    import sys
    import os
    is_mac = sys.platform == "darwin"  

    # Fix: Rust Tokenizers frequently deadlock in fork()
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    # 3. Load model (Fallback for unsupported systems)
    if not is_mac:
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            load_in_4bit=True,
            device_map="auto"
        )
    else:
        # Mac Fallback: avoid 4-bit, and MUST avoid 'auto' (MPS). 
        # Apple Metal (MPS) natively throws SIGABRT signal 6 when accessed inside a fork() child!
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            device_map="cpu"
        )

    # 4. Apply LoRA
    # Fix: Architecture-specific matching for LoRA target modules
    base_lower = base_model.lower()
    if "gpt2" in base_lower:
        target_modules = ["c_attn"]
    elif "pythia" in base_lower or "gpt-neox" in base_lower:
        target_modules = ["query_key_value"]
    else:
        target_modules = ["q_proj", "v_proj"]

    lora_config = LoraConfig(
        r=config["lora_r"],
        lora_alpha=16,
        target_modules=target_modules,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)

    # 5. Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=2,
        num_train_epochs=20, # Increased from 1 to 20 to allow small models to memorize tiny datasets!
        learning_rate=config["learning_rate"],
        logging_steps=10,
        save_steps=50,
        use_cpu=is_mac # OVERRIDE: Prevent Mac Trainer from forcing MPS compilation!
    )

    # 6. Trainer
    trainer = Trainer(
        model=model,
        train_dataset=dataset,
        args=training_args
    )

    # 7. Train
    trainer.train()

    # 8. Save adapter
    model.save_pretrained(output_dir)

    return output_dir
