# Conversation Cleanup Utility

Use `tools/conversation_cleanup.py` to strip noise from raw ULTRON conversation exports that follow the ChatGPT “mapping” structure. The script does **not** overwrite the original data; it writes a cleaned, flattened view plus optional Markdown statistics.

## Requirements

- Python 3.9+ (ships with the project)
- Input file shaped like `conversations.json` (list of conversations; each conversation has a `mapping` tree)

## Usage

```bash
# Basic cleanup – writes conversations_cleaned.json next to the source file
python tools/conversation_cleanup.py "H:/My Drive/ultron/conversations.json"

# Add --markdown for a human-readable report
python tools/conversation_cleanup.py "H:/My Drive/ultron/conversations.json" --markdown
```

Outputs:

- `<name>_cleaned.json` – Flattened conversations with:
  - Message list stripped of empty system/tool noise
  - Deduplicated attachment metadata
  - Role counts and fatigue flags
- `<name>_cleanup_report.md` (optional) – Summary metrics and a fatigue watch list

## What Counts as “Noise”

- Empty bootstrap system messages
- Tool spinner/context updates (`file_search` with `spinner`/`context_stuff` commands)
- Assistant/tool messages that contain no text and no attachments

Messages from the user are never removed. Attachments are deduplicated by ID/name, but the first occurrence is kept.

## Fatigue Detection

The script flags a conversation when:

- The cleaned message count exceeds 350, or
- The last few user turns contain keywords such as “I’m tired”, “need a break”, “exhausted”, etc.

Flagged conversations include `fatigue_reasons` so the agent can respond with summaries or rest prompts.

## Next Steps for Integration

- Import the cleaned JSON into Supabase or your analytics pipeline to power smarter UI prompts.
- Use the Markdown report for sprint reviews (longest sessions, attachment churn, fatigue hot spots).
- Extend `FATIGUE_KEYWORDS` / `NOISE_TOOL_NAMES` if new tool signals appear in the logs.
