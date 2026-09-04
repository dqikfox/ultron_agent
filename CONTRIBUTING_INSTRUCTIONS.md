# Contributing to ULTRON Agent - Developer Instructions

Guide for maintaining and updating developer instructions and documentation.

## Overview

This repository includes comprehensive auto-discoverable instructions for AI developers using Copilot, Codex, and other tools. When you modify instructions or add tools, the documentation must be kept in sync.

## Files to Maintain

### Auto-Discovered Instruction Files
These are auto-discovered by Copilot and similar tools:

1. **`.github/copilot-instructions.md`** (Primary)
   - Auto-discovered by: Copilot CLI, VS Code, JetBrains, GitHub Web
   - Update when: Adding tools, changing architecture, fixing issues
   - Length: 650+ lines (keep comprehensive)

2. **`.codex/instructions.md`** (Editor-specific)
   - For Codex editor users
   - Contains editor-specific workflows
   - Update when: Codex workflows change

3. **`.cursor/mcp.json`**
   - MCP server configuration
   - Update when: Adding new MCP servers

### Reference Guides

4. **`TOOLS_INVENTORY.md`** (Auto-generated)
   - Catalog of 105+ tools
   - **Keep in sync by running:** `python3 tools_inventory.py`
   - Update frequency: After adding/removing tools

5. **`TESTING_GUIDE.md`**
   - pytest fixtures and patterns
   - Update when: New test patterns emerge

6. **`MEMORY_AND_VECTORS_GUIDE.md`**
   - Memory system and Pinecone integration
   - Update when: Memory/vector changes made

## Workflow: Adding a New Tool

### Step 1: Create Tool File
```python
# tools/my_new_tool.py
from tools.tool_interface import ToolInterface

class MyNewTool(ToolInterface):
    """Brief description of what this tool does"""
    
    def __init__(self):
        super().__init__("my_tool_name", "Detailed description")
    
    def execute(self, **kwargs):
        # Implementation
        return result
```

### Step 2: Tool Auto-Discovery
Tools are auto-discovered by `tools/tool_loader.py`
- No manual registration needed
- Just add file to `tools/` directory

### Step 3: Update Inventory
Run the auto-discovery script:
```bash
python3 tools_inventory.py
# This updates TOOLS_INVENTORY.md with your new tool
```

### Step 4: Update Main Instructions
Edit `.github/copilot-instructions.md`:
- Add tool to appropriate category
- Add example usage if relevant
- Update tool count (now X+ tools)

### Step 5: Create Commit
```bash
git add tools/my_new_tool.py .github/copilot-instructions.md TOOLS_INVENTORY.md
git commit -m "feat: add MyNewTool

- Implements [feature description]
- Auto-discovered via tool_loader.py
- See TOOLS_INVENTORY.md for complete documentation

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

## Workflow: Fixing Documentation

### For Bugs or Inaccuracies
1. Edit the relevant instruction file
2. Keep references consistent across files
3. Test with actual Copilot tools if possible
4. Commit with clear message

Example:
```bash
git commit -m "docs: fix incorrect API port in instructions

- api_server.py uses port 5000, not 8000
- Updated .github/copilot-instructions.md
- Updated MEMORY_AND_VECTORS_GUIDE.md example code"
```

### For New Patterns or Features
1. Update primary instruction file (`.github/copilot-instructions.md`)
2. Add section to relevant guide (TESTING_GUIDE.md, etc.)
3. Run `tools_inventory.py` if tools affected
4. Update cross-references

## Validation Before Commit

### Checklist
- [ ] Instruction files have no broken links
- [ ] Code examples are runnable
- [ ] Cross-references are valid (search for filenames)
- [ ] Tool counts are accurate
- [ ] conftest.py locations verified (if testing changes)
- [ ] No trailing whitespace in markdown

### Manual Validation
```bash
# Check markdown syntax
for file in .github/copilot-instructions.md .codex/instructions.md *.md; do
  echo "Checking $file..."
  grep -n '\[.*\](#)' "$file" | head -5  # Broken links
done

# Verify tool inventory is current
python3 tools_inventory.py && git diff TOOLS_INVENTORY.md
# If there are changes, commit them too
```

## GitHub Actions Workflows

### Automatic Workflows
Two workflows run on relevant file changes:

1. **`update-tool-inventory.yml`**
   - Triggers: Changes to `tools/**/*.py`
   - Action: Runs tool discovery, creates PR if inventory changed
   - Manual trigger: Actions tab → "Update Tool Inventory" → Run

2. **`validate-instructions.yml`**
   - Triggers: Changes to instruction files
   - Action: Validates markdown, checks examples, cross-references
   - Runs on: Pushes and pull requests

### Local Hook Setup
```bash
# Use the hooks we've provided
git config core.hooksPath .githooks

# This enables:
# - Pre-commit: Checks for documentation quality
# - Post-merge: Alerts about instruction updates
```

## Common Update Scenarios

### Scenario 1: Adding New Architecture Pattern
1. Document in `.github/copilot-instructions.md`
2. Add example code with syntax highlighting
3. Cross-reference from TESTING_GUIDE.md or MEMORY_AND_VECTORS_GUIDE.md
4. Commit

### Scenario 2: Fixing Known Issue
1. Update "Troubleshooting" section in `.github/copilot-instructions.md`
2. Reference related files (e.g., agent_core.py line X)
3. Include actual error message and solution
4. Commit

### Scenario 3: Memory System Enhancement
1. Update MEMORY_AND_VECTORS_GUIDE.md with new API
2. Add example code
3. Update config examples
4. Reference in main instructions
5. Commit

### Scenario 4: New Tool Category
1. Add category to TOOLS_INVENTORY.md
2. Run `tools_inventory.py` to categorize
3. Update `.github/copilot-instructions.md` tool listing
4. Commit

## Testing Your Changes

### Before Committing
1. **Check with Copilot CLI:**
   ```bash
   # Verify instructions are readable
   cat .github/copilot-instructions.md | head -50
   ```

2. **Check cross-references:**
   ```bash
   # Find all markdown links
   grep -h '\[.*\](.*\.md)' .github/copilot-instructions.md | sort | uniq
   
   # Verify files exist
   for link in $(grep -o '[A-Z_]*\.md' .github/copilot-instructions.md | sort -u); do
     test -f "$link" && echo "✓ $link" || echo "✗ $link MISSING"
   done
   ```

3. **Validate tool inventory:**
   ```bash
   python3 tools_inventory.py
   git diff TOOLS_INVENTORY.md | head -50
   ```

### After Committing
- Monitor GitHub Actions workflows
- Check that validation workflow passes
- Review any auto-generated PRs (tool inventory)

## Style Guide

### Instruction Files
- **Line length:** Keep under 100 characters for readability
- **Code blocks:** Use language-specific syntax highlighting (```python, ```bash)
- **Emphasis:** Use **bold** for important terms, `code` for literals
- **Headers:** Use # for main sections, ## for subsections
- **Examples:** Always include runnable examples

### Markdown Standards
- Headings: Use # for h1, ## for h2, etc. (never skip levels)
- Lists: Use - for bullets, 1. for numbered
- Code: Use ```language for blocks, `text` for inline
- Links: Always verify targets exist
- Tables: Use standard markdown table syntax

### Git Commits
Include:
- Clear, descriptive subject (50 chars max)
- Blank line
- Detailed body (wrap at 72 chars)
- Reference to related docs if applicable
- Copilot co-author trailer

Example:
```
docs: document new memory lifecycle management

Added comprehensive section on memory archival and cleanup:
- Explains short-term vs long-term memory retention
- Documents archival strategies
- Includes implementation examples
- References ultron_config.json for TTL settings

See MEMORY_AND_VECTORS_GUIDE.md for full details.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## Troubleshooting

### Issue: Tool not showing in inventory
- Ensure file is in `tools/` directory
- Ensure class inherits from `ToolInterface`
- Run: `python3 tools_inventory.py`
- Check TOOLS_INVENTORY.md for tool name

### Issue: Broken cross-references
- Use full filename: `TESTING_GUIDE.md` not `Testing Guide`
- Verify file exists in repo root
- Check spelling and case

### Issue: GitHub Actions workflow failed
- Check Actions tab for error details
- Validate markdown syntax manually
- Run `python3 tools_inventory.py` locally
- Commit fixes and push again

## Review Process

For pull requests modifying instructions:

1. **Automated checks**
   - GitHub Actions workflows run automatically
   - Validation workflow checks markdown and examples

2. **Manual review**
   - Verify accuracy against actual codebase
   - Check consistency across documents
   - Ensure examples are runnable

3. **Approval**
   - At least one approval from maintainers
   - All checks passing
   - Cross-references verified

## Resources

- **Tool Discovery:** `tools_inventory.py` (executable)
- **Pytest Reference:** `TESTING_GUIDE.md`
- **Memory System:** `MEMORY_AND_VECTORS_GUIDE.md`
- **Main Instructions:** `.github/copilot-instructions.md`
- **Codex Guide:** `.codex/instructions.md`
- **Git Hooks:** `.githooks/` directory

## Questions?

Refer to:
- `.github/copilot-instructions.md` for development guidance
- `TOOLS_INVENTORY.md` for tool details
- Individual guides (TESTING_GUIDE.md, etc.) for specific topics
- GitHub Issues for bugs or feature requests

---

**Last Updated:** 2026-03-06
**Maintainer:** ULTRON Agent Team
**Version:** 3.0
