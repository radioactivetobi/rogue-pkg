# RoguePkg MCP Integration Guide

Complete guide for integrating RoguePkg MCP Server with AI assistants and the official GitHub MCP.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Integration Scenarios](#integration-scenarios)
4. [GitHub MCP Synergy](#github-mcp-synergy)
5. [Organization Scanning](#organization-scanning)
6. [Best Practices](#best-practices)
7. [Advanced Workflows](#advanced-workflows)

---

## Overview

The RoguePkg MCP Server provides security scanning capabilities for npm packages through the Model Context Protocol. It integrates seamlessly with:

- **AI Assistants**: Claude Desktop, Cursor, Cline, Continue.dev, and more
- **GitHub MCP**: Official GitHub MCP for repository management
- **GitHub API**: Direct repository and organization scanning
- **OSV.dev**: Free vulnerability database

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      AI Assistant                            │
│              (Claude, Cursor, Cline, etc.)                   │
└────────────────────┬──────────────────┬─────────────────────┘
                     │                  │
           ┌─────────▼─────────┐       │
           │   GitHub MCP      │       │ Model Context Protocol
           │   (Official)      │       │
           └─────────┬─────────┘       │
                     │                  │
                     │         ┌────────▼─────────┐
                     │         │  RoguePkg MCP    │
                     │         │    Server        │
                     │         └────────┬─────────┘
                     │                  │
                     │         ┌────────▼─────────┐
                     │         │   OSV Scanner    │
                     │         └────────┬─────────┘
                     │                  │
              ┌──────▼──────┐    ┌─────▼──────┐
              │ GitHub API  │    │  OSV.dev   │
              │             │    │    API     │
              └─────────────┘    └────────────┘
```

---

## Integration Scenarios

### Scenario 1: Single Package Check (No GitHub Required)

**Use Case:** Check if a package is safe before installing

**Tools Used:**
- `scan_package` (RoguePkg MCP)

**Example:**
```
User: "Is lodash@4.17.21 safe to use?"
AI: Uses scan_package tool
Response: "Yes, lodash@4.17.21 is clean. No malware detected."
```

**Benefits:**
- No GitHub token needed
- Fast response
- Works offline (for cached results)

---

### Scenario 2: Repository Security Audit (GitHub Integration)

**Use Case:** Check if a repository has vulnerable dependencies

**Tools Used:**
- `scan_github_repository` (RoguePkg MCP)

**Example:**
```
User: "Scan facebook/react for security issues"
AI: Uses scan_github_repository
Response: "Scanned 45 dependencies. No critical issues found."
```

**Requirements:**
- GITHUB_TOKEN (recommended)
- Repository must have package.json

---

### Scenario 3: Organization-Wide Security Scan

**Use Case:** Audit all repositories in an organization

**Tools Used:**
- `scan_github_organization` (RoguePkg MCP)

**Example:**
```
User: "Check all repositories in my-company org for malware"
AI: Uses scan_github_organization
Response: "Scanned 50 repos. Found malware in 2 repositories."
```

**Requirements:**
- GITHUB_TOKEN with `read:org` permission
- Organization must be accessible

---

### Scenario 4: Combined GitHub + RoguePkg Workflow

**Use Case:** Find and scan repositories based on criteria

**Tools Used:**
- GitHub MCP (list repositories)
- RoguePkg MCP (scan them)

**Example:**
```
User: "Find all JavaScript repos in my-org and scan them for malware"
AI Workflow:
1. Uses GitHub MCP: list_repositories(org="my-org", language="JavaScript")
2. Uses RoguePkg MCP: scan_github_repository for each repo
Response: "Found 10 JavaScript repos. 8 are clean, 2 have issues..."
```

**Requirements:**
- Both GitHub MCP and RoguePkg MCP configured
- GITHUB_TOKEN for both

---

## GitHub MCP Synergy

The RoguePkg MCP complements the official GitHub MCP:

### GitHub MCP Provides:
- Repository listing and search
- File operations
- Issue and PR management
- Code search
- Repository metadata

### RoguePkg MCP Provides:
- Security scanning
- Vulnerability detection
- Malware identification
- Dependency analysis

### Combined Power:

#### Example 1: Security-Focused PR Review

```
User: "Review the dependencies changed in PR #123 of my-org/my-repo"

Workflow:
1. GitHub MCP: Get PR diff
2. GitHub MCP: Extract changed dependencies from package.json
3. RoguePkg MCP: Scan each changed dependency
4. AI: Synthesize security analysis

Response: "PR adds 3 new dependencies. 2 are clean, 
          1 (package-x) has a high severity vulnerability..."
```

#### Example 2: Organization Repository Discovery and Scan

```
User: "Find all repositories in my-company that use React and check for security issues"

Workflow:
1. GitHub MCP: Search repositories with "react" dependency
2. RoguePkg MCP: Scan each repository
3. AI: Compile security report

Response: "Found 15 React repositories. 
          12 are secure, 3 have vulnerabilities..."
```

#### Example 3: Automated Security Issue Creation

```
User: "Scan my-org/my-repo and create issues for any vulnerabilities found"

Workflow:
1. RoguePkg MCP: Scan repository
2. GitHub MCP: Create issue for each vulnerability
3. AI: Format issue with details

Result: Issues created with vulnerability details, 
        references, and remediation steps
```

---

## Organization Scanning

### GitHub Dependency Insights Integration

While GitHub provides dependency insights, the RoguePkg MCP offers:

**Advantages:**
- Real-time scanning without GitHub Advanced Security
- Works with public and private repositories
- No GitHub subscription required
- Integrates OSV.dev's comprehensive malware database
- Immediate results via chat interface

**Limitations:**
- Rate limits (mitigated with GITHUB_TOKEN)
- Must scan repos individually (batch processing available)

### Bulk Organization Scanning

#### Method 1: Direct Organization Scan (Recommended)

```python
# Via AI Assistant
"Scan the first 50 repositories in acme-corp for malware"

# Uses tool
scan_github_organization(
    organization="acme-corp",
    malware_only=True,
    max_repos=50
)
```

**Benefits:**
- One command
- Aggregated results
- Cross-repository vulnerability tracking

#### Method 2: Repository-by-Repository

```python
# Via GitHub MCP + RoguePkg MCP
"List all repos in acme-corp and scan each one"

Workflow:
1. List repos with GitHub MCP
2. For each repo:
   - Scan with RoguePkg MCP
   - Collect results
3. Generate comprehensive report
```

**Benefits:**
- More detailed per-repo results
- Can filter by language/framework
- Parallel scanning possible

#### Method 3: Dependency Graph Analysis

```python
# Future feature - using GitHub's dependency graph API
scan_github_org(
    organization="acme-corp",
    use_dependency_graph=True
)
```

**Note:** Currently requires GitHub Advanced Security for full dependency graph API access.

---

## Best Practices

### 1. Token Management

**Do:**
- Use dedicated tokens for MCP servers
- Set minimal required permissions
- Rotate tokens regularly
- Use different tokens for personal and work

**Don't:**
- Share tokens between services
- Commit tokens to version control
- Use admin tokens for scanning

### 2. Scanning Strategy

**For Individual Developers:**
```
- Scan packages before installing (scan_package)
- Check repos on clone/pull (scan_github_repository)
- Weekly personal repo audits
```

**For Teams:**
```
- Organization scans weekly (scan_github_organization)
- PR-triggered scans (via CI/CD)
- Critical repos: daily scans
- All repos: weekly scans
```

**For Organizations:**
```
- Scheduled organization-wide scans
- New repository onboarding scans
- Pre-release security checks
- Quarterly security audits
```

### 3. Performance Optimization

**Rate Limits:**
- Use GITHUB_TOKEN (5000 req/hr vs 60)
- Batch organization scans during off-peak hours
- Set `max_repos` appropriately
- Use `malware_only=true` for faster scans

**Caching:**
- OSV.dev results are cached in session
- Reuse server instance for multiple scans
- Schedule scans to avoid redundant checks

### 4. Alert Fatigue Prevention

**Prioritization:**
1. Malware (immediate action)
2. Critical vulnerabilities (urgent)
3. High vulnerabilities (important)
4. Medium/Low (track)

**Filtering:**
- Use `malware_only=true` for noise reduction
- Focus on direct dependencies first
- Set severity thresholds
- Group similar vulnerabilities

### 5. Remediation Workflow

```
1. Detection: RoguePkg MCP identifies issue
2. Triage: Review severity and impact
3. Research: Check references and CVE details
4. Fix: Update dependency or find alternative
5. Verify: Re-scan to confirm fix
6. Document: Update security log
```

---

## Advanced Workflows

### Workflow 1: Security Gate for Dependency Updates

**Scenario:** Team wants to add a new dependency

```
Process:
1. Developer: "Check if new-package@1.0.0 is safe"
2. AI: Scans package with RoguePkg MCP
3. If clean → Approve
4. If issues → Report details and suggest alternatives
```

### Workflow 2: Continuous Security Monitoring

**Scenario:** Weekly security checks for organization

```
Schedule (via cron/GitHub Actions):
Monday 9 AM:
1. Scan organization (scan_github_organization)
2. Compare with previous week's results
3. Generate delta report
4. Create issues for new vulnerabilities
5. Post summary to Slack/Teams
```

### Workflow 3: Supply Chain Attack Detection

**Scenario:** Monitor for newly discovered malware

```
Daily Process:
1. Scan all production dependencies
2. Flag any new malware detections
3. Immediate alert if malware found
4. Automated rollback if possible
5. Incident response activation
```

### Workflow 4: Compliance Reporting

**Scenario:** Generate security compliance reports

```
Monthly:
1. Full organization scan
2. Export results to JSON
3. Generate compliance report:
   - Total packages scanned
   - Vulnerabilities by severity
   - Remediation timeline
   - Trend analysis
4. Submit to security team
```

### Workflow 5: Pre-Deployment Security Check

**Scenario:** Verify dependencies before production deployment

```
CI/CD Pipeline:
1. Build stage: Install dependencies
2. Security stage:
   - Extract dependencies
   - Scan with RoguePkg MCP
   - Fail if critical issues
3. Deploy stage: Only if security passed
```

---

## Configuration Examples

### Multi-Server Setup

For organizations using multiple MCP servers:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "roguepkg": {
      "command": "python",
      "args": ["/path/to/roguepkg/mcp_server.py"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

### Separate Tokens for Different Purposes

```json
{
  "mcpServers": {
    "github-admin": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_ADMIN_TOKEN}"
      }
    },
    "roguepkg-readonly": {
      "command": "python",
      "args": ["/path/to/roguepkg/mcp_server.py"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_READONLY_TOKEN}"
      }
    }
  }
}
```

---

## Troubleshooting Integration Issues

### Issue: Tools Not Showing Up

**Check:**
1. Both servers are in MCP config
2. Correct command paths
3. Tokens are set
4. Restart AI assistant

### Issue: GitHub MCP Works, RoguePkg Doesn't

**Check:**
1. Python is accessible
2. Dependencies installed (`requests`)
3. `roguepkg.py` is in same directory
4. Check logs for Python errors

### Issue: Rate Limit Errors

**Solutions:**
1. Add GITHUB_TOKEN
2. Reduce scan frequency
3. Lower `max_repos` setting
4. Use organization scan instead of individual scans

---

## Future Enhancements

Planned features:

1. **Native Dependency Graph Support**
   - Use GitHub's dependency graph API
   - Faster organization scans
   - Better transitive dependency tracking

2. **Cache Layer**
   - Persistent caching across sessions
   - Reduced API calls
   - Faster repeat scans

3. **Webhook Integration**
   - Real-time vulnerability alerts
   - Automated PR creation
   - Slack/Teams notifications

4. **Multi-Ecosystem Support**
   - PyPI (Python)
   - Maven (Java)
   - NuGet (.NET)
   - Cargo (Rust)

---

## Resources

- [RoguePkg Documentation](README.md)
- [MCP Setup Guide](SETUP_MCP.md)
- [Usage Examples](examples/mcp_examples.md)
- [Official GitHub MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [OSV.dev](https://osv.dev)

---

**Built with ❤️ for secure software development**

