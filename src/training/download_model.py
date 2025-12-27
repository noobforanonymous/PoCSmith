#!/usr/bin/env python3
"""Download CodeLlama-7B model"""
from transformers import AutoTokenizer, AutoModelForCausalLM

print("Downloading CodeLlama-7B model...")
print("This will download ~13GB - may take 10-20 minutes")

tokenizer = AutoTokenizer.from_pretrained('codellama/CodeLlama-7b-hf')
print("Tokenizer downloaded")

model = AutoModelForCausalLM.from_pretrained('codellama/CodeLlama-7b-hf')
print("Model downloaded")

print("\nDownload complete! Model cached locally.")
