# 🛡️ RoguePkg MCP Server

Model Context Protocol (MCP) server for **RoguePkg** - A vulnerability and malware scanner for npm packages with GitHub integration.

## 🚀 Features

- **🦠 Malware Detection** - Identify compromised npm packages
- **⚠️ Vulnerability Scanning** - Find CVEs and security issues
- **🔗 GitHub Integration** - Scan repositories and organizations directly
- **📊 Bulk Organization Scanning** - Check all repos in an organization at once
- **💬 Chat Interface** - Use via AI assistants supporting MCP
- **🆓 Completely Free** - Powered by OSV.dev (no API key required)

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- GitHub Personal Access Token (optional, but recommended for private repos and rate limits)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/radioactivetobi/roguepkg.git
cd roguepkg

# Install dependencies
pip install requests

# Set GitHub token (optional but recommended)
export GITHUB_TOKEN="your_github_token_here"
```

### For Claude Desktop / Cline / Cursor

Add to your MCP settings file:

**For Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):
```json
{
  "mcpServers": {
    "roguepkg": {
      "command": "python",
      "args": ["/path/to/roguepkg/mcp_server.py"],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

**For Cline/Cursor** (`.vscode/settings.json` or workspace settings):
```json
{
  "mcp.servers": {
    "roguepkg": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

**For Unix/Linux**, use full paths and ensure Python is in your PATH.

## 🛠️ Available Tools

### 1. `scan_package`

Scan a single npm package for vulnerabilities and malware.

**Parameters:**
- `package` (required): Package specification (e.g., 'lodash@4.17.21' or 'lodash')
- `malware_only` (optional): Only report malware, skip regular vulnerabilities (default: false)

**Example:**
```
Can you check if lodash version 4.17.21 has any malware?
```

### 2. `scan_github_repository`

Scan a GitHub repository's dependencies for vulnerabilities and malware.

**Parameters:**
- `owner` (required): Repository owner (user or organization)
- `repository` (required): Repository name
- `malware_only` (optional): Only report malware (default: false)

**Example:**
```
Check if the react repository on facebook's GitHub has any vulnerable dependencies
```

### 3. `scan_github_organization`

Scan all repositories in a GitHub organization for vulnerabilities and malware.

**Parameters:**
- `organization` (required): Organization name
- `malware_only` (optional): Only report malware (default: true, recommended)
- `max_repos` (optional): Maximum number of repositories to scan (default: 50)

**Example:**
```
Check if the microsoft organization has any repositories with malicious npm packages
```

### 4. `scan_dependencies`

Scan a list of dependencies for vulnerabilities and malware.

**Parameters:**
- `dependencies` (required): Dictionary of package names to versions
- `malware_only` (optional): Only report malware (default: false)

**Example:**
```
Check these packages for malware: {"lodash": "4.17.21", "express": "4.18.2"}
```

## 💬 Usage Examples

### Via Chat Interface

Once configured, you can use natural language to interact with the MCP server:

**Single Package Check:**
> "Is the package `@ctrl/tinycolor` version 4.1.2 safe?"

**Repository Scan:**
> "Scan the repository `facebook/react` for any malicious dependencies"

**Organization-Wide Scan:**
> "Check if the `vercel` organization has any repositories with npm malware"

**Bulk Dependency Check:**
> "I have these dependencies: lodash@4.17.21, express@4.18.2, react@18.2.0. Are they safe?"

## 🔑 GitHub Token Setup

To use GitHub integration features, you need a Personal Access Token:

1. Go to GitHub Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "RoguePkg MCP")
4. Select scopes:
   - `repo` (for private repos)
   - `read:org` (for organization scanning)
5. Generate and copy the token
6. Set it as an environment variable:
   ```bash
   export GITHUB_TOKEN="ghp_your_token_here"
   ```

**Note:** Without a token, you can still:
- Scan individual packages
- Scan public repositories (with rate limits)
- Use the scan_dependencies tool

## 🏗️ Architecture

The MCP server consists of:

1. **OSVScanner** - Core vulnerability scanning using OSV.dev API
2. **GitHubAPI** - Fetches repository files and organization data
3. **RoguePkgMCPServer** - MCP protocol implementation
4. **Tool Handlers** - Process chat commands and return results

```
┌─────────────────┐
│  Chat Interface │ (Claude, Cursor, etc.)
└────────┬────────┘
         │ MCP Protocol
         ▼
┌─────────────────┐
│  MCP Server     │
└────────┬────────┘
         │
    ┌────┴─────┐
    ▼          ▼
┌────────┐  ┌──────────┐
│ OSV.dev│  │ GitHub   │
│  API   │  │   API    │
└────────┘  └──────────┘
```

## 🔍 Output Format

All tools return structured JSON with:

```json
{
  "status": "clean | malware-detected | vulnerabilities-detected | error",
  "malware_count": 0,
  "vulnerability_count": 0,
  "total_scanned": 10,
  "malware_packages": [
    {
      "package": "package-name@version",
      "malware_count": 1,
      "issues": [
        {
          "id": "MAL-2025-XXXXX",
          "type": "malware",
          "severity": "CRITICAL (MALWARE)",
          "summary": "Description of the malware",
          "published": "2025-01-01T00:00:00Z",
          "references": ["https://..."],
          "aliases": ["CVE-XXXX-XXXXX"]
        }
      ]
    }
  ],
  "vulnerable_packages": [...],
  "affected_repositories": [...]
}
```

## 🚦 Best Practices

### For Individual Users
- Scan packages before adding them to your project
- Run organization scans weekly for security monitoring
- Use `malware_only=true` for faster scans

### For Organizations
- Set up scheduled organization scans
- Use GitHub tokens with appropriate permissions
- Monitor affected repositories regularly
- Limit `max_repos` for large organizations

### Rate Limits
- OSV.dev: No rate limits (free)
- GitHub API: 
  - Unauthenticated: 60 requests/hour
  - Authenticated: 5,000 requests/hour
  - Use tokens for organization scanning

## 🐛 Troubleshooting

### "GitHub integration not initialized"
- Ensure `GITHUB_TOKEN` is set in your environment
- Restart the MCP server after setting the token

### "No dependencies found"
- Repository may not have `package.json`
- Repository may be private (need token with `repo` scope)
- Try different branch (main vs master)

### "No repositories found for organization"
- Check organization name spelling
- Ensure token has `read:org` permission
- Organization may have no public repositories

### Rate Limit Errors
- Use a GitHub token for higher limits
- Reduce `max_repos` for organization scans
- Wait before retrying

## 📚 Integration with Official GitHub MCP

This MCP server is designed to complement the official GitHub MCP:

- **GitHub MCP**: Repository management, issues, PRs, code search
- **RoguePkg MCP**: Security scanning, vulnerability detection, malware checking

They can be used together:
1. Use GitHub MCP to find repositories
2. Use RoguePkg MCP to scan them for vulnerabilities

Example workflow:
```
1. "List all repositories in the acme-corp organization" (GitHub MCP)
2. "Scan the acme-corp organization for malicious packages" (RoguePkg MCP)
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📜 License

MIT License - See [LICENSE](LICENSE) for details

## 🙏 Credits

- Powered by [OSV.dev](https://osv.dev) (Google & Open Source Community)
- Created by [@radioactivetobi](https://github.com/radioactivetobi)
- Built on [Model Context Protocol](https://modelcontextprotocol.io/)

## ⭐ Support

If this MCP server helps secure your projects:
- ⭐ Star the repository
- 🐛 Report issues
- 💡 Suggest improvements
- 📢 Share with others

---

**Stay secure! 🛡️**

Made with ❤️ by [@radioactivetobi](https://github.com/radioactivetobi)

