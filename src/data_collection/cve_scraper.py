#!/usr/bin/env python3
"""
CVE Scraper for ExploitGPT
Fetches CVE data from the National Vulnerability Database (NVD) API
"""

import requests
import json
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse


class CVEScraper:
    """Scraper for CVE data from NVD API"""
    
    BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    RATE_LIMIT_DELAY = 6  # seconds between requests (NVD allows 5 per 30s)
    
    def __init__(self, output_dir: str = "data/raw/cves"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.stats = {
            "total_fetched": 0,
            "total_saved": 0,
            "errors": 0
        }
    
    def fetch_cves(
        self,
        year: Optional[int] = None,
        severity: Optional[str] = None,
        results_per_page: int = 100,
        max_results: Optional[int] = None
    ) -> List[Dict]:
        """
        Fetch CVEs from NVD API
        
        Args:
            year: Filter by year (e.g., 2024)
            severity: Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)
            results_per_page: Number of results per API call (max 2000)
            max_results: Maximum total results to fetch
        
        Returns:
            List of CVE dictionaries
        """
        cves = []
        
        print(f"[PARSE] Fetching CVEs from NVD API...")
        if year:
            print(f"   Year: {year}")
        if severity:
            print(f"   Severity: {severity}")
            
        # NVD API limits date ranges to 120 days.
        # If a year is specified, we need to split it into chunks.
        date_ranges = []
        if year:
            # Split year into 4 chunks (Jan-Mar, Apr-Jun, Jul-Sep, Oct-Dec)
            # This ensures we stay well within the 120-day limit
            date_ranges = [
                (f"{year}-01-01T00:00:00", f"{year}-03-31T23:59:59"),
                (f"{year}-04-01T00:00:00", f"{year}-06-30T23:59:59"),
                (f"{year}-07-01T00:00:00", f"{year}-09-30T23:59:59"),
                (f"{year}-10-01T00:00:00", f"{year}-12-31T23:59:59"),
            ]
        else:
            # If no year, just use one pass (will fetch all if no other filters, or just severity)
            # Note: NVD might require date range for large datasets, but let's try without if not specified
            date_ranges = [(None, None)]
            
        for start_date, end_date in date_ranges:
            if max_results and self.stats["total_fetched"] >= max_results:
                break
                
            start_index = 0
            while True:
                # Build API parameters
                params = {
                    "resultsPerPage": results_per_page,
                    "startIndex": start_index
                }
                
                # Add filters
                if start_date and end_date:
                    params["pubStartDate"] = start_date
                    params["pubEndDate"] = end_date
                    print(f"   [FETCH] Fetching range: {start_date[:10]} to {end_date[:10]}")
                
                if severity:
                    params["cvssV3Severity"] = severity
                
                try:
                    # Make API request
                    print(f"   Fetching results {start_index} to {start_index + results_per_page}...")
                    response = self.session.get(self.BASE_URL, params=params, timeout=30)
                    
                    # Handle rate limiting specifically
                    if response.status_code == 403:
                        print("   [WARNING]  Rate limited (403). Waiting 10s...")
                        time.sleep(10)
                        continue
                        
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # Extract CVEs
                    vulnerabilities = data.get("vulnerabilities", [])
                    if not vulnerabilities:
                        print("   No more results in this range")
                        break
                    
                    # Process each CVE
                    for vuln in vulnerabilities:
                        cve_data = self._process_cve(vuln)
                        if cve_data:
                            cves.append(cve_data)
                            self.stats["total_fetched"] += 1
                            
                        if max_results and self.stats["total_fetched"] >= max_results:
                            break
                    
                    print(f"   [OK] Fetched {len(vulnerabilities)} CVEs (total: {self.stats['total_fetched']})")
                    
                    # Check if we've reached max results
                    if max_results and self.stats["total_fetched"] >= max_results:
                        print(f"   Reached max results limit ({max_results})")
                        break
                    
                    # Check if there are more results
                    total_results = data.get("totalResults", 0)
                    if start_index + results_per_page >= total_results:
                        print(f"   Fetched all {total_results} results in this range")
                        break
                    
                    # Move to next page
                    start_index += results_per_page
                    
                    # Rate limiting
                    print(f"   ⏳ Waiting {self.RATE_LIMIT_DELAY}s (rate limit)...")
                    time.sleep(self.RATE_LIMIT_DELAY)
                    
                except requests.exceptions.RequestException as e:
                    self.stats["errors"] += 1
                    break
        
        return cves
    
    def _process_cve(self, vuln: Dict) -> Optional[Dict]:
        """
        Process and extract relevant data from a CVE
        
        Args:
            vuln: Raw vulnerability data from NVD
        
        Returns:
            Processed CVE dictionary or None if invalid
        """
        try:
            cve = vuln.get("cve", {})
            cve_id = cve.get("id", "UNKNOWN")
            
            # Extract description
            descriptions = cve.get("descriptions", [])
            description = ""
            for desc in descriptions:
                if desc.get("lang") == "en":
                    description = desc.get("value", "")
                    break
            
            # Extract CVSS scores
            metrics = cve.get("metrics", {})
            cvss_v3 = metrics.get("cvssMetricV31", [])
            cvss_score = None
            severity = None
            
            if cvss_v3:
                cvss_data = cvss_v3[0].get("cvssData", {})
                cvss_score = cvss_data.get("baseScore")
                severity = cvss_data.get("baseSeverity")
            
            # Extract CWE (weakness type)
            weaknesses = cve.get("weaknesses", [])
            cwe_ids = []
            for weakness in weaknesses:
                for desc in weakness.get("description", []):
                    cwe_id = desc.get("value", "")
                    if cwe_id.startswith("CWE-"):
                        cwe_ids.append(cwe_id)
            
            # Extract references
            references = []
            for ref in cve.get("references", []):
                references.append({
                    "url": ref.get("url", ""),
                    "source": ref.get("source", "")
                })
            
            # Build processed CVE
            processed = {
                "cve_id": cve_id,
                "description": description,
                "published_date": cve.get("published", ""),
                "last_modified": cve.get("lastModified", ""),
                "cvss_score": cvss_score,
                "severity": severity,
                "cwe_ids": cwe_ids,
                "references": references,
                "raw_data": cve  # Keep raw data for reference
            }
            
            return processed
            
        except Exception as e:
            print(f"   [WARNING]  Error processing CVE: {e}")
            return None
    
    def save_cves(self, cves: List[Dict], filename: Optional[str] = None):
        """
        Save CVEs to JSON file
        
        Args:
            cves: List of CVE dictionaries
            filename: Output filename (auto-generated if None)
        """
        if not cves:
            print("[WARNING]  No CVEs to save")
            return
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cves_{timestamp}.json"
        
        output_path = self.output_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(cves, f, indent=2, ensure_ascii=False)
            
            self.stats["total_saved"] = len(cves)
            print(f"[OK] Saved {len(cves)} CVEs to {output_path}")
            
        except Exception as e:
            print(f"[ERROR] Error saving CVEs: {e}")
            self.stats["errors"] += 1
    
    def print_stats(self):
        """Print scraping statistics"""
        print("\n" + "="*60)
        print("[STATS] Scraping Statistics")
        print("="*60)
        print(f"Total CVEs fetched: {self.stats['total_fetched']}")
        print(f"Total CVEs saved:   {self.stats['total_saved']}")
        print(f"Errors:             {self.stats['errors']}")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Scrape CVE data from NVD API")
    parser.add_argument("--year", type=int, help="Filter by year (e.g., 2024)")
    parser.add_argument("--severity", choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"], 
                       help="Filter by severity")
    parser.add_argument("--max-results", type=int, help="Maximum results to fetch")
    parser.add_argument("--output", help="Output filename")
    parser.add_argument("--output-dir", default="data/raw/cves", 
                       help="Output directory")
    
    args = parser.parse_args()
    
    print("="*60)
    print("[CVE] ExploitGPT CVE Scraper")
    print("="*60)
    
    # Create scraper
    scraper = CVEScraper(output_dir=args.output_dir)
    
    # Fetch CVEs
    cves = scraper.fetch_cves(
        year=args.year,
        severity=args.severity,
        max_results=args.max_results
    )
    
    # Save results
    if cves:
        scraper.save_cves(cves, filename=args.output)
    
    # Print statistics
    scraper.print_stats()


if __name__ == "__main__":
    main()
