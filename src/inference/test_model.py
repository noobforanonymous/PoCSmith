#!/usr/bin/env python3
"""
ExploitGPT - Working Inference Script  
Load base model + adapters correctly
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import argparse
import warnings
warnings.filterwarnings('ignore')


import os
from pathlib import Path

# Use cached model to avoid downloads
CACHE_DIR = Path.home() / ".cache/huggingface/hub/models--codellama--CodeLlama-7b-hf"
SNAPSHOT_DIR = list((CACHE_DIR / "snapshots").glob("*"))[0] if CACHE_DIR.exists() else None


BASE_MODEL = str(SNAPSHOT_DIR) if SNAPSHOT_DIR else "codellama/CodeLlama-7b-hf"
ADAPTER_PATH = "models/exploitgpt-v1"

print(f"Using base model: {BASE_MODEL}")


def load_model(use_4bit=True):
    """Load model with adapters"""
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(ADAPTER_PATH)
    
    print(f"Loading base model: {BASE_MODEL}...")
    
    if use_4bit:
        # Use 4-bit like training for memory efficiency
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            local_files_only=False  # Allow using HF cache
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            local_files_only=False
        )
    
    print(f"Loading LoRA adapters from: {ADAPTER_PATH}...")
    model = PeftModel.from_pretrained(
        model,
        ADAPTER_PATH,
        is_trainable=False,
        device_map={"": 0}
    )
    
    model.eval()
    print("Model ready!")
    return model, tokenizer


def generate_exploit(model, tokenizer, instruction, input_text="", max_tokens=256):
    """Generate from model"""
    if input_text:
        prompt = f"""### Instruction:
{instruction}

### Input:
{input_text}

### Response:
"""
    else:
        prompt = f"""### Instruction:
{instruction}

### Response:
"""
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    print("Generating (30-60 seconds)...")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract response only
    if "### Response:" in result:
        return result.split("### Response:")[1].strip()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="Generate a simple Linux x86 reverse shell shellcode.")
    parser.add_argument("--input", default="")
    parser.add_argument("--max-tokens", type=int, default=200)
    parser.add_argument("--no-4bit", action="store_true", help="Don't use 4-bit quantization")
    args = parser.parse_args()
    
    # Load
    model, tokenizer = load_model(use_4bit=not args.no_4bit)
    
    print("\n" + "="*60)
    print("GENERATING EXPLOIT")
    print("="*60)
    print(f"Instruction: {args.prompt}")
    if args.input:
        print(f"Input: {args.input}")
    print("="*60 + "\n")
    
    # Generate
    output = generate_exploit(model, tokenizer, args.prompt, args.input, args.max_tokens)
    
    print("\n" + "="*60)
    print("RESULT:")
    print("="*60)
    print(output)
    print("="*60)


if __name__ == "__main__":
    main()
