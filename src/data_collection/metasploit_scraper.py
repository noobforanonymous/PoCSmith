#!/usr/bin/env python3
"""
Metasploit Scraper for ExploitGPT
Clones Metasploit Framework and extracts exploit modules
"""

import os
import re
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class MetasploitScraper:
    """Scraper for Metasploit Framework modules"""
    
    REPO_URL = "https://github.com/rapid7/metasploit-framework.git"
    
    def __init__(self, output_dir: str = "data/raw/exploits/metasploit"):
        self.output_dir = Path(output_dir)
        self.repo_dir = self.output_dir / "repo"
        self.data_dir = self.output_dir / "json"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            "total_processed": 0,
            "total_saved": 0,
            "errors": 0
        }

    def sync_repo(self):
        """Clone or pull the Metasploit repository"""
        if self.repo_dir.exists():
            print("[UPDATE] Updating Metasploit repository...")
            try:
                subprocess.run(["git", "-C", str(self.repo_dir), "pull"], check=True)
                print("[OK] Repository updated")
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Error updating repo: {e}")
        else:
            print("[CLONE] Cloning Metasploit repository...")
            try:
                subprocess.run(["git", "clone", "--depth", "1", self.REPO_URL, str(self.repo_dir)], check=True)
                print("[OK] Repository cloned")
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Error cloning repo: {e}")
                raise

    def parse_modules(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Parse exploit modules from the repository
        """
        exploits_dir = self.repo_dir / "modules" / "exploits"
        if not exploits_dir.exists():
            raise FileNotFoundError(f"Exploits directory not found in {self.repo_dir}")
            
        modules = []
        print("[PARSE] Parsing Metasploit modules...")
        
        # Walk through all ruby files in modules/exploits
        for file_path in exploits_dir.rglob("*.rb"):
            try:
                module_data = self._process_module(file_path)
                if module_data:
                    modules.append(module_data)
                    self.stats["total_processed"] += 1
                    
                    if limit and self.stats["total_processed"] >= limit:
                        break
            except Exception as e:
                self.stats["errors"] += 1
                
        print(f"[OK] Processed {len(modules)} modules")
        return modules

    def _process_module(self, file_path: Path) -> Optional[Dict]:
        """Process a single Ruby module file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Extract basic metadata using regex
            # Note: This is a simple parser. A full Ruby parser would be better but heavier.
            
            # Extract Name
            name_match = re.search(r"'Name'\s*=>\s*['\"](.+?)['\"]", content)
            name = name_match.group(1) if name_match else "Unknown"
            
            # Extract Description
            desc_match = re.search(r"'Description'\s*=>\s*%q\{(.+?)\}", content, re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else ""
            
            # Extract CVEs
            cve_matches = re.findall(r"'CVE',\s*'(\d{4}-\d+)'", content)
            
            # Extract Platform
            platform_match = re.search(r"'Platform'\s*=>\s*\['(.+?)'\]", content)
            platform = platform_match.group(1) if platform_match else "unknown"
            
            # Get relative path as ID
            rel_path = file_path.relative_to(self.repo_dir)
            
            return {
                "id": str(rel_path),
                "name": name,
                "description": description,
                "cve_ids": cve_matches,
                "platform": platform,
                "content": content,
                "source": "metasploit",
                "language": "ruby"
            }
            
        except Exception:
            return None

    def save_modules(self, modules: List[Dict], filename: Optional[str] = None):
        """Save modules to JSON file"""
        if not modules:
            print("[WARNING] No modules to save")
            return
            
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metasploit_{timestamp}.json"
            
        output_path = self.data_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(modules, f, indent=2, ensure_ascii=False)
                
            self.stats["total_saved"] = len(modules)
            print(f"[OK] Saved {len(modules)} modules to {output_path}")
            
        except Exception as e:
            print(f"[ERROR] Error saving modules: {e}")
            self.stats["errors"] += 1

    def print_stats(self):
        """Print statistics"""
        print("\n" + "="*60)
        print("[STATS] Metasploit Scraper Statistics")
        print("="*60)
        print(f"Total processed: {self.stats['total_processed']}")
        print(f"Total saved:     {self.stats['total_saved']}")
        print(f"Errors:          {self.stats['errors']}")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description="Scrape Metasploit modules")
    parser.add_argument("--limit", type=int, help="Limit number of modules")
    parser.add_argument("--output", help="Output filename")
    parser.add_argument("--output-dir", default="data/raw/exploits/metasploit", help="Output directory")
    parser.add_argument("--skip-sync", action="store_true", help="Skip repo sync")
    
    args = parser.parse_args()
    
    print("="*60)
    print("Ⓜ️ ExploitGPT Metasploit Scraper")
    print("="*60)
    
    scraper = MetasploitScraper(output_dir=args.output_dir)
    
    if not args.skip_sync:
        scraper.sync_repo()
        
    modules = scraper.parse_modules(limit=args.limit)
    
    if modules:
        scraper.save_modules(modules, filename=args.output)
        
    scraper.print_stats()

if __name__ == "__main__":
    main()
