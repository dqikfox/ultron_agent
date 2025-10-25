# 🎨 Using the Blender ULTRON Model

## 📁 Files Overview

- **ultron+xps.blend** - Original Blender 3D model file
- **export_to_web.py** - Python script to export model for web
- **ultron_avatar_blender.html** - Web viewer for the exported model
- **ultron_avatar.html** - Procedurally generated avatar (no model needed)

## 🚀 Quick Start - Export & View

### Step 1: Open Blender Model

1. Open Blender (download from https://www.blender.org if needed)
2. File → Open → Select `ultron+xps.blend`
3. The ULTRON model should appear in the viewport

### Step 2: Export to Web Format (GLB)

**Option A: Using the Python Script (Recommended)**

1. In Blender, switch to the **Scripting** tab (top menu)
2. Click **Open** button
3. Navigate to `C:\Projects\ultron_agent\Avatar\`
4. Select `export_to_web.py`
5. Click **Run Script** button (▶️ icon)
6. Wait for "Model exported successfully" message
7. A new file `ultron_model.glb` will be created in the Avatar folder

**Option B: Manual Export**

1. In Blender: File → Export → glTF 2.0 (.glb/.gltf)
2. Set filename: `ultron_model.glb`
3. Save location: `C:\Projects\ultron_agent\Avatar\`
4. Format: **glTF Binary (.glb)**
5. Include: ✓ Textures, ✓ Materials, ✓ Animations
6. Click **Export glTF 2.0**

### Step 3: View in Browser

```powershell
# Open the viewer
Invoke-Item "C:\Projects\ultron_agent\Avatar\ultron_avatar_blender.html"

# Or use a local server (recommended for best performance)
cd C:\Projects\ultron_agent\Avatar
python -m http.server 8888
# Then open: http://localhost:8888/ultron_avatar_blender.html
```

## 🎮 Viewer Controls

Once loaded, you can:

- **🖱️ Left Click + Drag**: Rotate camera around model
- **🖱️ Right Click + Drag**: Pan camera
- **🖱️ Scroll**: Zoom in/out
- **Rotation Speed Slider**: Control auto-rotation speed
- **Zoom Slider**: Adjust camera distance
- **⏯️ Toggle Rotation**: Start/stop auto-rotation
- **🔲 Toggle Wireframe**: View model geometry
- **📷 Reset View**: Return to default camera position
- **💡 Cycle Lighting**: Switch between 3 lighting themes:
  - Green (ULTRON signature)
  - Blue (Tech/Cool)
  - Red (Alert mode)

## 📊 Model Information

The status panel (bottom-left) displays:
- **MODEL**: Loading status
- **VERTICES**: Number of vertices in the model
- **FACES**: Number of triangular faces
- **MATERIALS**: Number of unique materials
- **FPS**: Real-time rendering performance

## 🔧 Troubleshooting

### "ERROR LOADING MODEL" Message

**Problem**: The GLB file doesn't exist or can't be found

**Solution**:
1. Make sure you exported the model first (Step 2 above)
2. Check that `ultron_model.glb` exists in the Avatar folder
3. If using file:// protocol, some browsers block loading. Use a local server instead:
   ```powershell
   python -m http.server 8888
   ```

### Model Appears Tiny or Huge

**Problem**: Scale issues from Blender export

**Solution**: The viewer automatically scales the model to fit. If it still looks wrong:
1. In Blender: Edit → Preferences → Add-ons → Search "glTF"
2. Enable glTF exporter options
3. Re-export with "Apply Transforms" enabled

### Textures Not Showing

**Problem**: Texture files not embedded or found

**Solution**:
1. In Blender, pack all textures: File → External Data → Pack Resources
2. Save the blend file
3. Re-export to GLB

### Low FPS / Laggy

**Problem**: Model too complex or GPU limitations

**Solution**:
1. In Blender, reduce polygon count:
   - Select model → Modifiers → Add Modifier → Decimate
   - Set Ratio to 0.5 (reduces polys by 50%)
2. Reduce texture sizes
3. Disable shadows in viewer (edit HTML, set `shadowMap.enabled = false`)

## 🎨 Customizing the Model in Blender

### Add Animations

1. Select the model in Blender
2. Switch to **Animation** tab
3. Create keyframes for movements
4. Export with animations (they'll play automatically in viewer)

### Change Materials/Colors

1. Switch to **Shading** tab
2. Select a mesh part
3. Adjust material properties in Shader Editor
4. Re-export

### Add Glow Effects

1. Select object → Material Properties
2. Scroll to Emission
3. Set Emission color (e.g., green #00ff41)
4. Increase Strength (2.0+)
5. Re-export

## 🔗 Integration Ideas

### Option 1: Replace Procedural Avatar
Replace the geometric shapes in `ultron_avatar.html` with the GLB model:
```javascript
const loader = new THREE.GLTFLoader();
loader.load('ultron_model.glb', (gltf) => {
    this.model = gltf.scene;
    this.scene.add(this.model);
});
```

### Option 2: Embed in Main ULTRON GUI
Add the viewer as an iframe in the Pokédex interface:
```html
<iframe src="Avatar/ultron_avatar_blender.html" width="400" height="400"></iframe>
```

### Option 3: WebSocket Integration
Connect model animations to agent state:
```javascript
// In ultron_avatar_blender.html
const ws = new WebSocket('ws://localhost:8080/ws');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.event === 'speaking') {
        // Trigger animation
    }
};
```

## 📝 File Formats Explained

- **.blend**: Blender's native format (editable)
- **.glb**: Binary glTF (web-optimized, includes everything)
- **.gltf**: Text glTF (separate files for textures/data)
- **.obj**: Wavefront format (geometry only, no materials)
- **.fbx**: Autodesk format (animations, less web-friendly)

**For web use: GLB is recommended** ✓

## 🎯 Next Steps

1. ✅ Export model from Blender to GLB
2. ✅ Test in `ultron_avatar_blender.html`
3. 🔜 Integrate with main ULTRON GUI
4. 🔜 Add voice-synced animations
5. 🔜 Create emotion-based poses

## 💡 Tips

- **Performance**: GLB files should be under 10 MB for web
- **Textures**: Use power-of-2 sizes (256, 512, 1024, 2048)
- **Animations**: Keep under 30 seconds for smooth looping
- **Testing**: Always test exported models before integration

## 🆘 Need Help?

If you encounter issues:
1. Check Blender console for export errors (Window → Toggle System Console)
2. Check browser console for loading errors (F12)
3. Verify GLB file was created and is not 0 bytes
4. Try opening GLB in a viewer: https://gltf-viewer.donmccurdy.com/

---

**Ready to proceed?** Follow Step 1-3 above to export and view your ULTRON model! 🚀
