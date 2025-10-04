# RoguePkg - Software Supply Chain Compromise Detection

[![GitHub Action](https://img.shields.io/badge/GitHub-Action-blue?logo=github-actions)](https://github.com/marketplace/actions/roguepkg-malware-vulnerability-scanner)
[![OSV.dev](https://img.shields.io/badge/OSV.dev-Powered-green)](https://osv.dev)
[![Free](https://img.shields.io/badge/100%25-Free-brightgreen)](https://osv.dev)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Detect malicious npm packages and vulnerabilities in your JavaScript/TypeScript projects using the free [OSV.dev](https://osv.dev) (Open Source Vulnerabilities) database. Perfect for CI/CD pipelines, pull request checks, and local development.

**Coming Soon:** PyPI (Python), Maven (Java), and more ecosystem support!

**NEW:** 💬 **MCP Server** - Integrate with AI assistants (Claude, Cursor, Cline) for chat-based security scanning!

## 🚀 Features

-  **Malware Detection** - Identify compromised npm packages
-  **Vulnerability Scanning** - Find CVEs and security issues
-  **Fast** - Batch scanning for multiple packages
-  **Comprehensive** - Aggregates data from GitHub, npm, and more
-  **GitHub Action** - Easy CI/CD integration
-  **Detailed Reports** - With references, hashes, and remediation info
-  **MCP Integration** - Use via AI assistants for interactive security scanning

## 📦 Quick Start

### As an MCP Server (NEW! 🌟)

Use RoguePkg interactively via AI assistants like Claude Desktop, Cursor, or Cline:

```bash
# Install dependencies
cd mcp
pip install -r requirements.txt

# Configure in your AI assistant's MCP settings
# See mcp/docs/SETUP.md for detailed instructions
```

**Chat Examples:**
- "is lodash@4.17.21 safe to use in my software project"
- "Check all repositories in my-org for malicious packages"
- "Check my public github project radioactivetobi/roguepkg for malicious dependecies"

📚 **[MCP Documentation](mcp/docs/README.md)** | **[Quick Start](mcp/docs/QUICKSTART.md)** | **[Setup Guide](mcp/docs/SETUP.md)** | **[Examples](mcp/examples/usage_examples.md)**

### As a GitHub Action (Recommended)

Add this workflow to your repository at `.github/workflows/roguepkg-all.yml`:

```yaml
name: Rogue Dependency Check

on:
  pull_request:
    paths:
      - 'package.json'
      - 'package-lock.json'
      - 'yarn.lock'

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: radioactivetobi/roguepkg@v1
        with:
          scan-path: '.'
          malware-only: 'true'
          fail-on-malware: 'true'
```

### As a Command-Line Tool

```bash
# Install dependencies
pip install requests

# Scan a single package
python roguepkg.py lodash@4.17.21

# Scan project dependencies (malware only - recommended)
python roguepkg.py --file package.json --batch --malware-only

# Scan directory recursively
python roguepkg.py --scan-dir . --malware-only

# Full vulnerability scan
python roguepkg.py --file package.json --batch
```

## GitHub Action Usage

### Basic Malware Detection (PR Check)

```yaml
name: Rogue Dependency Check

on:
  pull_request:
    paths:
      - '**/package*.json'
      - '**/yarn.lock'

jobs:
  malware-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Scan for Malware
        uses: radioactivetobi/roguepkg@v1
        with:
          scan-path: '.'
          malware-only: 'true'
          fail-on-malware: 'true'
```

### Full Vulnerability Scan

```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Full Security Scan
        uses: radioactivetobi/roguepkg@v1
        with:
          scan-path: '.'
          malware-only: 'false'
          fail-on-malware: 'true'
          fail-on-vulnerability: 'true'
```

### Comprehensive Security Workflow (Recommended)

All-in-one workflow with push, pull request, manual, and scheduled triggers:

```yaml
name: 'RoguePkg Security Scan'

on:
  push:
    branches: [main, master, develop]
    paths: ['**/package*.json', '**/yarn.lock']
  
  pull_request:
    branches: [main, master, develop]
    paths: ['**/package*.json', '**/yarn.lock']
  
  workflow_dispatch:
    inputs:
      scan-type:
        description: 'Type of scan'
        type: choice
        options: [malware-only, full-scan]
  
  schedule:
    - cron: '0 9 * * 1' # Weekly

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: radioactivetobi/roguepkg@v1
        with:
          malware-only: 'true'
          fail-on-malware: 'true'
```

**See `.github/workflows/roguepkg-all.yml` for the complete implementation with PR comments and issue creation.**

### Monorepo / Multiple Projects

```yaml
name: Scan Monorepo

on: [pull_request]

jobs:
  scan-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: radioactivetobi/roguepkg@v1
        with:
          scan-path: 'frontend/package.json'
          malware-only: 'true'
  
  scan-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: radioactivetobi/roguepkg@v1
        with:
          scan-path: 'backend/package.json'
          malware-only: 'true'
```

##  Action Inputs

| Input | Description | Default | Required |
|-------|-------------|---------|----------|
| `scan-path` | Path to scan (directory or file) | `.` | No |
| `malware-only` | Only report malware (faster) | `true` | No |
| `fail-on-malware` | Fail workflow if malware detected | `true` | No |
| `fail-on-vulnerability` | Fail on any vulnerability | `false` | No |

##  Action Outputs

| Output | Description |
|--------|-------------|
| `malware-found` | Number of packages with malware |
| `vulnerabilities-found` | Number of packages with vulnerabilities |
| `total-scanned` | Total packages scanned |
| `scan-status` | Overall status: `clean`, `malware-detected`, or `vulnerabilities-detected` |

### Using Outputs in Workflows

```yaml
- name: Run Scanner
  id: scan
  uses: radioactivetobi/roguepkg@v1

- name: Check Results
  run: |
    echo "Scanned: ${{ steps.scan.outputs.total-scanned }} packages"
    echo "Malware: ${{ steps.scan.outputs.malware-found }}"
    echo "Status: ${{ steps.scan.outputs.scan-status }}"
```

##  Example Workflows

We provide several ready-to-use workflow templates in `.github/workflows/`:

1. **`roguepkg-all.yml`**  - **Recommended!** Comprehensive workflow with:
   - ✅ Push and pull request triggers
   - ✅ Manual workflow dispatch with options
   - ✅ Scheduled weekly scans
   - ✅ PR comments and issue creation
   - ✅ Configurable scan types

2. **`roguepkg-pr.yml`** - Scan on pull requests with PR comments
3. **`roguepkg-push.yml`** - Scan on push to main branches
4. **`roguepkg-scheduled.yml`** - Weekly scans with issue creation
5. **`roguepkg-all.yml`** - Comprehensive scanning

Copy any of these to your repository's `.github/workflows/` folder.

##  Command-Line Usage

### Scan a Single Package

```bash
python roguepkg.py lodash@4.17.21
python roguepkg.py @ctrl/tinycolor@4.1.2
python roguepkg.py express
```

### Scan Project Dependencies

```bash
# Malware only (recommended for quick checks)
python roguepkg.py --file package.json --batch --malware-only

# Full scan with all vulnerabilities
python roguepkg.py --file package.json --batch

# Scan package-lock.json (includes transitive dependencies)
python roguepkg.py --file package-lock.json --batch --malware-only

# Scan yarn.lock
python roguepkg.py --file yarn.lock --batch --malware-only
```

### Scan Directory Recursively

```bash
# Scan current directory
python roguepkg.py --scan-dir . --malware-only

# Scan specific directory
python roguepkg.py --scan-dir /path/to/project --malware-only
```

### JSON Output

```bash
python roguepkg.py --file package.json --json
```

## Example Output

### Malware Detection

```
================================================================================
Package: @ctrl/tinycolor@4.1.2
================================================================================
Total Issues: 1 malware detected

                        🚨 MALWARE DETECTED                          
================================================================================

────────────────────────────────────────────────────────────────────────────────
🦠 MALWARE: MAL-2025-47141
   Severity: CRITICAL (MALWARE)

   Summary:
   Malicious code in @ctrl/tinycolor (npm)
   This package was compromised by the Shai-Hulud NPM worm.

   Affected Versions:
   - SEMVER: >= 4.1.1, last affected: 4.1.2
   
   References:
   - [ADVISORY] https://github.com/advisories/GHSA-qjqf-7j6f-82c4
   - [WEB] https://www.wiz.io/blog/shai-hulud-npm-supply-chain-attack
```


##  Integration Examples

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

if git diff --cached --name-only | grep -qE 'package.*\.json|yarn\.lock'; then
  echo "🔍 Checking for malware in dependencies..."
  python roguepkg.py --file package.json --batch --malware-only
  if [ $? -ne 0 ]; then
    echo "❌ Malware detected! Commit blocked."
    exit 1
  fi
fi
```

### npm Script

```json
{
  "scripts": {
    "security:check": "python roguepkg.py --file package.json --batch --malware-only",
    "security:full": "python roguepkg.py --file package.json --batch"
  }
}
```

### CI/CD (Generic)

```bash
# In your CI script
pip install requests
python roguepkg.py --file package.json --batch --malware-only

if [ $? -ne 0 ]; then
    echo "Security issues detected!"
    exit 1
fi
```

##  Future Roadmap

- 🐍 **PyPI Support** - Scan Python packages for vulnerabilities
- ☕ **Maven Support** - Scan Java dependencies
- 📦 **NuGet Support** - Scan .NET packages
- 🦀 **Cargo Support** - Scan Rust crates
- 💎 **RubyGems Support** - Scan Ruby gems

##  Supported File Formats

- ✅ `package.json` - Direct dependencies
- ✅ `package-lock.json` - All dependencies (npm v1, v2, v3)
- ✅ `yarn.lock` - All dependencies (Yarn v1)
- 🔍 Auto-detection with `--scan-dir`

## Testing

Test with known malicious packages (included in `test_files/`):

```bash
# Test malware detection
python roguepkg.py --file test_files/package.json --batch --malware-only

# Test directory scanning
python roguepkg.py --scan-dir test_files --malware-only
```

**WARNING**: Never run `npm install` in the test_files directory!

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Resources

- [OSV.dev Documentation](https://osv.dev/docs/)
- [OSV.dev Vulnerability Database](https://osv.dev)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [npm Security Best Practices](https://docs.npmjs.com/security-best-practices)

## License

MIT License - See [LICENSE](LICENSE) for details

## Credits

- Powered by [OSV.dev](https://osv.dev) (Google & Open Source Community)
- Created by [@radioactivetobi](https://github.com/radioactivetobi)
- Uses the free OSV.dev API
- Malware database from [GitHub Advisory Database](https://github.com/advisories)

## Support

If this action helps secure your project, please:
- ⭐ Star this repository at [github.com/radioactivetobi/roguepkg](https://github.com/radioactivetobi/roguepkg)
- 🐛 Report issues
- 💡 Suggest improvements for PyPI, Maven, and other ecosystems
- 📢 Share with others

---

<div align="center">

**Stay secure! 🛡️**

Made with ❤️ by [@radioactivetobi](https://github.com/radioactivetobi) - Jesus ❤️'s you

</div>

