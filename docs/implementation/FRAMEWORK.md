# PoCSmith - Framework Architecture


## Architecture Diagram

```
+-------------------------------------------+
|          CLI Interface                     |
|         (src/cli/main.py)                 |
+------------------+------------------------+
                   |
       +-----------+-----------+
       |           |           |
       v           v           v
+------------+ +------------+ +------------+
| CVE Parser | |PoC Generator| | Shellcode  |
|            | |             | | Generator  |
+-----+------+ +------+------+ +------+-----+
      |               |               |
      |               v               |
      |        +------------+         |
      |        | AI Model   |         |
      |        |(CodeLlama) +<--------+
      |        +------+-----+
      |               |
      v               v
+--------------------------------+
|      Output Formatter          |
+--------------------------------+
              |
              v
       +------------+
       |File/Console|
       +------------+
```

---

## Component Details

### 1. CVE Parser (src/parsers/cve_parser.py)

**Purpose:** Fetch and parse CVE data from NVD API

**Key Features:**
- NVD API v2.0 integration
- Local JSON caching
- Rate limiting (5 req/30s)
- CVSS score extraction
- Affected software parsing

**Data Flow:**
```
User CVE ID -> NVD API -> Parse JSON -> Cache -> Format for AI
```

**Class:**
```python
class CVEParser:
    fetch_cve(cve_id) -> CVEData
    _parse_cve_data(raw_json) -> CVEData
    format_for_model(cve_data) -> str
```

---

### 2. PoC Generator (src/generators/poc_generator.py)

**Purpose:** AI-powered exploit generation

**Key Features:**
- Lazy model loading
- 4-bit quantization
- Template-based prompts
- Multiple input formats

**Templates:**
- CVE-based generation
- Description-based generation
- Custom instruction format

**Class:**
```python
class PoCGenerator:
    load_model()
    generate(instruction, context) -> str
    generate_from_cve(...) -> str
    generate_from_description(...) -> str
```

---

### 3. Shellcode Generator (src/generators/shellcode_generator.py)

**Purpose:** Multi-platform payload generation

**Supported:**
- **Platforms:** linux_x86, linux_x64, windows_x86, windows_x64, arm
- **Payloads:** reverse_shell, bind_shell, exec, download_exec

**Class:**
```python
class ShellcodeGenerator:
    generate(platform, payload_type, ...) -> str
    list_platforms() -> dict
    list_payload_types() -> dict
```

---

### 4. Output Formatter (src/formatters/output_formatter.py)

**Purpose:** Clean and format generated code

**Features:**
- Remove markdown artifacts
- Add headers/disclaimers
- File writing with permissions
- Syntax detection

**Class:**
```python
class OutputFormatter:
    clean(raw_output) -> str
    add_header(code, title) -> str
    to_file(code, filename) -> Path
```

---

### 5. CLI Interface (src/cli/main.py)

**Purpose:** User-friendly command-line tool

**Commands:**
```
cve <CVE-ID>              - Generate from CVE
generate --vuln TYPE      - Generate from description
shellcode --platform X    - Generate shellcode
list-platforms            - List platforms
list-payloads             - List payloads
disclaimer                - Show warning
```

**Framework:** Click (Python CLI framework)

---

## Configuration (src/core/config.py)

**Centralized settings:**
- Model paths
- API endpoints
- Generation parameters
- Output directories
- Ethical warnings

---

## Data Flow

### CVE Exploit Generation
```
1. User: pocsmith cve CVE-2024-1234
2. CLI parses arguments
3. CVEParser fetches from NVD
4. CVEParser formats data
5. PoCGenerator loads AI model
6. PoCGenerator generates exploit
7. OutputFormatter cleans output
8. Display or save to file
```

### Shellcode Generation
```
1. User: pocsmith shellcode --platform linux_x64
2. CLI validates arguments
3. ShellcodeGenerator creates prompt
4. PoCGenerator (wrapped) generates
5. OutputFormatter cleans
6. Display or save
```

---

## File Structure

```
src/
├── cli/
│   ├── __init__.py
│   └── main.py              # CLI entry point
├── parsers/
│   ├── __init__.py
│   └── cve_parser.py        # NVD integration
├── generators/
│   ├── __init__.py
│   ├── poc_generator.py     # AI wrapper
│   └── shellcode_generator.py
├── formatters/
│   ├── __init__.py
│   └── output_formatter.py
└── core/
    ├── __init__.py
    └── config.py            # Configuration
```

---

## Dependencies

**Core:**
- `torch` - Deep learning
- `transformers` - Model loading
- `peft` - LoRA adapters
- `bitsandbytes` - Quantization

**Utilities:**
- `click` - CLI framework
- `requests` - HTTP for NVD API
- `rich` - Console output

---

## Design Decisions

### Why Absolute Imports?
- More reliable for CLI tools
- Avoids relative import issues
- Works when run as script

### Why Lazy Loading?
- Model takes 15s to load
- Only load when actually generating
- Better for help/list commands

### Why Centralized Config?
- Single source of truth
- Easy to modify settings
- Clear separation of concerns

### Why Click for CLI?
- Clean command structure
- Automatic help generation
- Type validation built-in

---

**Total LOC:** Approximately 800 lines  
**Components:** 5 modules  
**Commands:** 6 CLI commands  
**Platforms:** 5 supported  

Built for PoCSmith v1.0
