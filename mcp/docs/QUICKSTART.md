# 🚀 RoguePkg MCP Server - Quick Start

Get up and running with RoguePkg MCP Server in 5 minutes!

## What You'll Get

After setup, you can ask your AI assistant:
- ✅ "Check if lodash@4.17.21 has any malware"
- ✅ "Scan the facebook/react repository for vulnerabilities"
- ✅ "Is my organization's code using any malicious packages?"

## Prerequisites

- ✅ Python 3.8+ installed
- ✅ An AI assistant that supports MCP (Claude Desktop, Cursor, Cline, etc.)
- ⚠️ GitHub Personal Access Token (optional but recommended)

## 3-Step Setup

### Step 1: Install Dependencies (30 seconds)

```bash
cd /path/to/rogue-pkg
pip install requests
```

That's it! Just one dependency.

---

### Step 2: Get GitHub Token (2 minutes, optional)

**Why?** Higher rate limits and private repo access.

1. Visit: https://github.com/settings/tokens/new
2. Name: "RoguePkg MCP"
3. Select scopes:
   - [x] `repo` (for private repos)
   - [x] `read:org` (for org scanning)
4. Click "Generate token"
5. Copy the token (starts with `ghp_`)

**Save it somewhere safe!** You won't see it again.

---

### Step 3: Configure Your AI Assistant (2 minutes)

#### For Claude Desktop

**File:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)  
**File:** `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

Add this:
```json
{
  "mcpServers": {
    "roguepkg": {
      "command": "python",
      "args": ["/FULL/PATH/TO/rogue-pkg/mcp_server.py"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

**⚠️ Important:** Use the FULL absolute path!

Find it:
```bash
# macOS/Linux
pwd

# Windows (in WSL)
/mnt/c/Users/your-name/Downloads/rogue-pkg
```

---

#### For Cursor / VSCode + Cline

**File:** Create `.cursor/mcp.json` in your project or add to settings

```json
{
  "mcpServers": {
    "roguepkg": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

---

#### For Continue.dev

**File:** `~/.continue/config.json`

```json
{
  "mcp": {
    "servers": {
      "roguepkg": {
        "command": "python",
        "args": ["/path/to/rogue-pkg/mcp_server.py"],
        "env": {
          "GITHUB_TOKEN": "ghp_your_token_here"
        }
      }
    }
  }
}
```

---

### ✅ Restart Your AI Assistant

**Important!** You must restart for changes to take effect.

---

## Verify It's Working

### Option 1: Chat Test (Easiest)

Open your AI assistant and try:

```
"Check if lodash version 4.17.21 has any vulnerabilities"
```

You should get a response like:
```
"Let me scan lodash@4.17.21... 
 Package is clean. No malware or vulnerabilities detected. ✅"
```

---

### Option 2: Verification Script

```bash
cd /path/to/rogue-pkg
python verify_setup.py
```

You should see:
```
✅ Python version
✅ requests package
✅ roguepkg.py module
✅ mcp_server.py
✅ GITHUB_TOKEN
✅ OSV.dev API connection
✅ GitHub API connection
✅ Basic package scan

🎉 Your RoguePkg MCP server is ready to use!
```

---

## Try It Out!

### Example 1: Check a Single Package
```
You: "Is express@4.18.2 safe to use?"

AI: "Let me check express@4.18.2...
     Package is clean ✅
     No malware or vulnerabilities detected."
```

### Example 2: Scan a Repository
```
You: "Scan the vercel/next.js repository for security issues"

AI: "Scanning vercel/next.js...
     Found 123 dependencies
     All packages are clean ✅
     No critical issues detected."
```

### Example 3: Check Your Organization
```
You: "Check if any repos in my-company have malicious packages"

AI: "Scanning my-company organization...
     Scanned 25 repositories
     Found 2 repositories with issues:
     - my-company/project-a: 1 malware package
     - my-company/project-b: 2 vulnerable packages"
```

### Example 4: Check Before Installing
```
You: "I want to install chalk@4.1.2. Is it safe?"

AI: "Let me verify chalk@4.1.2...
     Package is clean ✅
     No known security issues
     Safe to install!"
```

---

## Common Commands

### Security Checks
- "Check if [package]@[version] has any malware"
- "Is [package] safe to use?"
- "Scan [package] for vulnerabilities"

### Repository Scanning
- "Scan [owner]/[repo] for security issues"
- "Check [owner]/[repo] for malicious dependencies"
- "Are there any vulnerabilities in [owner]/[repo]?"

### Organization Audits
- "Scan [org] organization for malware"
- "Check all repos in [org] for security issues"
- "Which repositories in [org] have vulnerabilities?"

### Bulk Checks
- "Check these packages: lodash, express, axios"
- "Are these dependencies safe: [list]"
- "Scan my dependencies for malware"

---

## Troubleshooting

### "Tools not showing up"

**Fix:**
1. Verify JSON syntax in config file
2. Use FULL absolute paths
3. Restart AI assistant completely
4. Check logs for errors

### "Python not found"

**Fix:** Use full path to Python:
```json
"command": "/usr/bin/python3"  // Find with: which python3
```

### "Module not found: requests"

**Fix:**
```bash
python -m pip install requests
```

### "GitHub integration not initialized"

**Fix:**
1. Add GITHUB_TOKEN to config
2. Verify token is valid
3. Restart AI assistant

---

## What's Next?

### Learn More
- 📖 **[Full Documentation](README_MCP.md)** - Complete feature guide
- 🛠️ **[Setup Guide](SETUP_MCP.md)** - Detailed configuration
- 💡 **[Examples](examples/mcp_examples.md)** - More usage examples
- 🔗 **[Integration Guide](MCP_INTEGRATION_GUIDE.md)** - Advanced workflows

### Advanced Features
- Scan entire organizations
- Bulk dependency checking
- Integration with GitHub MCP
- Automated security monitoring

### Get Help
- Run `python verify_setup.py` for diagnostics
- Check [SETUP_MCP.md](SETUP_MCP.md) for detailed troubleshooting
- Open issue: https://github.com/radioactivetobi/roguepkg/issues

---

## Benefits Over CLI

### Before (CLI)
```bash
$ python roguepkg.py --file package.json --batch
[Scroll through long output...]
[Copy/paste vulnerabilities...]
[Switch between terminal and browser...]
```

### After (MCP)
```
You: "Is my project safe?"
AI: "All 45 dependencies are clean ✅"

You: "What about react?"
AI: "react@18.2.0 is secure ✅"
```

**Benefits:**
- ✅ Natural language interface
- ✅ Stay in your editor
- ✅ AI-synthesized reports
- ✅ Interactive follow-up questions
- ✅ Combined with other tools (GitHub MCP)

---

## Success Checklist

- [ ] Python 3.8+ installed
- [ ] `requests` package installed
- [ ] GitHub token created (optional)
- [ ] MCP config file updated
- [ ] Full paths used in config
- [ ] AI assistant restarted
- [ ] Test command works
- [ ] Can scan packages
- [ ] Can scan repositories (with token)

---

## You're Ready! 🎉

Start securing your dependencies with natural language:

```
"Check if my project has any malicious packages"
"Scan our organization for security issues"
"Is this package safe to install?"
```

**Happy scanning! 🛡️**

---

Need help? See [SETUP_MCP.md](SETUP_MCP.md) for detailed instructions.

