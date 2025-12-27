# ExploitGPT - Model Fine-tuning Documentation

## Overview

Successfully fine-tuned CodeLlama-7B on exploit generation using QLoRA 4-bit quantization on RTX 4050 (6GB VRAM).

## Model Selection

**Base Model:** `codellama/CodeLlama-7b-hf`

**Why CodeLlama?**
- Specialized for code generation
- Smaller than general LLMs (7B vs 70B)
- Better at understanding code structure
- Can run on consumer hardware

**Alternatives Considered:**
- Llama 3 8B - Too large for 6GB VRAM
- CodeLlama 13B - Requires 12GB+ VRAM
- GPT-based models - Closed source

## Training Configuration

### Hardware
- **GPU:** NVIDIA RTX 4050 Laptop (6GB VRAM)
- **VRAM Usage:** 5.9 GB / 6.0 GB (96%)
- **Temperature:** ~73°C stable

### QLoRA Configuration
```python
BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)
```

### LoRA Parameters
```python
LoraConfig(
    r=16,                    # Rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
```

**Trainable Parameters:** 8,388,608 (0.12% of total)

### Training Hyperparameters
- **Epochs:** 3
- **Batch Size:** 1 (with gradient accumulation=4)
- **Learning Rate:** 2e-4
- **Optimizer:** paged_adamw_8bit
- **Precision:** bfloat16
- **Max Sequence Length:** 1024
- **Gradient Checkpointing:** Enabled

## Dataset

- **Total Samples:** 1,472
- **Training:** 1,177 (80%)
- **Validation:** 147 (10%)
- **Test:** 148 (10%)

**Composition:**
- CVE→Exploit pairs: 407
- Shellcode examples: 1,065

**Data Format:**
```json
{
  "instruction": "Generate a PoC exploit for CVE-XXXX...",
  "input": "Vulnerability Description: ...",
  "output": "/* Exploit code */",
  "text": "### Instruction:\n...\n### Response:\n..."
}
```

## Training Results

### Performance Metrics
| Metric | Start | End | Improvement |
|--------|-------|-----|-------------|
| Loss | 1.20 | 0.84 | -30% |
| Token Accuracy | 72.6% | 78.4% | +5.8% |
| Eval Loss | N/A | 0.926 | Stable |

### Training Progress
- **Total Steps:** 885 (295 per epoch)
- **Time:** 3 hours 17 minutes
- **Speed:** ~12 seconds/step
- **Evaluation:** Every 100 steps
- **No OOM crashes**

### Learning Curve
```
Epoch 0.03: Loss 1.20, Acc 72.6%
Epoch 0.34: Loss 1.03, Acc 75.4%
Epoch 1.00: Loss 0.89, Acc 78.0%
Epoch 2.00: Loss 0.85, Acc 78.2%
Epoch 3.00: Loss 0.84, Acc 78.4%
```

## Optimizations Applied

### Memory Efficiency
1. **4-bit Quantization** - Reduced model from 13GB to ~4GB
2. **Gradient Checkpointing** - Saved VRAM during backprop
3. **Paged Optimizer** - Offloaded optimizer states to RAM
4. **bf16 Precision** - Native on RTX 40-series

### Training Speed
1. **Batch Size 1** - Maximum memory efficiency
2. **Gradient Accumulation** - Simulated effective batch of 4
3. **No Packing** - Avoided sequence concatenation overhead

## Challenges & Solutions

### Challenge 1: TRL API Compatibility
**Problem:** `SFTTrainer` API changed between versions  
**Solution:** Migrated from `TrainingArguments` to `SFTConfig`

### Challenge 2: Model Cache Issues
**Problem:** Model files downloaded to wrong directory  
**Solution:** Manually copied to correct commit hash folder

### Challenge 3: VRAM Spikes During Eval
**Problem:** Evaluation caused temporary VRAM spikes  
**Solution:** Accepted risk (228MB headroom was sufficient)

## Model Artifacts

**Output Directory:** `models/exploitgpt-v1/`

**Files:**
- `adapter_config.json` - LoRA configuration
- `adapter_model.safetensors` - LoRA weights (33MB)
- `tokenizer_config.json` - Tokenizer settings
- Training logs & checkpoints

## Next Steps

1. **Test Generation** - Validate on known CVEs
2. **Merge Adapters** - Create standalone model
3. **Optimize Inference** - Reduce latency
4. **Build CLI** - Make it usable

## References

- [QLoRA Paper](https://arxiv.org/abs/2305.14314)
- [CodeLlama](https://huggingface.co/codellama/CodeLlama-7b-hf)
- [TRL Documentation](https://huggingface.co/docs/trl)
