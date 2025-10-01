# Quick Start Guide - NPM Malware Detection

Choose your preferred method:

## Option 1: GitHub Action (Easiest for CI/CD)

Add this file to your repo at `.github/workflows/roguepkg-all.yml`:

```yaml
name: Security Scan

on:
  pull_request:
    paths:
      - 'package*.json'
      - 'yarn.lock'

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

That's it! Every PR will now be scanned for malware.

## Option 2: Command-Line Tool

### Installation

```bash
pip install requests
```

No API key needed!

### Quickest Way to Check for Malware

```bash
# Scans all package.json, package-lock.json, and yarn.lock files recursively
python roguepkg.py --scan-dir . --malware-only
```

This will:
- ✅ Find all dependency files in current directory and subdirectories
- ✅ Check all direct AND transitive dependencies
- ✅ Only show malware (skips regular CVEs)
- ✅ Fast batch processing
- ✅ Skip node_modules automatically

### Other Common Usage

```bash
# Scan specific package.json
python roguepkg.py --file package.json --batch --malware-only

# Scan package-lock.json (includes ALL dependencies)
python roguepkg.py --file package-lock.json --batch --malware-only

# Scan specific directory
python roguepkg.py --scan-dir /path/to/project --malware-only

# Check single package
python roguepkg.py @ctrl/tinycolor@4.1.2
```

## What You'll See

### If malware is found:
```
🚨 MALWARE DETECTED (1 packages):
   - @ctrl/tinycolor@4.1.2

[Detailed information including:]
- MAL ID and GHSA ID
- SHA256 hashes
- Affected versions
- Security advisory links
- Multiple source confirmations
```

### If clean:
```
No malware detected
```

## Test the Scanner

```bash
# Test with known malware
python roguepkg.py --scan-dir test_files --malware-only

# Expected: Will detect @ctrl/tinycolor@4.1.2 and mongodb-ci@1.0.0
```

## File Support

| File Type | What It Checks |
|-----------|----------------|
| `package.json` | Direct dependencies only |
| `package-lock.json` | All dependencies (including nested) |
| `yarn.lock` | All dependencies (including nested) |
| `--scan-dir` | All of the above, recursively |

## Flags Explained

| Flag | What It Does |
|------|-------------|
| `--scan-dir .` | Scan current directory and subdirectories |
| `--malware-only` | Only show malware (skip regular vulnerabilities) |
| `--batch` | Faster batch processing (auto-enabled with --scan-dir) |
| `--file` | Scan specific file |

## Pro Tips

1. **Always use `--scan-dir`** for complete coverage
2. **Always use `--malware-only`** for fastest results
3. **Scan package-lock.json** to catch transitive dependencies
4. **Run before deploying** to production
5. **Add to CI/CD** pipeline for automatic checks

## CI/CD Integration

### GitHub Actions (Recommended)

Use the published action:

```yaml
- uses: radioactivetobi/roguepkg@v1
  with:
    malware-only: 'true'
```

### Generic CI/CD

```bash
pip install requests
python roguepkg.py --scan-dir . --malware-only
```

## What It Detects

- 🦠 Malicious packages (malware, backdoors, trojans)
- 🔍 Compromised legitimate packages
- 🎯 Supply chain attacks
- 🚨 Known attack campaigns (Shai-Hulud, etc.)

## What It Doesn't Show (with --malware-only)

- Regular CVEs and vulnerabilities
- Outdated packages
- License issues
- Code quality problems

(Remove `--malware-only` flag to see all vulnerabilities)

## Need Help?

See full documentation:
- `README_OSV.md` - Complete guide
- `test_files/README.md` - Test file details
- https://osv.dev/docs/ - OSV.dev API docs

