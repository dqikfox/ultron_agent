# Supabase Database Setup

The repository ships with a full Supabase schema under `supabase/supabase/tables`. Use the helper script to push those tables into your Supabase/PostgreSQL instance so the Ultron web UI and tools can persist data.

## 1. Gather credentials

Make sure you have a database connection string. Either:

- Copy the `Connection string` from the **Project Settings → Database** panel inside the Supabase dashboard, or
- Build one manually: `postgresql://USER:PASSWORD@HOST:PORT/DATABASE`

> **Tip:** The project summary in `SYSTEM_SUMMARY.md` lists the current Supabase host (`https://jdkddrfloluhkytxdkkh.supabase.co`). You only need the database URL (typically ends with `supabase.co:6543/postgres`).

Export the string into an environment variable before running the setup:

```bash
export SUPABASE_DB_URL="postgresql://postgres:SERVICE_ROLE_KEY@db.xxx.supabase.co:5432/postgres"
```

The script also recognises `SUPABASE_POSTGRES_URL`, `POSTGRES_URL`, `DATABASE_URL`, or the individual `POSTGRES_*` variables.

## 2. Apply the schema

From the repository root run:

```bash
python supabase/setup_supabase_schema.py
```

The script will:

1. Connect to the database using the environment variables above.
2. Execute every SQL file inside `supabase/supabase/tables` (profiles, conversations, messages, ai_providers, file_uploads).
3. Skip tables that already exist so the command can be re-run safely.

You should see output similar to:

```
Connecting to database...
✓ Applied ai_providers.sql
✓ Applied conversations.sql
• Skipped messages.sql (table already exists)
Supabase schema applied successfully.
```

If you receive `psycopg2` import errors, install it first:

```bash
pip install psycopg2-binary
```

## 3. Link with the Ultron web UI

- Set the global variables in `gui/ultron_enhanced/web/index.html` (or inject them at runtime) so the chat widget points at your Supabase project:
  - `window.ULTRON_SUPABASE_URL`
  - `window.ULTRON_SUPABASE_ANON_KEY`
  - `window.ULTRON_SUPABASE_TABLE` (defaults to `messages`)
- Ensure the `messages` and `conversations` tables are present (verified in step 2).
- Run the UI and confirm new chat events appear inside the `messages` table in Supabase.

## 4. Optional: deploy Supabase Functions

Serverless functions live in `supabase/supabase/functions/*`. If you are using the Supabase CLI, copy that folder into your Supabase project directory and deploy as usual:

```bash
supabase functions deploy ai-chat
```

Repeat for `file-upload`, `create-admin-user`, etc., depending on which capabilities you need.

---

The schema script keeps database provisioning in sync with the repository so future table additions can be rolled out by simply dropping a new SQL file into `supabase/supabase/tables` and re-running the helper.
