# RoguePkg MCP Server - Setup Guide

Complete setup instructions for integrating RoguePkg with AI assistants via Model Context Protocol (MCP).

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- GitHub Personal Access Token (optional but recommended)

## Quick Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements-mcp.txt
```

Or manually:
```bash
pip install requests
```

### Step 2: Get GitHub Token (Optional)

GitHub integration requires a Personal Access Token for:
- Scanning private repositories
- Higher rate limits (5,000 vs 60 requests/hour)
- Organization scanning

**Create a token:**

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name it "RoguePkg MCP"
4. Select scopes:
   - ✅ `repo` (for private repositories)
   - ✅ `read:org` (for organization scanning)
5. Generate and copy the token
6. Save it securely (you won't see it again)

### Step 3: Configure Your AI Assistant

Choose your AI assistant and follow the corresponding setup:

---

## Setup for Claude Desktop

**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)  
**Location:** `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

```json
{
  "mcpServers": {
    "roguepkg": {
      "command": "python",
      "args": ["/full/path/to/rogue-pkg/mcp_server.py"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

**Important:** Use full absolute paths!

**Restart Claude Desktop** after adding this configuration.

---

## Setup for Cursor / VSCode with Cline

**Location:** `.vscode/settings.json` in your workspace or global settings

```json
{
  "mcp.servers": {
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

Or create a workspace file:

**Location:** `.cursor/mcp.json` or `mcp.json` in project root

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

**Restart Cursor/VSCode** after adding this configuration.

---

## Setup for Continue.dev

**Location:** `~/.continue/config.json`

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

**Restart Continue** after adding this configuration.

---

## Setup for Generic MCP Client

For other MCP clients, use this standard configuration:

```json
{
  "command": "python",
  "args": ["mcp_server.py"],
  "env": {
    "GITHUB_TOKEN": "your_token_here"
  }
}
```

---

## Step 4: Test the Setup

### Quick Test in Your AI Assistant

Try these commands in your chat:

```
1. "List the available roguepkg tools"
2. "Check if lodash@4.17.21 has any vulnerabilities"
3. "Scan the facebook/react repository for malware"
```

### Manual Test

Run the test script:

```bash
cd /path/to/rogue-pkg
python examples/test_mcp_tools.py
```

This will test all MCP tools and verify they're working correctly.

---

## Troubleshooting

### "Command not found" or "Python not found"

**Solution:** Use full path to Python:

```json
{
  "command": "/usr/bin/python3",  // macOS/Linux
  "command": "C:\\Python311\\python.exe",  // Windows
  ...
}
```

Find Python path:
```bash
# macOS/Linux
which python3

# Windows
where python
```

---

### "Module not found: requests"

**Solution:** Install in the correct Python environment:

```bash
# If using python3
python3 -m pip install requests

# If using specific Python version
/usr/bin/python3 -m pip install requests
```

---

### "GitHub integration not initialized"

**Symptoms:** 
- Can scan packages but GitHub features don't work
- Error messages about missing GitHub token

**Solution:**
1. Verify GITHUB_TOKEN is in your MCP config
2. Token has correct permissions (`repo`, `read:org`)
3. Token is not expired
4. Restart your AI assistant after adding token

---

### "No dependencies found in repository"

**Possible causes:**
1. Repository has no `package.json`
2. Repository is private (need token with `repo` scope)
3. Branch name is wrong (try `main` vs `master`)
4. Repository exists but in different location

**Solution:**
- Verify repository exists: `https://github.com/owner/repo`
- Check if it has `package.json` in root
- Add token if repository is private
- Specify correct branch if needed

---

### Rate Limit Errors

**Symptoms:**
- "API rate limit exceeded"
- Slow responses from GitHub

**Solution:**
1. Add GITHUB_TOKEN to configuration (5000 req/hr vs 60)
2. Reduce `max_repos` in organization scans
3. Wait before retrying
4. For large scans, run in batches

---

### MCP Server Not Showing Up

**Claude Desktop:**
1. Check logs: `~/Library/Logs/Claude/` (macOS)
2. Verify JSON syntax in config file
3. Use absolute paths, not relative
4. Restart Claude Desktop completely

**Cursor/VSCode:**
1. Check Output panel → MCP Servers
2. Verify JSON syntax
3. Reload window (Cmd/Ctrl + R)
4. Check extension logs

---

### Permission Denied Errors

**macOS/Linux:**
```bash
chmod +x mcp_server.py
```

**Windows:**
- Run terminal as Administrator
- Check Python is in PATH

---

## Advanced Configuration

### Using a Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install requests

# Use venv Python in MCP config
{
  "command": "/path/to/rogue-pkg/venv/bin/python",
  ...
}
```

---

### Multiple GitHub Tokens

If you need different tokens for different organizations:

```json
{
  "mcpServers": {
    "roguepkg-personal": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "GITHUB_TOKEN": "personal_token"
      }
    },
    "roguepkg-work": {
      "command": "python", 
      "args": ["mcp_server.py"],
      "env": {
        "GITHUB_TOKEN": "work_token"
      }
    }
  }
}
```

---

### Environment Variables from File

Instead of hardcoding tokens:

**Create `.env` file:**
```bash
GITHUB_TOKEN=ghp_your_token_here
```

**Update MCP config:**
```json
{
  "env": {
    "GITHUB_TOKEN": "${GITHUB_TOKEN}"
  }
}
```

Then load environment before starting:
```bash
export $(cat .env | xargs)
```

---

## Verification Checklist

After setup, verify:

- ✅ Python is installed and accessible
- ✅ `requests` package is installed
- ✅ MCP config file has correct syntax
- ✅ Paths to `mcp_server.py` are absolute
- ✅ GITHUB_TOKEN is set (if using GitHub features)
- ✅ Token has correct permissions
- ✅ AI assistant has been restarted
- ✅ Test commands work in chat

---

## Getting Help

If you're still having issues:

1. **Check logs** for error messages
2. **Run test script** (`python examples/test_mcp_tools.py`)
3. **Verify environment** (Python version, dependencies)
4. **Check GitHub token** (permissions, expiration)
5. **Open an issue** at https://github.com/radioactivetobi/roguepkg/issues

Include in your issue:
- OS and version
- Python version
- AI assistant being used
- Error messages from logs
- MCP configuration (remove token!)

---

## Next Steps

Once setup is complete:

1. **Read examples:** See `examples/mcp_examples.md` for usage examples
2. **Scan a repository:** Try scanning one of your repositories
3. **Set up monitoring:** Schedule regular organization scans
4. **Integrate with workflows:** Combine with GitHub MCP for advanced workflows

---

**Happy scanning! 🛡️**

