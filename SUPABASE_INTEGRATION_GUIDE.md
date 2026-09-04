# 🗄️ Supabase Integration Setup Guide

**Project**: ULTRON Agent 3.0
**Status**: ✅ Partially Configured
**Required For**: Message logging, conversation history
**Date**: November 4, 2025

---

## 📊 Current Status

| Component | Status | Config File |
|-----------|--------|-------------|
| Database Tool | ✅ Implemented | `tools/database_integration_tool.py` |
| Supabase Client | ⏳ Partially Configured | `ultron_agent_2/gui/ultron_enhanced/web/index.html` |
| Config Keys | ❌ Missing/Null | `ultron_config.json` |
| Environment Variables | ❌ Not Set | System Environment |

---

## 🎯 Quick Setup (5 Minutes)

### Step 1: Create Supabase Account

1. Go to https://supabase.com
2. Sign up with email or GitHub
3. Create new project:
   - **Project Name**: `ultron-agent`
   - **Database Password**: Generate strong password
   - **Region**: Pick closest to your location
4. Wait 2-3 minutes for project initialization

### Step 2: Get Supabase Credentials

After project created:

```
1. Click on "Settings" (⚙️) icon
2. Go to "API" tab
3. Copy these values:
   - Project URL: https://YOUR_PROJECT_ID.supabase.co
   - anon key: eyJhbGc... (starts with eyJ)
   - service_role key: (optional, for backend)
```

### Step 3: Update ultron_config.json

Replace `null` values:

```json
{
  "supabase_url": "https://YOUR_PROJECT_ID.supabase.co",
  "supabase_anon_key": "eyJhbGc...",
  "supabase_service_role_key": "eyJhbGc..."
}
```

### Step 4: Create Messages Table in Supabase

1. Go to Supabase Dashboard
2. Click "SQL Editor" (left sidebar)
3. Click "New Query"
4. Paste:

```sql
CREATE TABLE IF NOT EXISTS messages (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  sender TEXT NOT NULL,
  message TEXT NOT NULL,
  message_type TEXT DEFAULT 'text',
  metadata JSONB,
  session_id TEXT
);

ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all" ON messages FOR ALL USING (true);
```

5. Click "Run"

### Step 5: Verify Connection

```powershell
# Test Supabase URL is reachable
curl -I "https://YOUR_PROJECT_ID.supabase.co"

# Should return 200 OK
```

---

## 🔑 Environment Variables Setup

### Option 1: PowerShell (Temporary)

```powershell
# For current session only
$env:SUPABASE_URL = "https://YOUR_PROJECT_ID.supabase.co"
$env:SUPABASE_ANON_KEY = "eyJhbGc..."
$env:SUPABASE_SERVICE_ROLE_KEY = "eyJhbGc..."

# Verify
Write-Host $env:SUPABASE_URL
```

### Option 2: System Environment (Permanent)

```powershell
# Right-click "This PC" → Properties → Advanced system settings
# Click "Environment Variables"
# Click "New" button

# Add these variables:
# Name: SUPABASE_URL
# Value: https://YOUR_PROJECT_ID.supabase.co

# Name: SUPABASE_ANON_KEY
# Value: eyJhbGc...

# Name: SUPABASE_SERVICE_ROLE_KEY
# Value: eyJhbGc...

# Restart VS Code and PowerShell for changes to take effect
```

### Option 3: .env File (Development)

Create `.env` in project root:

```
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
```

Then in Python:
```python
import os
from dotenv import load_dotenv

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
```

---

## 📝 Configuration in Code

### Python (Backend)

```python
# In tools/database_integration_tool.py or brain.py

import os
from supabase import create_client, Client

supabase_url = os.getenv("SUPABASE_URL") or "https://YOUR_PROJECT_ID.supabase.co"
supabase_key = os.getenv("SUPABASE_ANON_KEY") or "eyJhbGc..."

supabase: Client = create_client(supabase_url, supabase_key)

# Store message
response = supabase.table("messages").insert({
    "sender": "user",
    "message": "Hello Ultron",
    "session_id": "session-123"
}).execute()

# Query messages
data = supabase.table("messages").select("*").limit(10).execute()
print(data.data)  # List of messages
```

### JavaScript (Frontend/GUI)

```javascript
// In gui/ultron_enhanced/web/index.html

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const supabaseUrl = 'https://YOUR_PROJECT_ID.supabase.co';
const supabaseAnonKey = 'eyJhbGc...';

const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Store message
const { data, error } = await supabase
  .from('messages')
  .insert([{
    sender: 'user',
    message: 'Hello from ULTRON',
    session_id: 'session-123'
  }]);

// Query messages
const { data, error } = await supabase
  .from('messages')
  .select('*')
  .limit(10);

console.log(data); // Array of messages
```

---

## ✅ Verification Checklist

After setup, verify each step:

- [ ] Supabase account created at https://supabase.com
- [ ] Project created with name "ultron-agent"
- [ ] API credentials copied (URL, anon key)
- [ ] `ultron_config.json` updated with real values
- [ ] Messages table created via SQL query
- [ ] Row-level security policies enabled
- [ ] `SUPABASE_URL` environment variable set
- [ ] `SUPABASE_ANON_KEY` environment variable set
- [ ] Test query works: `curl https://YOUR_PROJECT_ID.supabase.co/rest/v1/messages?select=count()`
- [ ] Continue.dev can access Supabase (check logs)

---

## 🧪 Test Connection

### Python Test

```python
# test_supabase.py
import os
from supabase import create_client

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    print("❌ Missing Supabase credentials")
    exit(1)

try:
    supabase = create_client(supabase_url, supabase_key)

    # Test insert
    response = supabase.table("messages").insert({
        "sender": "test",
        "message": "Test message"
    }).execute()

    print("✅ Supabase connection successful!")
    print(f"Inserted: {response.data}")

except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run test:
```powershell
python test_supabase.py
```

### JavaScript Test

```javascript
// test_supabase.js
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const supabase = createClient(
  'https://YOUR_PROJECT_ID.supabase.co',
  'eyJhbGc...'
);

async function test() {
  try {
    const { data, error } = await supabase
      .from('messages')
      .select('count()', { count: 'exact' });

    if (error) {
      console.error('❌ Error:', error);
    } else {
      console.log('✅ Connection successful!');
      console.log(`Total messages: ${data}`);
    }
  } catch (e) {
    console.error('❌ Connection failed:', e);
  }
}

test();
```

---

## 🔒 Security Best Practices

### ✅ DO

- Use `anon key` for frontend (public)
- Use `service_role key` for backend only
- Enable RLS (Row Level Security) policies
- Rotate keys regularly
- Use environment variables for secrets

### ❌ DON'T

- Commit secrets to Git
- Share `service_role key` publicly
- Disable RLS policies
- Use same key for dev and prod
- Hardcode credentials in code

---

## 🚨 Common Issues

| Issue | Solution |
|-------|----------|
| "Connection refused" | Verify URL is correct (check for typos) |
| "401 Unauthorized" | Check anon key is correct |
| "Table doesn't exist" | Run SQL query to create messages table |
| "CORS error" | Enable CORS in Supabase settings (Settings → CORS) |
| "Row Level Security denied" | Check RLS policies allow anonymous access |

---

## 🎯 Success Criteria

✅ Can insert messages to Supabase
✅ Can query messages from Supabase
✅ Frontend and backend both connected
✅ No authentication errors
✅ Table has data from tests

---

## 📚 Related Files

- **Database Tool**: `tools/database_integration_tool.py`
- **GUI Integration**: `gui/ultron_enhanced/web/index.html`
- **Config Example**: `ultron_config.json.example`
- **Enhanced Config**: `ultron_config_enhanced.json`

---

## 🔗 Resources

- **Supabase Docs**: https://supabase.com/docs
- **Supabase Python Client**: https://github.com/supabase-community/supabase-py
- **Supabase JavaScript Client**: https://github.com/supabase/supabase-js
- **SQL Examples**: https://supabase.com/docs/guides/database

---

*Created: November 4, 2025*
*Effort to complete: 5-15 minutes*
*Complexity: Low (mostly copy-paste credentials)*
