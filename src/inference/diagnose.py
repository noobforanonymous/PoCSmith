#!/usr/bin/env python3
"""Diagnose model loading issue"""

import torch
print("Step 1: Imports OK")

from transformers import AutoTokenizer
print("Step 2: Tokenizer import OK")

from peft import AutoPeftModelForCausalLM
print("Step 3: PEFT import OK")

print("\nStep 4: Loading tokenizer...")
MODEL_PATH = "models/exploitgpt-v1"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
print(f"Tokenizer loaded: {len(tokenizer)} tokens")

print("\nStep 5: Loading model (this may hang)...")
print("If this hangs, the issue is AutoPeftModelForCausalLM.from_pretrained()")

try:
    model = AutoPeftModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        low_cpu_mem_usage=True
    )
    print("Model loaded successfully!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
