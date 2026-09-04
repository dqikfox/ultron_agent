# Consciousness GUI Integration - Quick Reference

## New API Endpoints Added to Web GUI

Your web GUI (`http://localhost:8080`) now has these consciousness endpoints:

### GET Endpoints

**`/api/consciousness/status`** - Get consciousness system status
```json
{
  "enabled": true,
  "available": true,
  "name": "ULTRON",
  "role": "AI Assistant",
  "personality": "balanced",
  "model": "llava:7b",
  "ollama_connected": true,
  "conversation_length": 5,
  "predictions_made": 12,
  "workspace_items": 2,
  "self_model_aspects": 8
}
```

**`/api/consciousness/introspect`** - Get full internal state
```json
{
  "success": true,
  "introspection": "🧠 GLOBAL WORKSPACE...",
  "timestamp": "2025-12-17T17:30:00"
}
```

### POST Endpoints

**`/api/consciousness/toggle`** - Enable/disable consciousness mode
```javascript
fetch('/api/consciousness/toggle', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({enabled: true})
})
```

**`/api/consciousness/personality`** - Change personality
```javascript
fetch('/api/consciousness/personality', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({personality: 'curious'})
  // Options: 'brave', 'cautious', 'curious', 'friendly', 'balanced'
})
```

## How It Works

1. **Start Web GUI**: `python web_gui_server.py`
2. **Consciousness Auto-Loads**: When agent initializes
3. **Enable Conscious Mode**: POST to `/api/consciousness/toggle`
4. **Commands Route Through**: When enabled, all `/api/command` go through consciousness
5. **Get Status**: Call `/api/consciousness/status` anytime

## Testing from Browser Console

```javascript
// Check status
fetch('/api/consciousness/status').then(r => r.json()).then(console.log);

// Enable consciousness
fetch('/api/consciousness/toggle', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({enabled: true})
}).then(r => r.json()).then(console.log);

// Change personality to curious
fetch('/api/consciousness/personality', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({personality: 'curious'})
}).then(r => r.json()).then(console.log);

// Get introspection
fetch('/api/consciousness/introspect').then(r => r.json()).then(console.log);

// Send command (will use consciousness if enabled)
fetch('/api/command', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({command: 'What are you thinking about?'})
}).then(r => r.json()).then(console.log);
```

## GUI Changes Needed (Optional)

To add UI controls in your Pokédex GUI, edit `gui/ultron_enhanced/web/index.html`:

```html
<!-- Add to control panel -->
<div class="consciousness-controls">
  <h3>🧠 Consciousness Mode</h3>
  <label>
    <input type="checkbox" id="consciousnessToggle">
    Enable Personality-Driven Mode
  </label>

  <select id="personalitySelect">
    <option value="balanced">Balanced</option>
    <option value="brave">Brave</option>
    <option value="cautious">Cautious</option>
    <option value="curious">Curious</option>
    <option value="friendly">Friendly</option>
  </select>

  <button id="introspectBtn">View Internal State</button>
</div>

<script>
// Toggle consciousness
document.getElementById('consciousnessToggle').addEventListener('change', async (e) => {
  const response = await fetch('/api/consciousness/toggle', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({enabled: e.target.checked})
  });
  const data = await response.json();
  console.log('Consciousness:', data);
});

// Change personality
document.getElementById('personalitySelect').addEventListener('change', async (e) => {
  const response = await fetch('/api/consciousness/personality', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({personality: e.target.value})
  });
  const data = await response.json();
  console.log('Personality changed:', data);
});

// Show introspection
document.getElementById('introspectBtn').addEventListener('click', async () => {
  const response = await fetch('/api/consciousness/introspect');
  const data = await response.json();
  alert(data.introspection);
});
</script>
```

## What Happens When Enabled

**Before** (conscious_mode = False):
```
User: "Hello"
  ↓
brain.py (basic Ollama query)
  ↓
Response: "Hello! How can I help?"
```

**After** (conscious_mode = True):
```
User: "Hello"
  ↓
consciousness.process_input()
  ↓ Global Workspace (attention)
  ↓ Self-Model ("I am ULTRON...")
  ↓ Meta-Cognition (65% confidence)
  ↓ Personality traits applied
  ↓ Ollama with enriched context
  ↓
Response: "Hi there! I'm ULTRON, your AI assistant.
           Right now I'm feeling balanced and ready
           to help you explore interesting topics!"
```

## Verification

Start the server and test:

```bash
cd /home/ultro/projects/ultron_agent
python web_gui_server.py
```

Then in browser console:
```javascript
fetch('/api/consciousness/status').then(r=>r.json()).then(console.log)
```

Should show: `{enabled: false, available: true, name: "ULTRON", ...}`

---

**✅ Consciousness system is now wired into your GUI!**
