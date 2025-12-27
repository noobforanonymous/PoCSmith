# PoCSmith - System Architecture

## ARCHITECTURE: High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        PoCSmith                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   CLI/Web    │───▶│  Core Engine │───▶│  AI Model    │  │
│  │  Interface   │    │              │    │  (LLM)       │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Input      │    │  Exploit     │    │  Knowledge   │  │
│  │  Processor   │    │  Generator   │    │  Base (RAG)  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  CVE Parser  │    │  Shellcode   │    │   Binary     │  │
│  │              │    │  Generator   │    │   Analyzer   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

##  Component Breakdown

### 1. User Interface Layer
**Purpose:** Accept user input and display results

**Components:**
- **CLI Interface:** Primary interface for terminal usage
- **Web UI (Optional):** Browser-based interface for easier use
- **API Server:** RESTful API for programmatic access

**Tech Stack:**
- CLI: Python `click` or `argparse`
- Web: Flask/FastAPI
- API: FastAPI with OpenAPI docs

---

### 2. Core Engine
**Purpose:** Orchestrate all components and manage workflow

**Responsibilities:**
- Route requests to appropriate modules
- Manage AI model interactions
- Handle caching and optimization
- Error handling and logging

**Tech Stack:**
- Python 3.11+
- Async/await for performance
- Redis for caching (optional)

---

### 3. AI Model Layer
**Purpose:** Generate exploits using fine-tuned LLM

**Components:**
- **Base Model:** Llama 3 or CodeLlama
- **Fine-tuned Model:** Trained on exploit data
- **Inference Engine:** Optimized for speed
- **Prompt Templates:** Structured prompts for different tasks

**Tech Stack:**
- `transformers` library
- `llama-cpp-python` for local inference
- CUDA for GPU acceleration
- LoRA/QLoRA for efficient fine-tuning

---

### 4. Knowledge Base (RAG)
**Purpose:** Provide context from exploit databases

**Components:**
- **Vector Database:** Store exploit embeddings
- **Retrieval System:** Find relevant exploits
- **Context Builder:** Prepare context for LLM

**Data Sources:**
- Exploit-DB
- CVE database
- Metasploit modules
- Public PoCs from GitHub

**Tech Stack:**
- ChromaDB or FAISS for vector storage
- Sentence transformers for embeddings
- SQLite for metadata

---

### 5. Input Processors

#### CVE Parser
**Purpose:** Extract information from CVE descriptions

**Features:**
- Parse CVE JSON/XML
- Extract vulnerability type
- Identify affected software/versions
- Determine severity

#### Binary Analyzer
**Purpose:** Analyze binaries for vulnerabilities

**Features:**
- Disassembly (Ghidra/radare2)
- Vulnerability pattern matching
- Exploit suggestion based on findings

**Tech Stack:**
- Ghidra headless analyzer
- radare2 Python bindings
- Binary Ninja API (optional)

---

### 6. Exploit Generators

#### PoC Generator
**Purpose:** Create proof-of-concept exploits

**Features:**
- Template-based generation
- AI-powered code generation
- Multi-language support (Python, C, shellcode)

#### Shellcode Generator
**Purpose:** Generate shellcode for various architectures

**Features:**
- x86/x64 shellcode
- ARM shellcode
- Encoder/obfuscation
- Null-byte avoidance

**Tech Stack:**
- `pwntools` for shellcode
- Custom templates
- AI generation for complex payloads

---

##  Data Flow

### Scenario 1: CVE → PoC Generation
```
User Input (CVE-2024-XXXX)
    ↓
CVE Parser (extract details)
    ↓
Knowledge Base (retrieve similar exploits)
    ↓
AI Model (generate PoC with context)
    ↓
PoC Generator (format and validate)
    ↓
Output (working exploit code)
```

### Scenario 2: Binary Analysis
```
User Input (binary file)
    ↓
Binary Analyzer (disassemble + analyze)
    ↓
Vulnerability Detector (find weaknesses)
    ↓
AI Model (suggest exploit approach)
    ↓
Exploit Generator (create PoC)
    ↓
Output (exploit + explanation)
```

---

##  Data Storage

### Training Data
- **Location:** `data/training/`
- **Format:** JSONL
- **Size:** ~50GB (compressed)
- **Contents:** CVEs, exploits, shellcode examples

### Models
- **Location:** `models/`
- **Base Model:** ~7GB (quantized)
- **Fine-tuned Model:** ~8GB
- **Embeddings:** ~2GB

### Cache
- **Location:** `cache/` or Redis
- **Purpose:** Store frequently used results
- **TTL:** 24 hours

---

## SECURITY: Security Considerations

### Ethical Safeguards
- Require explicit confirmation for exploit generation
- Add warnings about legal implications
- Log all usage (locally only)
- Implement rate limiting

### Privacy
- All processing happens locally
- No data sent to external servers
- Optional telemetry (disabled by default)

---

##  Performance Targets

- **CVE → PoC:** < 30 seconds
- **Binary Analysis:** < 2 minutes
- **Shellcode Generation:** < 10 seconds
- **Memory Usage:** < 16GB RAM
- **GPU Usage:** < 8GB VRAM

---

##  Scalability

### Phase 1 (MVP)
- Single-user, local deployment
- CPU/GPU inference
- SQLite database

### Phase 2 (Enhanced)
- Multi-user support
- API server
- PostgreSQL database
- Redis caching

### Phase 3 (Production)
- Distributed inference
- Load balancing
- Cloud deployment option
