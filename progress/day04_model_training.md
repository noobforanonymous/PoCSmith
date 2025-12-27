# Day 4 - Model Fine-tuning

**Focus:** Fine-tune CodeLlama-7B on exploit generation dataset

## Goals

- Set up training environment
- Download CodeLlama-7B model
- Configure QLoRA for 6GB VRAM
- Train model on 1,472 samples
- Validate results

## What I Did

### 1. Environment Setup
- Created Python virtual environment
- Installed PyTorch 2.9.1 + CUDA 12.8
- Installed transformers, PEFT, TRL, bitsandbytes
- Total download: approximately 3GB dependencies

### 2. Model Download
- Downloaded CodeLlama-7B-hf from Hugging Face
- Size: 13GB (7 billion parameters)
- Format: safetensors (faster loading)
- Cached locally for offline training

### 3. Training Configuration

**QLoRA Settings (6GB VRAM Optimization):**
```python
- Load in 4-bit (nf4 quantization)
- Double quantization enabled
- bf16 compute dtype (RTX 40-series)
- Paged AdamW optimizer
```

**LoRA Parameters:**
```python
- Rank: 64
- Alpha: 16
- Dropout: 0.1
- Target modules: q_proj, v_proj
```

**Training Hyperparameters:**
```python
- Epochs: 3
- Batch size: 1 (with gradient accumulation x4)
- Learning rate: 2e-4
- Max sequence length: 1024 tokens
- Gradient checkpointing: enabled
```

### 4. Training Execution

**Dataset:**
- Train: 1,178 samples
- Val: 147 samples
- Test: 147 samples

**Training Time:** 3 hours 17 minutes

**Hardware Usage:**
- VRAM: 5.5GB / 6GB
- CPU: Minimal
- Disk: 13GB model + 350MB adapters

### 5. Training Results

**Metrics:**
```
Initial Loss: 1.20
Final Loss: 0.84
Reduction: 30%
Token Accuracy: 78.4%
```

**Observations:**
- Loss decreased steadily
- No overfitting detected
- Validation loss tracked training loss
- Model generated coherent exploit code

---

## Challenges Faced

### Challenge 1: API Compatibility
**Problem:** TRL 0.26.2 changed API
**Solution:** Used `SFTConfig` instead of `TrainingArguments`, `processing_class` instead of `tokenizer`

### Challenge 2: VRAM Management
**Problem:** 7B model won't fit in 6GB
**Solution:** QLoRA 4-bit quantization + gradient checkpointing

### Challenge 3: Batch Size
**Problem:** OOM errors with batch_size=2
**Solution:** batch_size=1 with gradient_accumulation_steps=4

---

## Model Output Quality

**Tested on:**
1. Linux shellcode generation - Success
2. HTTP buffer overflow exploit - Success
3. CVE-based exploit generation - Success

**Quality Assessment:**
- Code structure is correct
- Comments are relevant
- Compilation instructions included
- Realistic exploit patterns

---

## Model Backup

Created compressed backup:
- File: `backups/pocsmith-v1_*.tar.gz`
- Size: approximately 350MB (compressed)
- Contents: LoRA adapters + tokenizer files

---

## Next Steps

**Day 5:** Build production framework
- CVE parser
- PoC generator wrapper
- Shellcode generator
- CLI interface

---

## Lessons Learned

1. **QLoRA is essential** for consumer GPU training
2. **bf16 works better** than fp16 on RTX 40-series
3. **Gradient checkpointing** trades speed for memory
4. **Small dataset works** if quality is high (1,472 samples sufficient)
5. **Loss reduction of 30%** is excellent for 3 epochs

---

Status: Model training complete, ready to build framework.
