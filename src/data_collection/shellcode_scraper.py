#!/usr/bin/env python3
"""
Shellcode Scraper for ExploitGPT
Extracts shellcode samples from Exploit-DB repository
"""

import os
import csv
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class ShellcodeScraper:
    """Scraper for shellcode data from Exploit-DB"""
    
    def __init__(self, repo_dir: str = "data/raw/exploits/exploitdb/repo", 
                 output_dir: str = "data/raw/shellcode"):
        self.repo_dir = Path(repo_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            "total_processed": 0,
            "total_saved": 0,
            "errors": 0
        }

    def parse_shellcodes(self, limit: Optional[int] = None, platform: Optional[str] = None) -> List[Dict]:
        """
        Parse shellcodes from the repository
        
        Args:
            limit: Maximum number of shellcodes to process
            platform: Filter by platform/architecture (e.g., 'linux_x86')
            
        Returns:
            List of shellcode dictionaries
        """
        csv_path = self.repo_dir / "files_shellcodes.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"files_shellcodes.csv not found in {self.repo_dir}")
            
        shellcodes = []
        
        print("[PARSE] Parsing shellcodes...")
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Apply filters
                    if platform and platform.lower() not in row.get('platform', '').lower():
                        continue
                        
                    try:
                        shellcode_data = self._process_shellcode(row)
                        if shellcode_data:
                            shellcodes.append(shellcode_data)
                            self.stats["total_processed"] += 1
                            
                            if limit and self.stats["total_processed"] >= limit:
                                break
                                
                    except Exception as e:
                        self.stats["errors"] += 1
                        
        except Exception as e:
            print(f"[ERROR] Error reading CSV: {e}")
            raise
            
        print(f"[OK] Processed {len(shellcodes)} shellcodes")
        return shellcodes

    def _process_shellcode(self, row: Dict) -> Optional[Dict]:
        """Process a single shellcode row"""
        shellcode_id = row.get('id')
        file_path = row.get('file')
        description = row.get('description')
        date = row.get('date')
        author = row.get('author')
        platform = row.get('platform')
        type_ = row.get('type')
        
        full_path = self.repo_dir / file_path
        
        if not full_path.exists():
            return None
            
        # Read content
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(full_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception:
                return None
                
        return {
            "id": shellcode_id,
            "description": description,
            "date": date,
            "author": author,
            "platform": platform,
            "type": type_,
            "content": content,
            "source": "exploit-db"
        }

    def save_shellcodes(self, shellcodes: List[Dict], filename: Optional[str] = None):
        """Save shellcodes to JSON file"""
        if not shellcodes:
            print("[WARNING] No shellcodes to save")
            return
            
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"shellcodes_{timestamp}.json"
            
        output_path = self.output_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(shellcodes, f, indent=2, ensure_ascii=False)
                
            self.stats["total_saved"] = len(shellcodes)
            print(f"[OK] Saved {len(shellcodes)} shellcodes to {output_path}")
            
        except Exception as e:
            print(f"[ERROR] Error saving shellcodes: {e}")
            self.stats["errors"] += 1

    def print_stats(self):
        """Print statistics"""
        print("\n" + "="*60)
        print("[STATS] Shellcode Scraper Statistics")
        print("="*60)
        print(f"Total processed: {self.stats['total_processed']}")
        print(f"Total saved:     {self.stats['total_saved']}")
        print(f"Errors:          {self.stats['errors']}")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description="Scrape shellcode data")
    parser.add_argument("--limit", type=int, help="Limit number of shellcodes")
    parser.add_argument("--platform", help="Filter by platform (e.g., linux_x86)")
    parser.add_argument("--output", help="Output filename")
    parser.add_argument("--repo-dir", default="data/raw/exploits/exploitdb/repo", help="Path to Exploit-DB repo")
    parser.add_argument("--output-dir", default="data/raw/shellcode", help="Output directory")
    
    args = parser.parse_args()
    
    print("="*60)
    print("[SHELLCODE] ExploitGPT Shellcode Scraper")
    print("="*60)
    
    scraper = ShellcodeScraper(repo_dir=args.repo_dir, output_dir=args.output_dir)
    
    shellcodes = scraper.parse_shellcodes(limit=args.limit, platform=args.platform)
    
    if shellcodes:
        scraper.save_shellcodes(shellcodes, filename=args.output)
        
    scraper.print_stats()

if __name__ == "__main__":
    main()
