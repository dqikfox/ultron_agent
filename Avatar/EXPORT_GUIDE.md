# 🚀 Quick Export Guide for ULTRON Model

## Option 1: Using Blender GUI (RECOMMENDED)

### Step-by-Step:

1. **Open Blender**
   - Double-click `ultron+xps.blend` in the Avatar folder
   - Or: Open Blender → File → Open → Select `ultron+xps.blend`

2. **Prepare Model (Optional)**
   - Check that your model looks correct in the viewport
   - Select all objects you want to export (A key)
   - You can include animations if the model has them

3. **Export to GLB**
   - Go to: **File** → **Export** → **glTF 2.0 (.glb/.gltf)**
   - In the export dialog:
     ```
     Format: GLB (binary)
     ✓ Include: Selected Objects (or leave unchecked for all)
     ✓ +Y Up (important!)
     ✓ Remember Export Settings
     ✓ Textures
     ✓ Materials
     ✓ Colors
     ✓ Animations (if available)
     ```
   - **File name**: `ultron_model.glb`
   - **Location**: Same folder as your .blend file (Avatar folder)
   - Click **Export glTF 2.0**

4. **Verify Export**
   - Look for `ultron_model.glb` in the Avatar folder
   - File size should be > 0 KB (usually several MB for models)

5. **View Your Model**
   - Refresh the browser page with `ultron_avatar_viewer.html`
   - Model should load automatically!

---

## Option 2: Using Blender Script

1. **Open Blender** with `ultron+xps.blend`

2. **Switch to Scripting Tab**
   - Top menu: Click "Scripting" workspace

3. **Load Export Script**
   - Click "Open" button in script editor
   - Navigate to: `Avatar/export_ultron_model.py`
   - Click "Open"

4. **Run Script**
   - Click the ▶️ "Run Script" button (or press Alt+P)
   - Watch the console for progress messages

5. **Check Output**
   - Script will print success message
   - `ultron_model.glb` will be created in Avatar folder

6. **Refresh Viewer**
   - Go back to your browser
   - Refresh `ultron_avatar_viewer.html`

---

## Option 3: Command Line (Advanced)

If Blender is in your PATH:

```powershell
cd C:\Projects\ultron_agent\Avatar
blender ultron+xps.blend --background --python export_ultron_model.py
```

---

## Troubleshooting

### ❌ "Export failed" or "Nothing exported"
**Solution**:
- Make sure objects are visible (eye icon in outliner)
- Try selecting all objects (press A in 3D viewport)
- Check that the blend file isn't corrupted

### ❌ "No texture in web viewer"
**Solution**:
- In export settings, make sure "Textures" is checked
- Texture files must be in the same directory or packed in .blend file

### ❌ "Model too small/large in viewer"
**Solution**:
- The viewer auto-scales, but if it looks wrong:
- In Blender: Select all → S (scale) → type desired size → Enter
- Re-export

### ❌ "Model is black/no materials"
**Solution**:
- Make sure "Materials" is checked in export settings
- Check that materials are assigned in Blender
- Try switching lighting mode in viewer (💡 button)

### ❌ "Browser shows 'MODEL NOT FOUND'"
**Solution**:
- Verify `ultron_model.glb` exists in Avatar folder
- Check filename is exactly `ultron_model.glb` (case-sensitive)
- Make sure it's in the same folder as ultron_avatar_viewer.html

---

## Quick Reference

**Export Location**: `C:\Projects\ultron_agent\Avatar\ultron_model.glb`

**Required Filename**: Must be exactly `ultron_model.glb`

**Recommended Settings**:
- Format: GLB (not GLTF)
- Y Up axis
- Include textures, materials, colors
- Apply transforms

**File Path Structure**:
```
Avatar/
├── ultron+xps.blend          ← Source file
├── ultron_model.glb          ← Export here
├── ultron_avatar_viewer.html ← Open this in browser
└── export_ultron_model.py    ← Optional: Blender script
```

---

## What Happens After Export?

1. ✅ GLB file created (~1-50 MB depending on model complexity)
2. ✅ All textures embedded in single file
3. ✅ Materials and colors included
4. ✅ Web viewer can load it instantly
5. ✅ No additional setup needed

**Refresh the viewer page and your ULTRON model will appear! 🤖**
