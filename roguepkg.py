#!/usr/bin/env python3
"""
Detect vulnerabilities and malware in npm packages using OSV.dev API.

OSV (Open Source Vulnerabilities) is a free, open-source vulnerability database
that aggregates data from multiple sources including GitHub, npm, and others.

Features:
- No API key required (completely free)
- Comprehensive vulnerability data
- Malware detection
- Multiple ecosystem support
- Detailed version ranges and affected versions

Usage:
    python roguepkg.py lodash@4.17.15
    python roguepkg.py lodash
    python roguepkg.py --file package.json --batch
    python roguepkg.py --file package.json --batch --malware-only
    python roguepkg.py --file package.json --json
"""

import json
import requests
import sys
import re
from pathlib import Path
import argparse
from datetime import datetime


class OSVScanner:
    def __init__(self):
        self.base_url = "https://api.osv.dev/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "npm-vulnerability-scanner/1.0"
        })
        self.vuln_cache = {}  # Cache for vulnerability details
    
    def query_package(self, package_name, version=None):
        """Query OSV.dev for vulnerabilities in a package"""
        endpoint = f"{self.base_url}/query"
        
        # Build query payload
        payload = {
            "package": {
                "name": package_name,
                "ecosystem": "npm"
            }
        }
        
        # Add version if specified
        if version:
            payload["version"] = version
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[!] API error ({response.status_code}): {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"[!] Request failed: {e}")
            return None
    
    def get_vulnerability_details(self, vuln_id):
        """Fetch full details for a vulnerability by ID"""
        # Check cache first
        if vuln_id in self.vuln_cache:
            return self.vuln_cache[vuln_id]
        
        endpoint = f"{self.base_url}/vulns/{vuln_id}"
        
        try:
            response = self.session.get(endpoint, timeout=10)
            
            if response.status_code == 200:
                details = response.json()
                self.vuln_cache[vuln_id] = details
                return details
            else:
                return None
                
        except requests.exceptions.RequestException:
            return None
    
    def batch_query(self, packages):
        """Query multiple packages in batch"""
        endpoint = f"{self.base_url}/querybatch"
        
        # Build batch query
        queries = []
        for pkg_name, pkg_version in packages.items():
            query = {
                "package": {
                    "name": pkg_name,
                    "ecosystem": "npm"
                }
            }
            if pkg_version:
                # Clean version
                clean_version = re.sub(r'^[\^~>=<]+', '', pkg_version)
                query["version"] = clean_version
            
            queries.append(query)
        
        payload = {"queries": queries}
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                # Batch query returns minimal data - fetch full details for each vuln
                if result.get('results'):
                    for query_result in result['results']:
                        if query_result.get('vulns'):
                            enriched_vulns = []
                            for vuln in query_result['vulns']:
                                vuln_id = vuln.get('id')
                                if vuln_id:
                                    # Fetch full details
                                    full_details = self.get_vulnerability_details(vuln_id)
                                    if full_details:
                                        enriched_vulns.append(full_details)
                                    else:
                                        enriched_vulns.append(vuln)
                                else:
                                    enriched_vulns.append(vuln)
                            query_result['vulns'] = enriched_vulns
                
                return result
            else:
                print(f"[!] Batch query failed ({response.status_code}): {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"[!] Batch request failed: {e}")
            return None
    
    def format_vulnerability(self, vuln):
        """Format a single vulnerability for display"""
        vuln_id = vuln.get("id", "UNKNOWN")
        summary = vuln.get("summary", "")
        
        # Try to extract summary from details if not available
        if not summary and vuln.get("details"):
            details_text = vuln.get("details", "")
            # Extract first meaningful line from details
            lines = [line.strip() for line in details_text.split('\n') if line.strip() and not line.startswith('---')]
            if lines:
                summary = lines[0][:200]  # First 200 chars
        
        if not summary:
            summary = "No summary available"
        
        details = vuln.get("details", "")
        
        # Get severity
        severity = "UNKNOWN"
        
        # Check severity field at root level first
        sev_field = vuln.get("severity")
        if sev_field:
            # Severity can be a string or list
            if isinstance(sev_field, list):
                severity = sev_field[0].get("score", "UNKNOWN") if sev_field else "UNKNOWN"
            elif isinstance(sev_field, str):
                severity = sev_field.upper()
        elif "database_specific" in vuln:
            db_specific = vuln["database_specific"]
            if "severity" in db_specific:
                severity = db_specific["severity"]
        
        # Override for malware
        if vuln_id.startswith("MAL-"):
            severity = "CRITICAL (MALWARE)"
        
        # Determine if it's malware
        is_malware = (
            vuln_id.startswith("MAL-") or
            "malicious" in summary.lower() or
            "malware" in details.lower() or
            any("malware" in ref.get("type", "").lower() or 
                "malicious" in ref.get("url", "").lower() 
                for ref in vuln.get("references", []))
        )
        
        return {
            "id": vuln_id,
            "summary": summary,
            "details": details,
            "severity": severity,
            "is_malware": is_malware,
            "aliases": vuln.get("aliases", []),
            "references": vuln.get("references", []),
            "affected": vuln.get("affected", []),
            "published": vuln.get("published", ""),
            "modified": vuln.get("modified", ""),
            "database_specific": vuln.get("database_specific", {})
        }
    
    def print_vulnerability_report(self, package_name, version, result, malware_only=False):
        """Print a detailed vulnerability report"""
        if not result:
            print(f"[!] No data returned for {package_name}")
            return False
        
        vulns = result.get("vulns", [])
        
        if not vulns:
            if not malware_only:
                print(f"\n{'='*80}")
                print(f"Package: {package_name}@{version or 'any'}")
                print(f"{'='*80}")
                print("✅ No known vulnerabilities or malware detected")
            return False
        
        # Separate malware from other vulnerabilities
        malware = []
        vulnerabilities = []
        
        for vuln in vulns:
            formatted = self.format_vulnerability(vuln)
            if formatted["is_malware"]:
                malware.append(formatted)
            else:
                vulnerabilities.append(formatted)
        
        # If malware_only mode and no malware, skip this package
        if malware_only and not malware:
            return False
        
        # Print header
        print(f"\n{'='*80}")
        print(f"Package: {package_name}@{version or 'any'}")
        print(f"{'='*80}")
        
        if malware_only:
            print(f"Total Issues: {len(malware)} malware detected")
        else:
            print(f"Total Issues: {len(vulns)} ({len(malware)} malware, {len(vulnerabilities)} vulnerabilities)")
        
        has_critical = False
        
        # Print malware first (most critical)
        if malware:
            print(f"\n{'🚨 MALWARE DETECTED':^80}")
            print(f"{'='*80}")
            has_critical = True
            
            for mal in malware:
                self._print_issue(mal, package_name)
        
        # Print vulnerabilities (only if not malware_only mode)
        if vulnerabilities and not malware_only:
            print(f"\n{'⚠️  VULNERABILITIES':^80}")
            print(f"{'='*80}")
            
            for vuln in vulnerabilities:
                if "CRITICAL" in vuln["severity"].upper() or "HIGH" in vuln["severity"].upper():
                    has_critical = True
                self._print_issue(vuln, package_name)
        
        return has_critical or bool(malware)
    
    def _print_issue(self, issue, package_name):
        """Print a single issue (malware or vulnerability)"""
        print(f"\n{'─'*80}")
        
        # Header
        marker = "🦠" if issue["is_malware"] else "⚠️"
        issue_type = "MALWARE" if issue["is_malware"] else "VULNERABILITY"
        print(f"{marker} {issue_type}: {issue['id']}")
        print(f"   Severity: {issue['severity']}")
        
        # Summary
        if issue['summary']:
            print(f"\n   Summary:")
            for line in issue['summary'].split('\n')[:3]:  # First 3 lines
                if line.strip():
                    print(f"   {line.strip()}")
        
        # Aliases
        if issue['aliases']:
            print(f"\n   Aliases: {', '.join(issue['aliases'])}")
        
        # Affected versions
        if issue['affected']:
            print(f"\n   Affected Versions:")
            for affected in issue['affected']:
                pkg = affected.get('package', {})
                if pkg.get('name') == package_name or pkg.get('name') == f"@{package_name}":
                    ranges = affected.get('ranges', [])
                    versions = affected.get('versions', [])
                    
                    if ranges:
                        for range_info in ranges:
                            range_type = range_info.get('type', 'UNKNOWN')
                            events = range_info.get('events', [])
                            
                            if events:
                                introduced = None
                                fixed = None
                                last_affected = None
                                
                                for event in events:
                                    if 'introduced' in event:
                                        introduced = event['introduced']
                                    elif 'fixed' in event:
                                        fixed = event['fixed']
                                    elif 'last_affected' in event:
                                        last_affected = event['last_affected']
                                
                                if introduced is not None:
                                    range_str = f"   - {range_type}: "
                                    if introduced == "0":
                                        range_str += "All versions"
                                    else:
                                        range_str += f">= {introduced}"
                                    
                                    if fixed:
                                        range_str += f", fixed in {fixed}"
                                    elif last_affected:
                                        range_str += f", last affected: {last_affected}"
                                    
                                    print(range_str)
                    
                    if versions:
                        print(f"   - Specific versions: {', '.join(versions[:10])}")
                        if len(versions) > 10:
                            print(f"     ... and {len(versions) - 10} more")
                    
                    # Database specific info (hashes, sources)
                    db_specific = affected.get('database_specific', {})
                    if db_specific:
                        if 'sha256' in db_specific:
                            print(f"   - SHA256: {db_specific['sha256'][:32]}...")
                        if 'source' in db_specific:
                            print(f"   - Source: {db_specific['source']}")
        
        # References
        if issue['references']:
            print(f"\n   References:")
            for ref in issue['references'][:5]:  # Show first 5 references
                ref_type = ref.get('type', 'WEB')
                ref_url = ref.get('url', '')
                print(f"   - [{ref_type}] {ref_url}")
            if len(issue['references']) > 5:
                print(f"   ... and {len(issue['references']) - 5} more references")
        
        # Database specific malware origins
        if issue['database_specific'].get('malicious-packages-origins'):
            origins = issue['database_specific']['malicious-packages-origins']
            print(f"\n   Malware Sources ({len(origins)} detections):")
            for origin in origins[:3]:
                source = origin.get('source', 'unknown')
                sha = origin.get('sha256', '')
                print(f"   - {source}")
                if sha:
                    print(f"     SHA256: {sha[:32]}...")
        
        # Dates
        if issue['published']:
            pub_date = issue['published'].split('T')[0]
            print(f"\n   Published: {pub_date}")
        if issue['modified']:
            mod_date = issue['modified'].split('T')[0]
            print(f"   Last Modified: {mod_date}")


def load_package_json(file_path):
    """Load dependencies from package.json"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        dependencies = {}
        dependencies.update(data.get("dependencies", {}))
        dependencies.update(data.get("devDependencies", {}))
        
        return dependencies
    except Exception as e:
        print(f"[!] Error reading {file_path}: {e}")
        return {}


def load_package_lock(file_path):
    """Load all deps (including transitive) from package-lock.json"""
    try:
        with open(file_path, 'r') as f:
            lock_data = json.load(f)
        
        dependencies = {}
        
        # npm v2/v3 (lockfileVersion >= 2)
        if "packages" in lock_data:
            for path, meta in lock_data["packages"].items():
                if path == "":  # skip root entry
                    continue
                name = meta.get("name")
                version = meta.get("version")
                if name and version:
                    dependencies[name] = version
        
        # npm v1 (lockfileVersion = 1)
        elif "dependencies" in lock_data:
            def extract_deps(node, collected):
                for name, meta in node.get("dependencies", {}).items():
                    version = meta.get("version", "unknown")
                    collected[name] = version
                    if "dependencies" in meta:
                        extract_deps(meta, collected)
            
            extract_deps(lock_data, dependencies)
        
        return dependencies
    except Exception as e:
        print(f"[!] Error reading {file_path}: {e}")
        return {}


def load_yarn_lock(file_path):
    """Load deps from yarn.lock (basic parser for Yarn v1)"""
    try:
        dependencies = {}
        with open(file_path, 'r') as f:
            current_pkg = None
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.endswith(":"):
                    # entry start like "left-pad@^1.0.0:"
                    pkg_name = line.split("@", 1)[0].strip('"')
                    current_pkg = pkg_name
                elif line.startswith("version") and current_pkg:
                    version = line.split(" ")[1].strip('"')
                    dependencies[current_pkg] = version
                    current_pkg = None
        
        return dependencies
    except Exception as e:
        print(f"[!] Error reading {file_path}: {e}")
        return {}


def find_dependency_files(start_path="."):
    """Find all package.json, package-lock.json, and yarn.lock files in directory tree"""
    from pathlib import Path
    
    dependency_files = {
        "package.json": [],
        "package-lock.json": [],
        "yarn.lock": []
    }
    
    start_path = Path(start_path)
    
    # Search for all dependency files recursively
    for file_type in dependency_files.keys():
        for file_path in start_path.rglob(file_type):
            # Skip node_modules directories
            if "node_modules" not in file_path.parts:
                dependency_files[file_type].append(file_path)
    
    return dependency_files


def load_all_dependencies(dependency_files):
    """Load dependencies from all found files"""
    all_dependencies = {}
    
    # Load from package.json files
    for pkg_file in dependency_files["package.json"]:
        print(f"[+] Loading dependencies from {pkg_file}")
        deps = load_package_json(pkg_file)
        all_dependencies.update(deps)
    
    # Load from package-lock.json files
    for lock_file in dependency_files["package-lock.json"]:
        print(f"[+] Loading dependencies from {lock_file}")
        deps = load_package_lock(lock_file)
        all_dependencies.update(deps)
    
    # Load from yarn.lock files
    for yarn_file in dependency_files["yarn.lock"]:
        print(f"[+] Loading dependencies from {yarn_file}")
        deps = load_yarn_lock(yarn_file)
        all_dependencies.update(deps)
    
    return all_dependencies


def parse_package_spec(spec):
    """Parse package specification like 'lodash@4.17.21' into name and version"""
    if '@' in spec:
        # Handle scoped packages like @babel/core@7.0.0
        if spec.startswith('@'):
            parts = spec.split('@')
            if len(parts) >= 3:
                name = '@' + parts[1]
                version = parts[2]
                return name, version
            else:
                return spec, None
        else:
            parts = spec.split('@')
            return parts[0], parts[1] if len(parts) > 1 else None
    return spec, None


def main():
    parser = argparse.ArgumentParser(
        description="Scan npm packages for vulnerabilities and malware using OSV.dev API"
    )
    parser.add_argument(
        "package",
        nargs="?",
        help="Package to scan (e.g., 'lodash@4.17.21' or 'lodash')"
    )
    parser.add_argument(
        "--file",
        help="Path to package.json, package-lock.json, or yarn.lock file"
    )
    parser.add_argument(
        "--scan-dir",
        help="Scan directory recursively for all dependency files (package.json, package-lock.json, yarn.lock)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON results"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Use batch API for multiple packages (faster)"
    )
    parser.add_argument(
        "--malware-only",
        action="store_true",
        help="Only report malware, ignore regular vulnerabilities"
    )
    
    args = parser.parse_args()
    scanner = OSVScanner()
    
    # Scan directory recursively for all dependency files
    if args.scan_dir:
        print(f"[+] Scanning directory: {args.scan_dir}")
        print(f"[+] Looking for package.json, package-lock.json, and yarn.lock files...")
        
        dependency_files = find_dependency_files(args.scan_dir)
        
        total_files = sum(len(files) for files in dependency_files.values())
        if total_files == 0:
            print("[!] No dependency files found in directory")
            sys.exit(1)
        
        print(f"[+] Found {len(dependency_files['package.json'])} package.json files")
        print(f"[+] Found {len(dependency_files['package-lock.json'])} package-lock.json files")
        print(f"[+] Found {len(dependency_files['yarn.lock'])} yarn.lock files")
        
        dependencies = load_all_dependencies(dependency_files)
        
        if not dependencies:
            print("[!] No dependencies found")
            sys.exit(1)
        
        print(f"[+] Total unique dependencies found: {len(dependencies)}")
        print(f"[+] Querying OSV.dev database...")
        
        # Process the batch query directly for scan-dir mode
        batch_result = scanner.batch_query(dependencies)
        if batch_result and 'results' in batch_result:
            critical_packages = []
            malware_packages = []
            vulnerable_packages = []
            
            pkg_list = list(dependencies.keys())
            for i, result in enumerate(batch_result['results']):
                pkg_name = pkg_list[i] if i < len(pkg_list) else "unknown"
                pkg_version = dependencies.get(pkg_name, "unknown")
                
                if result.get('vulns'):
                    has_critical = scanner.print_vulnerability_report(
                        pkg_name, 
                        pkg_version, 
                        result,
                        malware_only=args.malware_only
                    )
                    
                    # Check if malware
                    has_malware = any(
                        vuln.get('id', '').startswith('MAL-') 
                        for vuln in result.get('vulns', [])
                    )
                    
                    if has_malware:
                        malware_packages.append(f"{pkg_name}@{pkg_version}")
                    elif has_critical and not args.malware_only:
                        critical_packages.append(f"{pkg_name}@{pkg_version}")
                    elif not args.malware_only:
                        vulnerable_packages.append(f"{pkg_name}@{pkg_version}")
            
            # Summary
            print(f"\n{'='*80}")
            print(f"{'SCAN SUMMARY':^80}")
            print(f"{'='*80}")
            print(f"Total packages scanned: {len(dependencies)}")
            
            if malware_packages:
                print(f"\n🚨 MALWARE DETECTED ({len(malware_packages)} packages):")
                for pkg in malware_packages:
                    print(f"   - {pkg}")
            
            if not args.malware_only:
                if critical_packages:
                    print(f"\n⚠️  CRITICAL VULNERABILITIES ({len(critical_packages)} packages):")
                    for pkg in critical_packages:
                        print(f"   - {pkg}")
                
                if vulnerable_packages:
                    print(f"\n⚡ OTHER VULNERABILITIES ({len(vulnerable_packages)} packages):")
                    for pkg in vulnerable_packages:
                        print(f"   - {pkg}")
            
            if args.malware_only:
                if not malware_packages:
                    print("\n✅ No malware detected")
            else:
                if not malware_packages and not critical_packages and not vulnerable_packages:
                    print("\n✅ No vulnerabilities or malware detected")
        else:
            print("[!] Batch query failed")
    
    # Scan from specific file
    elif args.file:
        # Determine file type and load accordingly
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"[!] File not found: {args.file}")
            sys.exit(1)
        
        if file_path.name == "package.json":
            dependencies = load_package_json(args.file)
        elif file_path.name == "package-lock.json":
            dependencies = load_package_lock(args.file)
        elif file_path.name == "yarn.lock":
            dependencies = load_yarn_lock(args.file)
        else:
            print(f"[!] Unsupported file type. Use package.json, package-lock.json, or yarn.lock")
            sys.exit(1)
        
        if not dependencies:
            print(f"[!] No dependencies found in {args.file}")
            sys.exit(1)
        
        print(f"[+] Found {len(dependencies)} dependencies in {args.file}")
        print(f"[+] Querying OSV.dev database...")
        
        if args.batch:
            # Batch query
            batch_result = scanner.batch_query(dependencies)
            if batch_result and 'results' in batch_result:
                critical_packages = []
                malware_packages = []
                vulnerable_packages = []
                
                pkg_list = list(dependencies.keys())
                for i, result in enumerate(batch_result['results']):
                    pkg_name = pkg_list[i] if i < len(pkg_list) else "unknown"
                    pkg_version = dependencies.get(pkg_name, "unknown")
                    
                    if result.get('vulns'):
                        has_critical = scanner.print_vulnerability_report(
                            pkg_name, 
                            pkg_version, 
                            result,
                            malware_only=args.malware_only
                        )
                        
                        # Check if malware
                        has_malware = any(
                            vuln.get('id', '').startswith('MAL-') 
                            for vuln in result.get('vulns', [])
                        )
                        
                        if has_malware:
                            malware_packages.append(f"{pkg_name}@{pkg_version}")
                        elif has_critical and not args.malware_only:
                            critical_packages.append(f"{pkg_name}@{pkg_version}")
                        elif not args.malware_only:
                            vulnerable_packages.append(f"{pkg_name}@{pkg_version}")
                
                # Summary
                print(f"\n{'='*80}")
                print(f"{'SCAN SUMMARY':^80}")
                print(f"{'='*80}")
                print(f"Total packages scanned: {len(dependencies)}")
                
                if malware_packages:
                    print(f"\n🚨 MALWARE DETECTED ({len(malware_packages)} packages):")
                    for pkg in malware_packages:
                        print(f"   - {pkg}")
                
                if not args.malware_only:
                    if critical_packages:
                        print(f"\n⚠️  CRITICAL VULNERABILITIES ({len(critical_packages)} packages):")
                        for pkg in critical_packages:
                            print(f"   - {pkg}")
                    
                    if vulnerable_packages:
                        print(f"\n⚡ OTHER VULNERABILITIES ({len(vulnerable_packages)} packages):")
                        for pkg in vulnerable_packages:
                            print(f"   - {pkg}")
                
                if args.malware_only:
                    if not malware_packages:
                        print("\n✅ No malware detected")
                else:
                    if not malware_packages and not critical_packages and not vulnerable_packages:
                        print("\n✅ No vulnerabilities or malware detected")
            else:
                print("[!] Batch query failed, falling back to individual queries...")
                args.batch = False
        
        if not args.batch:
            # Individual queries
            critical_packages = []
            malware_packages = []
            vulnerable_packages = []
            
            for pkg_name, pkg_version in dependencies.items():
                clean_version = re.sub(r'^[\^~>=<]+', '', pkg_version)
                result = scanner.query_package(pkg_name, clean_version)
                
                if result and result.get('vulns'):
                    has_critical = scanner.print_vulnerability_report(
                        pkg_name, 
                        clean_version, 
                        result,
                        malware_only=args.malware_only
                    )
                    
                    # Check if malware
                    has_malware = any(
                        vuln.get('id', '').startswith('MAL-') 
                        for vuln in result.get('vulns', [])
                    )
                    
                    if has_malware:
                        malware_packages.append(f"{pkg_name}@{clean_version}")
                    elif has_critical and not args.malware_only:
                        critical_packages.append(f"{pkg_name}@{clean_version}")
                    elif not args.malware_only:
                        vulnerable_packages.append(f"{pkg_name}@{clean_version}")
            
            # Summary
            print(f"\n{'='*80}")
            print(f"{'SCAN SUMMARY':^80}")
            print(f"{'='*80}")
            print(f"Total packages scanned: {len(dependencies)}")
            
            if malware_packages:
                print(f"\n🚨 MALWARE DETECTED ({len(malware_packages)} packages):")
                for pkg in malware_packages:
                    print(f"   - {pkg}")
            
            if not args.malware_only:
                if critical_packages:
                    print(f"\n⚠️  CRITICAL VULNERABILITIES ({len(critical_packages)} packages):")
                    for pkg in critical_packages:
                        print(f"   - {pkg}")
                
                if vulnerable_packages:
                    print(f"\n⚡ OTHER VULNERABILITIES ({len(vulnerable_packages)} packages):")
                    for pkg in vulnerable_packages:
                        print(f"   - {pkg}")
            
            if args.malware_only:
                if not malware_packages:
                    print("\n✅ No malware detected")
            else:
                if not malware_packages and not critical_packages and not vulnerable_packages:
                    print("\n✅ No vulnerabilities or malware detected")
    
    # Scan single package
    elif args.package:
        pkg_name, pkg_version = parse_package_spec(args.package)
        print(f"[+] Querying OSV.dev for {pkg_name}@{pkg_version or 'any version'}...")
        
        result = scanner.query_package(pkg_name, pkg_version)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            scanner.print_vulnerability_report(pkg_name, pkg_version or "any", result)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

