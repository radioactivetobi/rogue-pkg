#!/usr/bin/env python3
"""
Test script for RoguePkg MCP Server tools
Run this to verify the MCP server is working correctly
"""

import sys
import os

# Add mcp directory to path to import mcp_server
mcp_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, mcp_dir)
# Add root directory to path for roguepkg
root_dir = os.path.dirname(mcp_dir)
sys.path.insert(0, root_dir)

from mcp_server import RoguePkgMCPServer
import json


def print_result(title: str, result: dict):
    """Pretty print test results"""
    print(f"\n{'='*80}")
    print(f"Test: {title}")
    print(f"{'='*80}")
    print(json.dumps(result, indent=2))
    print()


def test_scan_package():
    """Test scanning a single package"""
    server = RoguePkgMCPServer()
    
    # Test 1: Clean package
    result = server.scan_package("lodash@4.17.21", malware_only=False)
    print_result("Scan lodash@4.17.21", result)
    
    # Test 2: Package without version
    result = server.scan_package("express", malware_only=True)
    print_result("Scan express (no version, malware only)", result)
    
    # Test 3: Known malicious package (if available in OSV)
    result = server.scan_package("@ctrl/tinycolor@4.1.2", malware_only=False)
    print_result("Scan @ctrl/tinycolor@4.1.2 (known malware)", result)


def test_scan_dependencies():
    """Test scanning multiple dependencies"""
    server = RoguePkgMCPServer()
    
    dependencies = {
        "lodash": "4.17.21",
        "express": "4.18.2",
        "axios": "1.6.2"
    }
    
    result = server.scan_dependencies(dependencies, malware_only=False)
    print_result("Scan multiple dependencies", result)


def test_github_integration():
    """Test GitHub integration (requires GITHUB_TOKEN)"""
    server = RoguePkgMCPServer()
    
    # Check if token is available
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("\n⚠️  GITHUB_TOKEN not set. Skipping GitHub integration tests.")
        print("Set GITHUB_TOKEN environment variable to test GitHub features.")
        return
    
    server.initialize_github(token)
    
    # Test 1: Scan a public repository
    result = server.scan_github_repo("lodash", "lodash", malware_only=True)
    print_result("Scan lodash/lodash repository", result)
    
    # Test 2: Organization scan (limited to 5 repos for testing)
    result = server.scan_github_org("vercel", malware_only=True, max_repos=5)
    print_result("Scan vercel organization (first 5 repos)", result)


def main():
    """Run all tests"""
    print("🛡️  RoguePkg MCP Server - Tool Tests")
    print("="*80)
    
    # Test 1: Package scanning
    print("\n📦 Testing package scanning...")
    test_scan_package()
    
    # Test 2: Batch dependency scanning
    print("\n📦 Testing batch dependency scanning...")
    test_scan_dependencies()
    
    # Test 3: GitHub integration
    print("\n🔗 Testing GitHub integration...")
    test_github_integration()
    
    print("\n✅ All tests completed!")
    print("\nNote: Some tests may fail if packages are not in OSV database")
    print("or if GITHUB_TOKEN is not set for GitHub tests.")


if __name__ == "__main__":
    main()

