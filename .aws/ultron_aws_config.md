# ULTRON Agent - AWS Configuration Guide

## AWS Resources Overview

### Amazon Q / CodeWhisperer
- **Region**: us-east-1
- **Customization**: ultron
- **ARN**: `arn:aws:codewhisperer:us-east-1:941284019015:customization/7UY44NRR97Q4`
- **Status**: Creating (as of 2025-10-25 7:07 PM)

### Application (Oasis)
- **Name**: oasis_app
- **Description**: playground
- **Region**: us-west-2
- **Application Tag Key**: awsApplication
- **Application Tag Value**: `arn:aws:resource-groups:us-west-2:941284019015:group/oasis_app/06685rwrf3sclyi4jebduohwkd`

### CodeBuild
- **Project**: runner
- **Latest Build**: `runner:f9aedd7c-a0f1-4321-b83f-92379522f90d`
- **Status**: In Progress

## VS Code Settings

Add to your `.vscode/settings.json`:

```json
{
  "aws.region": "us-east-1",
  "aws.codeWhisperer.enabled": true,
  "aws.codeWhisperer.shareCodeWhispererContentWithAWS": true,
  "aws.codeWhisperer.includeSuggestionsWithCodeReferences": true,
  "amazonQ.telemetry": "Disable",

  // Once customization is available:
  "aws.codeWhisperer.customization": "arn:aws:codewhisperer:us-east-1:941284019015:customization/7UY44NRR97Q4"
}
```

## Authentication Issue Fix

### Current Problem
Amazon Q shows: "Amazon Q service is not signed in"

### Root Cause
- Network timeouts to `oidc.us-east-1.amazonaws.com`
- No active SSO connection detected
- Token refresh failed

### Solution
1. **Sign Out**: `Ctrl+Shift+P` → "Amazon Q: Sign Out"
2. **Clear Cache** (if needed):
   ```powershell
   Remove-Item -Recurse -Force "$env:USERPROFILE\.aws\sso\cache" -ErrorAction SilentlyContinue
   ```
3. **Sign In**: `Ctrl+Shift+P` → "Amazon Q: Sign In"
4. **Choose Method**:
   - AWS Builder ID (recommended for individual use)
   - IAM Identity Center (for organization access)

### Verify Authentication
```powershell
# Check AWS credentials
aws sts get-caller-identity

# Test CodeWhisperer access
aws codewhisperer list-customizations
```

## Multi-Region Setup

Since you have resources in both regions:

```powershell
# Set default region for CodeWhisperer
$env:AWS_REGION = "us-east-1"

# For oasis_app operations, specify region explicitly
aws resourcegroupstaggingapi get-resources `
  --region us-west-2 `
  --resource-arn-list "arn:aws:resource-groups:us-west-2:941284019015:group/oasis_app/06685rwrf3sclyi4jebduohwkd"
```

## Integration with ULTRON Agent

### Environment Variables
Add to your environment or `.env` file:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_DEFAULT_REGION=us-east-1
AWS_ACCOUNT_ID=941284019015

# CodeWhisperer
CODEWHISPERER_CUSTOMIZATION_ARN=arn:aws:codewhisperer:us-east-1:941284019015:customization/7UY44NRR97Q4

# Oasis Application
OASIS_APP_REGION=us-west-2
OASIS_APP_ARN=arn:aws:resource-groups:us-west-2:941284019015:group/oasis_app/06685rwrf3sclyi4jebduohwkd
```

### ULTRON Config Integration
Add to `ultron_config.json`:

```json
{
  "aws": {
    "region": "us-east-1",
    "account_id": "941284019015",
    "codewhisperer_customization": "arn:aws:codewhisperer:us-east-1:941284019015:customization/7UY44NRR97Q4",
    "oasis_app": {
      "name": "oasis_app",
      "region": "us-west-2",
      "resource_group_arn": "arn:aws:resource-groups:us-west-2:941284019015:group/oasis_app/06685rwrf3sclyi4jebduohwkd"
    }
  }
}
```

## Troubleshooting

### Issue: TimeoutError to oidc.us-east-1.amazonaws.com
**Fix**: Re-authenticate using steps above

### Issue: customizationArn=undefined
**Cause**: Customization still creating OR not configured in VS Code
**Fix**: Wait for creation to complete, then add ARN to settings.json

### Issue: No MCP servers found
**Cause**: Amazon Q looking for `.amazonq/mcp.json` which doesn't exist
**Fix**: Create if needed OR ignore (doesn't affect functionality)

### Issue: High memory usage (602 GB)
**Cause**: Likely a reporting bug in the language server
**Fix**: Restart VS Code if it feels sluggish

## Next Steps

1. ✅ Re-authenticate Amazon Q (fixes current issue)
2. ⏳ Wait for CodeWhisperer customization to complete
3. ✅ Configure VS Code settings with customization ARN
4. ✅ Test CodeWhisperer with ULTRON code
5. ✅ Integrate with Continue.dev (already done)

## Verification Checklist

- [ ] Amazon Q signed in (no auth errors)
- [ ] CodeWhisperer customization status = "Available"
- [ ] Inline suggestions working
- [ ] ULTRON-specific suggestions appearing
- [ ] Continue.dev integration working
- [ ] GitHub Copilot coordination active
- [ ] All 4 AI assistants operational
