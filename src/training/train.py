#!/usr/bin/env python3
"""
ExploitGPT Fine-tuning Script
Optimized for RTX 4050 (6GB VRAM) using QLoRA 4-bit quantization
"""

import json
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig
import os

# Configuration
MODEL_NAME = "codellama/CodeLlama-7b-hf"  # Start with 7B model
OUTPUT_DIR = "models/exploitgpt-v1"
DATA_DIR = "data/processed/FINAL_COMPLETE"

# QLoRA config for 6GB VRAM
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

# LoRA config
lora_config = LoraConfig(
    r=16,  # Rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],  # Attention matrices only
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

def load_data():
    """Load training data from JSONL"""
    print("Loading data...")
    
    def load_jsonl(file_path):
        data = []
        with open(file_path, 'r') as f:
            for line in f:
                item = json.loads(line)
                # Format into single text field
                formatted_text = f"""### Instruction:
{item['instruction']}

### Input:
{item['input']}

###Response:
{item['output']}"""
                item['text'] = formatted_text
                data.append(item)
        return data
    
    train_data = load_jsonl(f"{DATA_DIR}/train.jsonl")
    val_data = load_jsonl(f"{DATA_DIR}/validation.jsonl")
    
    print(f"Loaded {len(train_data)} train, {len(val_data)} val samples")
    
    return Dataset.from_list(train_data), Dataset.from_list(val_data)

def format_prompt(sample):
    """Format data into instruction-following prompt"""
    return f"""### Instruction:
{sample['instruction']}

### Input:
{sample['input']}

### Response:
{sample['output']}"""

def main():
    print("="*60)
    print("ExploitGPT Training - Optimized for RTX 4050")
    print("="*60)
    
    # Load data
    train_dataset, val_dataset = load_data()
    
    # Load tokenizer
    print("\nLoading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    # Load model with 4-bit quantization
    print("\nLoading model with 4-bit quantization...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    
    # Prepare model for k-bit training
    model = prepare_model_for_kbit_training(model)
    
    # Add LoRA adapters
    print("\nAdding LoRA adapters...")
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Training config - OPTIMIZED FOR 6GB VRAM
    training_config = SFTConfig(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=4,
        gradient_checkpointing=True,
        optim="paged_adamw_8bit",
        learning_rate=2e-4,
        weight_decay=0.01,
        fp16=False,
        bf16=True,
        max_grad_norm=0.3,
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
        logging_steps=10,
        save_strategy="steps",
        save_steps=100,
        eval_strategy="steps",
        eval_steps=100,
        do_eval=True,
        report_to="none",
        max_steps=-1,
        logging_dir=f"{OUTPUT_DIR}/logs",
        # SFT-specific  
        dataset_text_field="text",
        max_length=1024,
        packing=False
    )
    
    # Initialize trainer
    print("\nInitializing trainer...")
    trainer = SFTTrainer(
        model=model,
        args=training_config,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processing_class=tokenizer,
        peft_config=lora_config
    )
    
    # Train!
    print("\nStarting training...")
    print(f"Device: {model.device}")
    print(f"VRAM available: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    
    trainer.train()
    
    # Save final model
    print("\nSaving model...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    print("\n✅ Training complete!")
    print(f"Model saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
