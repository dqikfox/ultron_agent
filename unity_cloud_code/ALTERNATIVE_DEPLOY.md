# Alternative Deployment (Without UGS CLI)

## Option 1: Unity Dashboard (Manual - 5 minutes)

### Deploy C# Module
1. Build locally: `cd UltronModule && dotnet build`
2. Go to [Cloud Code Dashboard](https://dashboard.unity3d.com/organizations/dqikst/projects/3f675a32-c96c-4d4e-b5a2-c81e23697d10/cloud-code/modules)
3. Click **Create Module**
4. Upload `UltronModule.dll` from `bin/Debug/netstandard2.1/`
5. Publish

### Deploy JavaScript Scripts
1. Go to [Cloud Code Scripts](https://dashboard.unity3d.com/organizations/dqikst/projects/3f675a32-c96c-4d4e-b5a2-c81e23697d10/cloud-code/scripts)
2. Click **Create Script**
3. Name: `hello-world`, copy code from `hello-world.js`
4. Add parameter: `name` (string)
5. Save & Publish
6. Repeat for `ultron-command.js`

## Option 2: Use Unity Editor Package Manager

### Install Cloud Code Authoring
1. Open Unity Editor
2. Window > Package Manager
3. Add by name: `com.unity.services.cloudcode.authoring`
4. Create scripts in `Assets/CloudCode/`
5. Right-click > Publish to Cloud Code

## Option 3: REST API (Automated)

### Upload via API
```bash
# Get access token
curl -X POST https://services.api.unity.com/auth/v1/token \
  -H "Content-Type: application/json" \
  -d '{"grant_type":"client_credentials","client_id":"YOUR_KEY","client_secret":"YOUR_SECRET"}'

# Deploy script
curl -X POST https://services.api.unity.com/cloud-code/v1/projects/3f675a32-c96c-4d4e-b5a2-c81e23697d10/scripts \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d @script.json
```

## Recommended: Use Dashboard (Easiest)

**Steps**:
1. Build C# module: `dotnet build`
2. Upload DLL via Dashboard
3. Create JavaScript scripts via Dashboard
4. Test from Unity

**No CLI needed!** ✅
