#!/usr/bin/env python3
"""
RoguePkg MCP Server - Setup Verification Script
Checks if everything is configured correctly
"""

import sys
import os
import json


def print_status(check: str, passed: bool, message: str = ""):
    """Print check status"""
    status = "✅" if passed else "❌"
    print(f"{status} {check}")
    if message:
        print(f"   {message}")


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    passed = version >= (3, 8)
    print_status(
        "Python version",
        passed,
        f"Python {version.major}.{version.minor}.{version.micro}" + 
        ("" if passed else " (requires 3.8+)")
    )
    return passed


def check_dependencies():
    """Check if required packages are installed"""
    try:
        import requests
        print_status("requests package", True, f"Version: {requests.__version__}")
        return True
    except ImportError:
        print_status("requests package", False, "Not installed. Run: pip install requests")
        return False


def check_roguepkg_module():
    """Check if roguepkg.py is accessible"""
    try:
        # Add parent directory to path
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        import roguepkg
        print_status("roguepkg.py module", True)
        return True
    except ImportError:
        print_status("roguepkg.py module", False, "Cannot import roguepkg.py from parent directory")
        return False


def check_mcp_server():
    """Check if MCP server file exists"""
    mcp_server_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp_server.py")
    if os.path.exists(mcp_server_path):
        print_status("mcp_server.py", True, f"Location: mcp/mcp_server.py")
        return True
    else:
        print_status("mcp_server.py", False, "File not found in mcp/ directory")
        return False


def check_github_token():
    """Check if GitHub token is set"""
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        # Mask token for security
        masked = token[:7] + "..." + token[-4:] if len(token) > 11 else "***"
        print_status("GITHUB_TOKEN", True, f"Set: {masked}")
        return True
    else:
        print_status("GITHUB_TOKEN", False, "Not set (optional, but recommended)")
        print("   To set: export GITHUB_TOKEN='your_token_here'")
        return False


def test_osv_connection():
    """Test connection to OSV.dev API"""
    try:
        import requests
        response = requests.get("https://api.osv.dev/v1/vulns/GHSA-c3h9-896r-86jm", timeout=10)
        passed = response.status_code == 200
        print_status("OSV.dev API connection", passed)
        return passed
    except Exception as e:
        print_status("OSV.dev API connection", False, str(e))
        return False


def test_github_connection():
    """Test connection to GitHub API"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print_status("GitHub API connection", False, "Skipped (no token)")
        return False
    
    try:
        import requests
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        passed = response.status_code == 200
        
        if passed:
            data = response.json()
            username = data.get("login", "unknown")
            print_status("GitHub API connection", True, f"Authenticated as: {username}")
        else:
            print_status("GitHub API connection", False, f"Status code: {response.status_code}")
        
        return passed
    except Exception as e:
        print_status("GitHub API connection", False, str(e))
        return False


def test_basic_scan():
    """Test basic package scanning"""
    try:
        # Add parent directory to path
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from mcp_server import RoguePkgMCPServer
        server = RoguePkgMCPServer()
        result = server.scan_package("lodash@4.17.21", malware_only=True)
        passed = result.get("status") in ["clean", "malware-detected", "vulnerabilities-detected"]
        print_status("Basic package scan", passed, f"Status: {result.get('status')}")
        return passed
    except Exception as e:
        print_status("Basic package scan", False, str(e))
        return False


def main():
    """Run all verification checks"""
    print("🛡️  RoguePkg MCP Server - Setup Verification")
    print("=" * 80)
    print()
    
    checks = []
    
    print("📋 Checking System Requirements...")
    checks.append(check_python_version())
    checks.append(check_dependencies())
    print()
    
    print("📋 Checking Files...")
    checks.append(check_roguepkg_module())
    checks.append(check_mcp_server())
    print()
    
    print("📋 Checking Configuration...")
    token_set = check_github_token()
    print()
    
    print("📋 Testing Connections...")
    checks.append(test_osv_connection())
    if token_set:
        test_github_connection()
    print()
    
    print("📋 Testing Functionality...")
    checks.append(test_basic_scan())
    print()
    
    # Summary
    print("=" * 80)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print("✅ All critical checks passed!")
        print()
        print("🎉 Your RoguePkg MCP server is ready to use!")
        print()
        print("Next steps:")
        print("1. Configure your AI assistant (see SETUP_MCP.md)")
        print("2. Restart your AI assistant")
        print("3. Try: 'Check if lodash@4.17.21 has any vulnerabilities'")
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print()
        print("Please fix the failed checks before using the MCP server.")
        print("See SETUP_MCP.md for detailed setup instructions.")
    
    print()
    print("For help: https://github.com/radioactivetobi/roguepkg")
    print("=" * 80)


if __name__ == "__main__":
    main()

