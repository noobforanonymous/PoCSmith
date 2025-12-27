# PoCSmith - Setup Guide

## System Requirements

- **OS:** Linux (tested on Arch Linux), macOS, Windows
- **Python:** 3.11 or higher
- **GPU:** NVIDIA GPU with 6GB+ VRAM (RTX 4050 or better)
- **CUDA:** 12.0+
- **Disk:** 20GB free space
- **RAM:** 16GB recommended

---

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/noobforanonymous/PoCSmith.git
cd PoCSmith
```

### 2. Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install PoCSmith
pip install -e .
```

**Dependencies installed:**
- torch>=2.0.0
- transformers>=4.35.0
- peft>=0.7.0
- bitsandbytes>=0.41.0
- click>=8.1.0
- requests>=2.31.0
- rich>=13.0.0

---

## Model Setup

The fine-tuned model should be in `models/pocsmith-v1/`.

**Files needed:**
```
models/pocsmith-v1/
├── adapter_config.json
├── adapter_model.safetensors
├── tokenizer_config.json
└── tokenizer.json
```

**If model is missing:**

The base CodeLlama-7B model will be downloaded automatically on first use (approximately 13GB).

---

## Verify Installation

### 1. Check Python Version

```bash
python --version
# Should be 3.11 or higher
```

### 2. Check CUDA

```bash
python -c "import torch; print(torch.cuda.is_available())"
# Should print: True
```

### 3. Test CLI

```bash
python src/cli/main.py --help
```

You should see:
```
PoCSmith v1.0

Usage: main.py [OPTIONS] COMMAND [ARGS]...

  PoCSmith - AI-Powered Security Research Tool

Commands:
  cve             Generate PoC exploit from CVE ID
  disclaimer      Show ethical use disclaimer
  generate        Generate PoC from vulnerability description
  list-payloads   List supported payload types
  list-platforms  List supported platforms for shellcode
  shellcode       Generate shellcode for specified platform
```

---

## Configuration

Edit `src/core/config.py` to customize:

```python
# Model paths
MODEL_PATH = "models/pocsmith-v1"

# Generation settings
DEFAULT_MAX_TOKENS = 512
DEFAULT_TEMPERATURE = 0.7

# Output
OUTPUT_DIR = "output/"
```

---

## First Run

### Generate Your First Exploit

```bash
# Test with shellcode generation (fast)
python src/cli/main.py shellcode \
  --platform linux_x64 \
  --type reverse_shell \
  --lhost 10.10.14.5 \
  --lport 4444
```

**Expected output:**
```
PoCSmith v1.0

[*] Generating reverse_shell for linux_x64...
Loading PoCSmith model...
Model ready!

============================================================
<generated shellcode>
============================================================
```

**First run will take approximately 30-60 seconds** (model loading + generation)

---

## Troubleshooting

### Issue: "No module named 'torch'"

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### Issue: "CUDA out of memory"

**Solution 1:** Close other GPU applications
```bash
nvidia-smi  # Check GPU usage
```

**Solution 2:** Use CPU mode (slower)
```python
# In src/core/config.py
USE_4BIT = False
```

### Issue: "Model not found"

Check model directory exists:
```bash
ls -la models/pocsmith-v1/
```

If missing, restore from backup:
```bash
tar -xzf backups/pocsmith-v1_*.tar.gz
```

### Issue: Import errors

Ensure you are in the virtual environment:
```bash
which python  # Should show path with 'venv'
```

---

## Development Setup

For development work:

```bash
# Install dev dependencies
pip install pytest black ruff

# Run tests
pytest tests/

# Format code
black src/

# Lint
ruff check src/
```

---

## Uninstallation

```bash
# Deactivate venv
deactivate

# Remove directory
cd ..
rm -rf PoCSmith
```

---

## Next Steps

1. Read [Usage Guide](USAGE.md)
2. Review [Ethical Guidelines](guidelines/ETHICAL_GUIDELINES.md)
3. Try generating exploits
4. Report bugs/contribute

---

PoCSmith is ready to use.
