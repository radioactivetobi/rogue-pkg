#!/usr/bin/env python3
"""
RoguePkg MCP Server
Model Context Protocol server for vulnerability and malware detection in npm packages.
Integrates with GitHub to scan repositories and organizations.
"""

import asyncio
import json
import sys
import os
from typing import Any, Optional, Dict, List
import requests
from urllib.parse import quote

# Import the OSV scanner from roguepkg (parent directory)
import sys
import os
# Add parent directory to path to import roguepkg
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from roguepkg import OSVScanner, load_package_json, load_package_lock, load_yarn_lock, parse_package_spec


class GitHubAPI:
    """GitHub API integration for fetching repository files and dependency insights"""
    
    def __init__(self, token: Optional[str] = None):
        self.base_url = "https://api.github.com"
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        })
        if self.token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
    
    def get_file_content(self, owner: str, repo: str, path: str, branch: str = "main") -> Optional[str]:
        """Fetch file content from a GitHub repository"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": branch}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                # GitHub returns base64 encoded content
                import base64
                content = base64.b64decode(data.get("content", "")).decode("utf-8")
                return content
            elif response.status_code == 404:
                # Try master branch if main fails
                if branch == "main":
                    return self.get_file_content(owner, repo, path, "master")
                return None
            else:
                return None
        except Exception as e:
            print(f"Error fetching file: {e}", file=sys.stderr)
            return None
    
    def get_repo_dependencies(self, owner: str, repo: str) -> Dict[str, str]:
        """
        Fetch dependencies from a repository by checking package.json, package-lock.json, etc.
        """
        dependencies = {}
        
        # Try package.json first
        pkg_json = self.get_file_content(owner, repo, "package.json")
        if pkg_json:
            try:
                data = json.loads(pkg_json)
                dependencies.update(data.get("dependencies", {}))
                dependencies.update(data.get("devDependencies", {}))
            except json.JSONDecodeError:
                pass
        
        # Try package-lock.json for more complete dependency list
        pkg_lock = self.get_file_content(owner, repo, "package-lock.json")
        if pkg_lock:
            try:
                lock_data = json.loads(pkg_lock)
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
            except json.JSONDecodeError:
                pass
        
        return dependencies
    
    def get_org_repositories(self, org: str, per_page: int = 100) -> List[Dict[str, str]]:
        """Get all repositories in an organization"""
        url = f"{self.base_url}/orgs/{org}/repos"
        repos = []
        page = 1
        
        try:
            while True:
                response = self.session.get(
                    url, 
                    params={"per_page": per_page, "page": page, "type": "all"},
                    timeout=30
                )
                if response.status_code != 200:
                    break
                
                data = response.json()
                if not data:
                    break
                
                for repo in data:
                    repos.append({
                        "name": repo["name"],
                        "full_name": repo["full_name"],
                        "owner": repo["owner"]["login"],
                        "default_branch": repo.get("default_branch", "main"),
                        "language": repo.get("language"),
                        "private": repo.get("private", False)
                    })
                
                page += 1
                
                # Safety limit
                if page > 10:
                    break
            
            return repos
        except Exception as e:
            print(f"Error fetching org repos: {e}", file=sys.stderr)
            return []
    
    def get_dependency_graph(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get dependency graph/insights for a repository
        Note: Requires special permissions and may not be available for all repos
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/dependency-graph/sbom"
        
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception:
            return {}


class RoguePkgMCPServer:
    """MCP Server for RoguePkg functionality"""
    
    def __init__(self):
        self.scanner = OSVScanner()
        self.github = None
    
    def initialize_github(self, token: Optional[str] = None):
        """Initialize GitHub integration"""
        self.github = GitHubAPI(token)
    
    def scan_package(self, package_spec: str, malware_only: bool = False) -> Dict[str, Any]:
        """
        Scan a single package for vulnerabilities and malware
        
        Args:
            package_spec: Package specification (e.g., 'lodash@4.17.21' or 'lodash')
            malware_only: Only report malware
        
        Returns:
            Dictionary with scan results
        """
        pkg_name, pkg_version = parse_package_spec(package_spec)
        result = self.scanner.query_package(pkg_name, pkg_version)
        
        if not result or not result.get("vulns"):
            return {
                "package": package_spec,
                "status": "clean",
                "malware_count": 0,
                "vulnerability_count": 0,
                "issues": []
            }
        
        # Process vulnerabilities
        malware = []
        vulnerabilities = []
        
        for vuln in result.get("vulns", []):
            formatted = self.scanner.format_vulnerability(vuln)
            if formatted["is_malware"]:
                malware.append(formatted)
            else:
                vulnerabilities.append(formatted)
        
        # Filter if malware_only
        if malware_only:
            issues = malware
        else:
            issues = malware + vulnerabilities
        
        return {
            "package": package_spec,
            "status": "malware-detected" if malware else ("vulnerabilities-detected" if vulnerabilities else "clean"),
            "malware_count": len(malware),
            "vulnerability_count": len(vulnerabilities),
            "issues": [self._format_issue_for_output(issue) for issue in issues]
        }
    
    def scan_dependencies(self, dependencies: Dict[str, str], malware_only: bool = False) -> Dict[str, Any]:
        """
        Scan multiple dependencies in batch
        
        Args:
            dependencies: Dictionary of package names to versions
            malware_only: Only report malware
        
        Returns:
            Dictionary with batch scan results
        """
        if not dependencies:
            return {
                "status": "clean",
                "total_scanned": 0,
                "malware_count": 0,
                "vulnerability_count": 0,
                "affected_packages": []
            }
        
        batch_result = self.scanner.batch_query(dependencies)
        
        if not batch_result or "results" not in batch_result:
            return {
                "status": "error",
                "error": "Batch query failed",
                "total_scanned": len(dependencies),
                "malware_count": 0,
                "vulnerability_count": 0,
                "affected_packages": []
            }
        
        malware_packages = []
        vulnerable_packages = []
        pkg_list = list(dependencies.keys())
        
        for i, result in enumerate(batch_result["results"]):
            pkg_name = pkg_list[i] if i < len(pkg_list) else "unknown"
            pkg_version = dependencies.get(pkg_name, "unknown")
            
            if not result.get("vulns"):
                continue
            
            malware = []
            vulnerabilities = []
            
            for vuln in result["vulns"]:
                formatted = self.scanner.format_vulnerability(vuln)
                if formatted["is_malware"]:
                    malware.append(formatted)
                else:
                    vulnerabilities.append(formatted)
            
            if malware:
                malware_packages.append({
                    "package": f"{pkg_name}@{pkg_version}",
                    "malware_count": len(malware),
                    "issues": [self._format_issue_for_output(m) for m in malware]
                })
            
            if vulnerabilities and not malware_only:
                vulnerable_packages.append({
                    "package": f"{pkg_name}@{pkg_version}",
                    "vulnerability_count": len(vulnerabilities),
                    "issues": [self._format_issue_for_output(v) for v in vulnerabilities]
                })
        
        return {
            "status": "malware-detected" if malware_packages else ("vulnerabilities-detected" if vulnerable_packages else "clean"),
            "total_scanned": len(dependencies),
            "malware_count": len(malware_packages),
            "vulnerability_count": len(vulnerable_packages),
            "malware_packages": malware_packages,
            "vulnerable_packages": vulnerable_packages
        }
    
    def scan_github_repo(self, owner: str, repo: str, malware_only: bool = False) -> Dict[str, Any]:
        """
        Scan a GitHub repository for vulnerabilities
        
        Args:
            owner: Repository owner
            repo: Repository name
            malware_only: Only report malware
        
        Returns:
            Dictionary with scan results
        """
        if not self.github:
            return {
                "status": "error",
                "error": "GitHub integration not initialized. Set GITHUB_TOKEN environment variable."
            }
        
        dependencies = self.github.get_repo_dependencies(owner, repo)
        
        if not dependencies:
            return {
                "status": "error",
                "error": f"No dependencies found in {owner}/{repo}. Repository may not have package.json or may not be accessible.",
                "repository": f"{owner}/{repo}"
            }
        
        result = self.scan_dependencies(dependencies, malware_only)
        result["repository"] = f"{owner}/{repo}"
        
        return result
    
    def scan_github_org(self, org: str, malware_only: bool = True, max_repos: int = 50) -> Dict[str, Any]:
        """
        Scan all repositories in a GitHub organization
        
        Args:
            org: Organization name
            malware_only: Only report malware (recommended for org-wide scans)
            max_repos: Maximum number of repositories to scan
        
        Returns:
            Dictionary with organization-wide scan results
        """
        if not self.github:
            return {
                "status": "error",
                "error": "GitHub integration not initialized. Set GITHUB_TOKEN environment variable."
            }
        
        repos = self.github.get_org_repositories(org)
        
        if not repos:
            return {
                "status": "error",
                "error": f"No repositories found for organization {org} or insufficient permissions",
                "organization": org
            }
        
        # Limit repos to scan
        repos = repos[:max_repos]
        
        org_dependencies = {}
        repo_dependency_map = {}
        
        # Collect all unique dependencies across repos
        for repo_info in repos:
            repo_name = repo_info["name"]
            owner = repo_info["owner"]
            
            deps = self.github.get_repo_dependencies(owner, repo_name)
            if deps:
                repo_dependency_map[repo_name] = deps
                # Track which repos use which dependency
                for pkg_name, pkg_version in deps.items():
                    if pkg_name not in org_dependencies:
                        org_dependencies[pkg_name] = pkg_version
        
        if not org_dependencies:
            return {
                "status": "clean",
                "organization": org,
                "repositories_scanned": len(repos),
                "repositories_with_dependencies": 0,
                "total_unique_dependencies": 0,
                "malware_count": 0,
                "affected_repositories": []
            }
        
        # Scan all unique dependencies
        scan_result = self.scan_dependencies(org_dependencies, malware_only)
        
        # Map affected packages back to repositories
        affected_repos = {}
        
        for malware_pkg in scan_result.get("malware_packages", []):
            pkg_name = malware_pkg["package"].split("@")[0]
            for repo_name, deps in repo_dependency_map.items():
                if pkg_name in deps:
                    if repo_name not in affected_repos:
                        affected_repos[repo_name] = []
                    affected_repos[repo_name].append(malware_pkg)
        
        if not malware_only:
            for vuln_pkg in scan_result.get("vulnerable_packages", []):
                pkg_name = vuln_pkg["package"].split("@")[0]
                for repo_name, deps in repo_dependency_map.items():
                    if pkg_name in deps:
                        if repo_name not in affected_repos:
                            affected_repos[repo_name] = []
                        affected_repos[repo_name].append(vuln_pkg)
        
        return {
            "status": scan_result["status"],
            "organization": org,
            "repositories_scanned": len(repos),
            "repositories_with_dependencies": len(repo_dependency_map),
            "repositories_affected": len(affected_repos),
            "total_unique_dependencies": len(org_dependencies),
            "malware_count": scan_result["malware_count"],
            "vulnerability_count": scan_result.get("vulnerability_count", 0),
            "affected_repositories": [
                {
                    "repository": repo_name,
                    "affected_packages": packages
                }
                for repo_name, packages in affected_repos.items()
            ]
        }
    
    def _format_issue_for_output(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Format issue for JSON output"""
        return {
            "id": issue["id"],
            "type": "malware" if issue["is_malware"] else "vulnerability",
            "severity": issue["severity"],
            "summary": issue["summary"],
            "published": issue.get("published", ""),
            "references": [ref.get("url", "") for ref in issue.get("references", [])[:3]],
            "aliases": issue.get("aliases", [])
        }


def handle_call_tool(server: RoguePkgMCPServer, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP tool calls"""
    
    if name == "scan_package":
        package = arguments.get("package", "")
        malware_only = arguments.get("malware_only", False)
        return server.scan_package(package, malware_only)
    
    elif name == "scan_github_repository":
        owner = arguments.get("owner", "")
        repo = arguments.get("repository", "")
        malware_only = arguments.get("malware_only", False)
        return server.scan_github_repo(owner, repo, malware_only)
    
    elif name == "scan_github_organization":
        org = arguments.get("organization", "")
        malware_only = arguments.get("malware_only", True)
        max_repos = arguments.get("max_repos", 50)
        return server.scan_github_org(org, malware_only, max_repos)
    
    elif name == "scan_dependencies":
        dependencies = arguments.get("dependencies", {})
        malware_only = arguments.get("malware_only", False)
        return server.scan_dependencies(dependencies, malware_only)
    
    else:
        return {"error": f"Unknown tool: {name}"}


def print_response(response: Dict[str, Any], request_id: Any = None):
    """Print JSON-RPC 2.0 response for MCP protocol"""
    jsonrpc_response = {
        "jsonrpc": "2.0"
    }
    
    if request_id is not None:
        jsonrpc_response["id"] = request_id
    
    # Check if this is an error or result
    if "error" in response:
        # Format as JSON-RPC error
        error_msg = response["error"]
        jsonrpc_response["error"] = {
            "code": -32603,  # Internal error
            "message": error_msg if isinstance(error_msg, str) else str(error_msg)
        }
    else:
        jsonrpc_response["result"] = response
    
    print(json.dumps(jsonrpc_response), flush=True)


def main():
    """Main MCP server loop"""
    server = RoguePkgMCPServer()
    
    # Initialize GitHub integration if token is available
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        server.initialize_github(github_token)
        print("GitHub integration initialized", file=sys.stderr)
    else:
        print("Warning: GITHUB_TOKEN not set. GitHub features will be unavailable.", file=sys.stderr)
    
    print("RoguePkg MCP Server started", file=sys.stderr)
    print("Listening for MCP requests...", file=sys.stderr)
    
    # Simple stdio-based MCP protocol handler
    for line in sys.stdin:
        request_id = None
        try:
            request = json.loads(line.strip())
            request_id = request.get("id")
            method = request.get("method")
            
            if method == "initialize":
                # MCP initialization handshake
                response = {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "roguepkg",
                        "version": "1.0.0"
                    }
                }
                print_response(response, request_id)
            
            elif method == "notifications/initialized":
                # Client has completed initialization, no response needed
                pass
            
            elif method == "ping":
                # Health check
                response = {}
                print_response(response, request_id)
            
            elif method == "tools/list":
                # Return available tools
                response = {
                    "tools": [
                        {
                            "name": "scan_package",
                            "description": "Scan a single npm package for vulnerabilities and malware",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "package": {
                                        "type": "string",
                                        "description": "Package specification (e.g., 'lodash@4.17.21' or 'lodash')"
                                    },
                                    "malware_only": {
                                        "type": "boolean",
                                        "description": "Only report malware, skip regular vulnerabilities",
                                        "default": False
                                    }
                                },
                                "required": ["package"]
                            }
                        },
                        {
                            "name": "scan_github_repository",
                            "description": "Scan a GitHub repository's dependencies for vulnerabilities and malware",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "owner": {
                                        "type": "string",
                                        "description": "Repository owner (user or organization)"
                                    },
                                    "repository": {
                                        "type": "string",
                                        "description": "Repository name"
                                    },
                                    "malware_only": {
                                        "type": "boolean",
                                        "description": "Only report malware",
                                        "default": False
                                    }
                                },
                                "required": ["owner", "repository"]
                            }
                        },
                        {
                            "name": "scan_github_organization",
                            "description": "Scan all repositories in a GitHub organization for vulnerabilities and malware",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "organization": {
                                        "type": "string",
                                        "description": "Organization name"
                                    },
                                    "malware_only": {
                                        "type": "boolean",
                                        "description": "Only report malware (recommended for org-wide scans)",
                                        "default": True
                                    },
                                    "max_repos": {
                                        "type": "integer",
                                        "description": "Maximum number of repositories to scan",
                                        "default": 50
                                    }
                                },
                                "required": ["organization"]
                            }
                        },
                        {
                            "name": "scan_dependencies",
                            "description": "Scan a list of dependencies for vulnerabilities and malware",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "dependencies": {
                                        "type": "object",
                                        "description": "Dictionary of package names to versions (e.g., {'lodash': '4.17.21'})"
                                    },
                                    "malware_only": {
                                        "type": "boolean",
                                        "description": "Only report malware",
                                        "default": False
                                    }
                                },
                                "required": ["dependencies"]
                            }
                        }
                    ]
                }
                print_response(response, request_id)
            
            elif request.get("method") == "tools/call":
                tool_name = request.get("params", {}).get("name")
                arguments = request.get("params", {}).get("arguments", {})
                
                result = handle_call_tool(server, tool_name, arguments)
                
                response = {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
                print_response(response, request_id)
            
            else:
                # Unknown method
                print(f"Warning: Unknown method '{method}' received", file=sys.stderr)
                response = {"error": f"Unknown method: {method}"}
                print_response(response, request_id)
        
        except json.JSONDecodeError as e:
            response = {"error": f"Invalid JSON: {str(e)}"}
            print_response(response, request_id)
        except Exception as e:
            response = {"error": f"Server error: {str(e)}"}
            print_response(response, request_id)


if __name__ == "__main__":
    main()

