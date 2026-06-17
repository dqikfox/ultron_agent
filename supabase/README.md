# Supabase Integration for Ultron Agent

This module provides Supabase backend integration for the Ultron Agent platform, replacing local SQLite storage with a cloud-based PostgreSQL database.

## Features

- **Conversations** - Store and retrieve chat histories
- **Avatars** - Persistent avatar game character data
- **Agent Sessions** - State management for AI agent workflows
- **Workflows** - Save and load workflow definitions
- **User Preferences** - Customizable user settings
- **Audit Logging** - Track actions and changes

## Setup

### 1. Configure Supabase

Copy the example environment file and add your credentials:

```bash
cp supabase/.env.example supabase/.env
```

Edit `.env` with your Supabase credentials:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` - Your service role key (keep secret!)

### 2. Create Database Schema

Go to your Supabase Dashboard and navigate to **SQL Editor**. Copy and paste the contents of `supabase/schema.sql` and run it.

This will create:
- 8 database tables
- Indexes for performance
- Row Level Security policies
- Automatic timestamp triggers

### 3. Install Dependencies

Make sure you have the Supabase Python client:

```bash
pip install supabase python-dotenv
```

## Usage

### Basic Usage

```python
from supabase.database import UltronDB

# Initialize database
db = UltronDB()

# Create a conversation
conversation = db.create_conversation(user_id="user123", title="My Chat")
print(f"Created: {conversation['id']}")

# Add messages
db.add_message(conversation["id"], "user", "Hello!")
db.add_message(conversation["id"], "assistant", "Hi there!")

# Get messages
messages = db.get_messages(conversation["id"])
```

### Avatar Management

```python
# Create an avatar
avatar = db.create_avatar(
    user_id="user123",
    name="Hero",
    race="Elf",
    char_class="Mage",
    alignment="Chaotic Good"
)

# Update avatar stats
db.update_avatar(avatar["id"], health=150, mana=200)

# Get all user avatars
avatars = db.get_user_avatars("user123")
```

### Agent Sessions

```python
# Create a session
session = db.create_session(
    session_id="session_001",
    user_id="user123",
    context={"mode": "assistant"}
)

# Update session state
db.update_session(
    session_id="session_001",
    state={"step": 5, "data": {...}}
)

# Get session
session = db.get_session("session_001")
```

### Workflows

```python
# Save a workflow
workflow = db.create_workflow(
    name="My Workflow",
    definition={"steps": [...]},
    user_id="user123",
    is_public=False
)

# List workflows
workflows = db.list_workflows(user_id="user123")
```

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key for admin access |
| `SUPABASE_ANON_KEY` | Anonymous key for client access |

### Row Level Security

The database uses Supabase's Row Level Security (RLS) policies. By default, all authenticated users can perform all operations. You can customize these policies in the Supabase Dashboard under **Authentication > Policies**.

## Files

- `schema.sql` - Database schema definition
- `database.py` - Python database client
- `supabase_client.py` - Connection utilities
- `.env.example` - Environment template

## License

Same as ultron_agent project.
