# RoguePkg MCP Server - Usage Examples

## Natural Language Queries

Once the MCP server is configured with your AI assistant (Claude, Cursor, Cline, etc.), you can use natural language to interact with it.

## Example Conversations

### 1. Single Package Check

**User:** Is the package lodash@4.17.21 safe to use?

**AI uses:** `scan_package` tool with `{"package": "lodash@4.17.21"}`

**Response:** Package lodash@4.17.21 is clean. No malware or critical vulnerabilities detected.

---

### 2. Check Latest Version

**User:** Check if the latest version of express has any vulnerabilities

**AI uses:** `scan_package` tool with `{"package": "express"}`

**Response:** Found 2 vulnerabilities in express (latest version)...

---

### 3. Repository Scan

**User:** Can you check if the facebook/react repository has any malicious dependencies?

**AI uses:** `scan_github_repository` tool with `{"owner": "facebook", "repository": "react", "malware_only": true}`

**Response:** Scanned 45 dependencies in facebook/react. No malware detected. ✅

---

### 4. Repository with Full Scan

**User:** Do a full security scan of vercel/next.js including all vulnerabilities

**AI uses:** `scan_github_repository` tool with `{"owner": "vercel", "repository": "next.js", "malware_only": false}`

**Response:** Scanned 123 dependencies. Found 3 packages with vulnerabilities (1 critical)...

---

### 5. Organization-Wide Scan

**User:** Check if any repositories in the microsoft organization have npm malware

**AI uses:** `scan_github_organization` tool with `{"organization": "microsoft", "malware_only": true, "max_repos": 50}`

**Response:** Scanned 50 repositories across microsoft organization. Found malware in 2 repositories...

---

### 6. Organization with Repository Details

**User:** Scan the first 20 repositories in the airbnb organization and tell me which ones are affected

**AI uses:** `scan_github_organization` tool with `{"organization": "airbnb", "malware_only": true, "max_repos": 20}`

**Response:** 
- Scanned 20 repositories
- 3 repositories have malicious dependencies:
  1. airbnb/project-a: Package malicious-pkg@1.0.0
  2. airbnb/project-b: Package bad-actor@2.1.0
  ...

---

### 7. Bulk Dependency Check

**User:** I'm considering adding these packages to my project. Are they safe?
- lodash@4.17.21
- express@4.18.2
- axios@1.6.2

**AI uses:** `scan_dependencies` tool with:
```json
{
  "dependencies": {
    "lodash": "4.17.21",
    "express": "4.18.2", 
    "axios": "1.6.2"
  },
  "malware_only": false
}
```

**Response:** All 3 packages are safe. No malware or critical vulnerabilities detected.

---

### 8. Check Specific Malware

**User:** I heard @ctrl/tinycolor version 4.1.2 was compromised. Is this true?

**AI uses:** `scan_package` tool with `{"package": "@ctrl/tinycolor@4.1.2", "malware_only": false}`

**Response:** ⚠️ MALWARE DETECTED! Package @ctrl/tinycolor@4.1.2 contains malicious code (MAL-2025-47141) - Shai-Hulud NPM worm...

---

### 9. Compare Versions

**User:** Is lodash version 4.17.15 safer than 4.17.20?

**AI uses:** `scan_package` twice:
- `{"package": "lodash@4.17.15"}`
- `{"package": "lodash@4.17.20"}`

**Response:** 
- lodash@4.17.15: Found 2 vulnerabilities
- lodash@4.17.20: Clean
- Recommendation: Upgrade to 4.17.20

---

### 10. Private Repository Scan (with token)

**User:** Check if my company's private repo acme-corp/internal-app has any security issues

**AI uses:** `scan_github_repository` tool with `{"owner": "acme-corp", "repository": "internal-app", "malware_only": false}`

**Response:** Scanned 67 dependencies. Found 1 critical vulnerability in package foo@1.2.3...

---

## Advanced Use Cases

### CI/CD Integration Check

**User:** I want to add RoguePkg to my CI/CD pipeline. Can you check if my current dependencies in my-org/my-repo are clean?

**AI uses:** `scan_github_repository` tool

**Response:** [Results] + Suggestions for integrating into CI/CD...

---

### Organization Security Audit

**User:** Perform a security audit of all repositories in my-company organization and generate a summary

**AI uses:** `scan_github_organization` tool

**Response:** 
Security Audit Summary for my-company:
- Total repositories scanned: 50
- Clean repositories: 45 (90%)
- Repositories with vulnerabilities: 5 (10%)
- Critical issues: 2

Affected Repositories:
1. my-company/repo-a (CRITICAL - malware detected)
2. my-company/repo-b (HIGH - 3 vulnerabilities)
...

---

### Dependency Decision Making

**User:** I need a color manipulation library. Should I use tinycolor2 or chroma-js? Which is safer?

**AI uses:** `scan_package` for both:
- `{"package": "tinycolor2"}`
- `{"package": "chroma-js"}`

**Response:** 
- tinycolor2: Clean ✅
- chroma-js: Clean ✅
Both are safe to use. [Additional comparison]...

---

### Transitive Dependency Check

**User:** Check if react has any vulnerable transitive dependencies

**AI uses:** GitHub API to fetch package-lock.json, then `scan_dependencies`

**Response:** Scanned 42 total dependencies (including transitive). Found 1 vulnerability in a transitive dependency...

---

## Error Handling Examples

### Missing Token

**User:** Scan the private-org organization

**Response:** Error: GitHub integration requires GITHUB_TOKEN to be set. Please configure your token in the MCP settings.

---

### Repository Not Found

**User:** Check the repository nonexistent/repo

**Response:** Error: Repository not found or inaccessible. This could be because:
1. Repository doesn't exist
2. Repository is private (need token)
3. Repository has no package.json

---

### Rate Limit Hit

**User:** Scan google organization with 200 repos

**Response:** Scanning 200 repositories... (Note: this may take time due to GitHub rate limits)

---

## Tips for Best Results

1. **Be specific** - Include version numbers when checking specific packages
2. **Use malware_only** - For faster scans when you only care about malware
3. **Set max_repos** - When scanning large organizations
4. **Combine with GitHub MCP** - Use GitHub MCP to list repos, then RoguePkg to scan them
5. **Schedule regular scans** - Ask to check organizations weekly

## Sample Workflows

### Workflow 1: Adding a New Dependency

```
1. "Is package-name safe?"
2. "What version of package-name should I use?"
3. "Check if package-name has any recent security issues"
```

### Workflow 2: Repository Security Review

```
1. "Scan owner/repo for malware"
2. "Do a full vulnerability scan of owner/repo"
3. "Show me the most critical issues in owner/repo"
```

### Workflow 3: Organization Security Audit

```
1. "How many repositories does organization have?"
2. "Scan organization for malicious packages"
3. "Which repositories in organization need immediate attention?"
4. "Generate a security report for organization"
```

