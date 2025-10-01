---
name: Bug Report
about: Report a bug or issue with the OSV Scanner
title: '[BUG] '
labels: bug
assignees: ''
---

## Describe the Bug
A clear and concise description of what the bug is.

## To Reproduce
Steps to reproduce the behavior:
1. Run command '...'
2. With file '...'
3. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g. Ubuntu 22.04, macOS 13, Windows 11]
- Python Version: [e.g. 3.9, 3.10, 3.11]
- Scanner Version/Commit: [e.g. v1.0.0 or commit hash]
- Running as: [GitHub Action / Command-line]

## Command/Workflow
```bash
# If using command-line, paste the command you ran
python rogue_dep.py --file package.json --batch
```

```yaml
# If using GitHub Action, paste relevant workflow snippet
- uses: YOUR-USERNAME/osv-scanner-action@v1
  with:
    malware-only: 'true'
```

## Error Messages/Logs
```
Paste any error messages or relevant log output here
```

## Sample package.json (if applicable)
```json
{
  "dependencies": {
    "problematic-package": "1.0.0"
  }
}
```

## Additional Context
Add any other context about the problem here.

