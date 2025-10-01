# Test Files for OSV Scanner

This directory contains test files with **known compromised packages** for testing the malware detection scanner.

## ⚠️ WARNING

**DO NOT run `npm install` in this directory!**

These files contain references to known malicious packages for testing purposes only.

## Test Files

### Main Project (`test_files/`)
- **package.json** - Contains `@ctrl/tinycolor@4.1.2` (COMPROMISED - Shai-Hulud worm)
- **package-lock.json** - Lockfile with the same compromised package and its dependencies

### Subproject (`test_files/subproject/`)
- **package.json** - Contains `mongodb-ci@1.0.0` (COMPROMISED - malware)

## Known Malware Packages in Test Files

1. **@ctrl/tinycolor@4.1.2**
   - Type: Malware (Shai-Hulud NPM worm)
   - GHSA: GHSA-qjqf-7j6f-82c4
   - MAL ID: MAL-2025-47141
   - Description: Steals tokens and credentials, propagates to other packages

2. **mongodb-ci@1.0.0**
   - Type: Malware
   - GHSA: GHSA-xx5w-6pvc-686w
   - Description: Malicious package masquerading as MongoDB tooling

## How to Test

### Test single file
```bash
# Test with package.json
python osv_scan.py --file test_files/package.json --malware-only

# Test with package-lock.json
python osv_scan.py --file test_files/package-lock.json --batch --malware-only
```

### Test directory scanning (auto-detection)
```bash
# Scan entire test_files directory recursively
python osv_scan.py --scan-dir test_files --malware-only

# This will find:
# - test_files/package.json
# - test_files/package-lock.json
# - test_files/subproject/package.json
```

## Expected Results

When scanning these test files, you should see:

- ✅ Detection of `@ctrl/tinycolor@4.1.2` as malware
- ✅ Detection of `mongodb-ci@1.0.0` as malware
- ✅ Detailed information including SHA256 hashes
- ✅ Multiple source confirmations (ghsa-malware, google-open-source-security)
- ✅ References to security advisories and incident reports

## Clean Packages (Should NOT be flagged)

These packages in the test files are clean and should not trigger alerts:
- `express@4.19.2` (may have vulnerabilities but not malware)
- `lodash@4.17.21` (clean version)
- `webpack@5.90.0` (clean)
- `react@18.2.0` (clean)
- `typescript@5.3.3` (clean)

## Safety Notes

1. **Never install dependencies** from these test files
2. These are for **testing detection only**
3. The compromised packages are real and dangerous
4. Always use in isolated test environments
5. Delete after testing if desired

