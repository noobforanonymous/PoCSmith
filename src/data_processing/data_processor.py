#!/usr/bin/env python3
"""
Data Processor for ExploitGPT
Cleans, links, and formats data for LLM fine-tuning
"""

import json
import re
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse

class DataProcessor:
    """Process and format data for ExploitGPT training"""
    
    def __init__(self, output_dir: str = "data/processed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            "cves_loaded": 0,
            "exploits_loaded": 0,
            "linked_pairs": 0,
            "shellcodes_loaded": 0
        }

    def load_data(self, cve_file: str, exploit_file: str, shellcode_file: Optional[str] = None, metasploit_file: Optional[str] = None):
        """Load raw data files"""
        print("[LOAD] Loading data...")
        
        with open(cve_file, 'r') as f:
            self.cves = json.load(f)
            self.stats["cves_loaded"] = len(self.cves)
            
        with open(exploit_file, 'r') as f:
            self.exploits = json.load(f)
            self.stats["exploits_loaded"] = len(self.exploits)
            
        if shellcode_file:
            with open(shellcode_file, 'r') as f:
                self.shellcodes = json.load(f)
                self.stats["shellcodes_loaded"] = len(self.shellcodes)
        else:
            self.shellcodes = []
            
        if metasploit_file:
            with open(metasploit_file, 'r') as f:
                self.metasploit_modules = json.load(f)
                self.stats["metasploit_loaded"] = len(self.metasploit_modules)
        else:
            self.metasploit_modules = []
            
        print(f"[OK] Loaded {len(self.cves)} CVEs, {len(self.exploits)} exploits, {len(self.metasploit_modules)} MSF modules")

    def link_data(self) -> List[Dict]:
        """Link CVEs to Exploits based on CVE ID"""
        print("[LINK] Linking CVEs to Exploits...")
        
        # Create CVE lookup map
        cve_map = {cve['cve_id']: cve for cve in self.cves}
        
        linked_data = []
        
        # Process Exploit-DB
        for exploit in self.exploits:
            codes = exploit.get('codes', '')
            if not codes:
                continue
                
            cve_ids = re.findall(r'CVE-\d{4}-\d+', codes)
            for cve_id in cve_ids:
                if cve_id in cve_map:
                    cve_data = cve_map[cve_id]
                    linked_data.append({
                        "cve_id": cve_id,
                        "cve_description": cve_data['description'],
                        "cvss_score": cve_data['cvss_score'],
                        "exploit_id": exploit['id'],
                        "exploit_type": exploit['type'],
                        "platform": exploit['platform'],
                        "exploit_code": exploit['content'],
                        "source": "exploit-db"
                    })
                    
        # Process Metasploit
        for module in self.metasploit_modules:
            cve_ids = module.get('cve_ids', [])
            for cve_id in cve_ids:
                if cve_id in cve_map:
                    cve_data = cve_map[cve_id]
                    linked_data.append({
                        "cve_id": cve_id,
                        "cve_description": cve_data['description'],
                        "cvss_score": cve_data['cvss_score'],
                        "exploit_id": module['id'],
                        "exploit_type": "metasploit_module",
                        "platform": module['platform'],
                        "exploit_code": module['content'],
                        "source": "metasploit"
                    })
        
        self.stats["linked_pairs"] = len(linked_data)
        print(f"[OK] Found {len(linked_data)} linked CVE-Exploit pairs")
        return linked_data

    def format_for_training(self, linked_data: List[Dict]) -> List[Dict]:
        """Format data into instruction-input-output pairs"""
        formatted_data = []
        
        # Format CVE -> PoC pairs
        for item in linked_data:
            instruction = (
                f"Generate a Proof-of-Concept (PoC) exploit for {item['cve_id']} "
                f"affecting {item['platform']}."
            )
            
            input_text = (
                f"Vulnerability Description: {item['cve_description']}\n"
                f"CVSS Score: {item['cvss_score']}\n"
                f"Exploit Type: {item['exploit_type']}"
            )
            
            output_text = item['exploit_code']
            
            formatted_data.append({
                "instruction": instruction,
                "input": input_text,
                "output": output_text,
                "source": "cve-exploit"
            })
            
        # Format Shellcodes
        for sc in self.shellcodes:
            instruction = f"Generate shellcode for {sc['platform']} {sc['type']}."
            input_text = f"Description: {sc['description']}"
            output_text = sc['content']
            
            formatted_data.append({
                "instruction": instruction,
                "input": input_text,
                "output": output_text,
                "source": "shellcode"
            })
            
        return formatted_data

    def split_and_save(self, data: List[Dict], train_ratio: float = 0.8, val_ratio: float = 0.1):
        """Split dataset and save to JSONL"""
        random.shuffle(data)
        
        n = len(data)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))
        
        train_data = data[:train_end]
        val_data = data[train_end:val_end]
        test_data = data[val_end:]
        
        self._save_jsonl(train_data, "train.jsonl")
        self._save_jsonl(val_data, "validation.jsonl")
        self._save_jsonl(test_data, "test.jsonl")
        
        print(f"[STATS] Split: Train={len(train_data)}, Val={len(val_data)}, Test={len(test_data)}")

    def _save_jsonl(self, data: List[Dict], filename: str):
        """Save list of dicts to JSONL"""
        path = self.output_dir / filename
        with open(path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"[SAVE] Saved {path}")

def main():
    parser = argparse.ArgumentParser(description="Process data for ExploitGPT")
    parser.add_argument("--cves", required=True, help="Path to CVE JSON file")
    parser.add_argument("--exploits", required=True, help="Path to Exploit JSON file")
    parser.add_argument("--shellcodes", help="Path to Shellcode JSON file")
    parser.add_argument("--metasploit", help="Path to Metasploit JSON file")
    parser.add_argument("--output-dir", default="data/processed", help="Output directory")
    
    args = parser.parse_args()
    
    processor = DataProcessor(output_dir=args.output_dir)
    processor.load_data(args.cves, args.exploits, args.shellcodes, args.metasploit)
    
    linked_data = processor.link_data()
    formatted_data = processor.format_for_training(linked_data)
    
    processor.split_and_save(formatted_data)

if __name__ == "__main__":
    main()
