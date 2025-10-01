# 🚀 Getting Started with RoguePkg

Quick guide to publish your GitHub Action to the marketplace.

## 📦 What You Have

Your repository now includes everything needed for a GitHub Action:

- ✅ `action.yml` - GitHub Action definition
- ✅ `rogue_dep.py` - Scanner script  
- ✅ `README.md` - Complete documentation
- ✅ `QUICK_START.md` - Quick reference
- ✅ `LICENSE` - MIT License
- ✅ `.github/workflows/` - Example workflows for users

## 🎯 Publishing Steps

### 1. Push to GitHub

```bash
git add .
git commit -m "Initial release of RoguePkg"
git push origin main
```

### 2. Create Release

```bash
# Create and push version tag
git tag -a v1.0.0 -m "v1.0.0 - Initial Release"
git push origin v1.0.0

# Create v1 tag for auto-updates
git tag -a v1 -m "v1.0.0"
git push origin v1
```

### 3. Publish to Marketplace

1. Go to: `https://github.com/radioactivetobi/roguepkg/releases/new`
2. Select tag: `v1.0.0`
3. Title: `v1.0.0 - Initial Release`
4. Description:
```markdown
## 🎉 Initial Release

Detect malicious npm packages using OSV.dev - completely free!

### Features
- 🦠 Malware detection for npm packages
- ⚠️  Vulnerability scanning with CVE tracking
- 🚀 GitHub Action for easy CI/CD integration
- 🆓 No API key required

### Usage
```yaml
- uses: radioactivetobi/roguepkg@v1
  with:
    malware-only: 'true'
```

See [README](https://github.com/radioactivetobi/roguepkg#readme) for full documentation.
```
5. **✅ Check "Publish this action to the GitHub Marketplace"**
6. Select category: **"Security"**
7. Click **"Publish release"**

### 4. Test It

We provide a comprehensive workflow template that handles multiple triggers. Copy `.github/workflows/security-scan.yml` to your repository, or create a simple test:

```yaml
name: Test RoguePkg
on: [push, pull_request, workflow_dispatch]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: radioactivetobi/roguepkg@v1
        with:
          malware-only: 'true'
```

**Recommended:** Use the comprehensive `security-scan.yml` workflow that includes:
- Push, pull request, manual, and scheduled triggers
- PR comments with scan results
- Automatic issue creation for malware
- Configurable scan types

## 🔮 Future Development

Ready to add support for other ecosystems? The OSV.dev API supports:

- 🐍 **PyPI** (Python) - ecosystem: "PyPI"
- ☕ **Maven** (Java) - ecosystem: "Maven"  
- 📦 **NuGet** (.NET) - ecosystem: "NuGet"
- 🦀 **Cargo** (Rust) - ecosystem: "crates.io"
- 💎 **RubyGems** (Ruby) - ecosystem: "RubyGems"

Just update `rogue_dep.py` to support multiple ecosystems!

## 📚 Resources

- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [OSV.dev API Docs](https://osv.dev/docs/)
- [GitHub Actions Publishing Guide](https://docs.github.com/en/actions/creating-actions/publishing-actions-in-github-marketplace)

## 🎊 After Publishing

Your action will be available at:
- Marketplace: `https://github.com/marketplace/actions/roguepkg-malware-vulnerability-scanner`
- Direct use: `radioactivetobi/roguepkg@v1`

Share it with the community! 🚀

