#!/usr/bin/env python3
"""Download CodeLlama using transformers directly"""

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

print("Downloading CodeLlama-7B using transformers...")
print("This will download to HuggingFace cache properly")

# This will trigger proper download
tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")
print("Tokenizer downloaded")

# Download model (this will take time)
print("\nDownloading model weights (~13GB)...")
model = AutoModelForCausalLM.from_pretrained(
    "codellama/CodeLlama-7b-hf",
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True
)

print("\nDownload complete!")
print(f"Model type: {type(model)}")
print("Files are now cached properly")
