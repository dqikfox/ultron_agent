# 🎯 Browser MCP Cheat Sheet for VS Code

**Quick Reference - Keep This Open While Coding!**

---

## ⌨️ Essential Shortcuts

```
Ctrl + L .................. Open Continue (Browser MCP access)
Ctrl + I .................. GitHub Copilot Inline
Ctrl + Shift + I .......... GitHub Copilot Chat Panel
```

---

## 🌐 Browser MCP Commands

### Navigation
```
@browsermcp navigate to [URL]
@browsermcp go to [URL]
@browsermcp open [URL]
```

### Interaction
```
@browsermcp click [element/button]
@browsermcp fill [field] with [value]
@browsermcp submit form
@browsermcp scroll to [position]
```

### Data Extraction
```
@browsermcp extract all links
@browsermcp extract [selector/element]
@browsermcp get page title
@browsermcp get main content
@browsermcp scrape [data]
```

### Screenshots
```
@browsermcp screenshot
@browsermcp capture page
@browsermcp screenshot [element]
```

### Server Control
```
@browsermcp start
@browsermcp stop
@browsermcp status
```

---

## 🎨 Common Patterns

### Research Pattern
```
@browsermcp navigate to [docs URL]
→ extract documentation
→ help me implement [feature]
```

### Code Review Pattern
```
@browsermcp check [best practices URL]
→ review my current code
→ suggest improvements
```

### Testing Pattern
```
@browsermcp navigate to localhost:[port]
→ test [functionality]
→ report issues
```

---

## 🔥 Power Combos

### Combo 1: Research + Code
```bash
# Continue (Ctrl+L)
@browsermcp navigate to react.dev/learn
@browsermcp extract hooks guide

# Copilot (Ctrl+I in file)
"Implement based on React hooks guide Continue just read"
```

### Combo 2: Multi-Source Research
```bash
@browsermcp navigate to [URL1]
@github get README from [repo]
@filesystem read [file]

"Now help me code [feature] using all this context"
```

### Combo 3: Competitive Analysis
```bash
@browsermcp analyze [competitor URL]
@browsermcp extract UI patterns

"Help me implement similar features in my app"
```

---

## 📋 Your Available MCP Servers

```
@browsermcp ............ Modern browser automation
@browser ............... Alternative browser (Anthropic)
@github ................ GitHub operations
@filesystem ............ File system access
@deepwiki .............. Wikipedia knowledge
```

---

## 🎯 Top 10 Use Cases

| # | Use Case | Command Example |
|---|----------|-----------------|
| 1 | API Docs | `@browsermcp navigate to stripe.com/docs/api` |
| 2 | Framework Updates | `@browsermcp check react.dev for v19 changes` |
| 3 | UI Inspiration | `@browsermcp analyze tailwindui.com layout` |
| 4 | Error Research | `@browsermcp search stackoverflow for [error]` |
| 5 | Competitor Analysis | `@browsermcp visit [competitor] and analyze` |
| 6 | Package Research | `@browsermcp check npm package [name]` |
| 7 | Testing | `@browsermcp test localhost:3000` |
| 8 | Data Scraping | `@browsermcp extract table from [URL]` |
| 9 | Code Examples | `@browsermcp get examples from [tutorial]` |
| 10 | Release Notes | `@browsermcp check [library] changelog` |

---

## ⚠️ Troubleshooting Quick Fixes

| Issue | Fix |
|-------|-----|
| MCP not responding | `@browsermcp stop` then `@browsermcp start` |
| Command not working | Check spelling, use exact format |
| Slow response | Wait 5-10 seconds, may be loading page |
| Server error | Check Continue output panel |
| Node.js error | Verify: `node --version` (need v16+) |

---

## 🚀 Quick Start (30 Seconds)

1. Press `Ctrl + L`
2. Type: `@browsermcp navigate to github.com`
3. See it work! ✨

---

## 📚 Full Docs

- **Complete Guide:** `VSCODE_BROWSER_MCP_GUIDE.md`
- **Quick Demo:** `QUICK_DEMO_BROWSER_MCP.md`
- **Browser MCP:** `BROWSER_MCP_GUIDE.md`

---

**Keep this open while coding! 📌**

*Press `Ctrl+L` and try: `@browsermcp navigate to example.com`*
