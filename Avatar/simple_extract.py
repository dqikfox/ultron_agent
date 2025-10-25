"""
Simple Unity asset extractor using UnityPy export
"""
import UnityPy
from pathlib import Path

# Path to the mesh asset (largest file - 1.25MB)
mesh_asset = r"C:\Projects\ultron_agent\Avatar\Unity_Ultron\6fbbc664ae83ba448b343c02edc8417d\asset"
texture_asset = r"C:\Projects\ultron_agent\Avatar\Unity_Ultron\01ecf119a310fda498582ce0da2733bb\asset"
output_dir = Path(r"C:\Projects\ultron_agent\Avatar\Unity_Extracted")
output_dir.mkdir(exist_ok=True)

print("=" * 60)
print("🤖 ULTRON Simple Unity Extractor")
print("=" * 60)

# Extract mesh
print("\n📦 Extracting mesh...")
try:
    env = UnityPy.load(mesh_asset)

    for obj in env.objects:
        print(f"   Object type: {obj.type} (Class ID: {obj.type.value})")

        if obj.type.name == "Mesh" or obj.type.value == 43:
            data = obj.read()
            print(f"   ✅ Found mesh: {data.name if hasattr(data, 'name') else 'Unknown'}")

            # Try to export using UnityPy's built-in export
            dest = output_dir / f"ultron_mesh.obj"
            try:
                with open(dest, 'wb') as f:
                    f.write(data.export())
                print(f"   💾 Exported to: {dest.name}")
            except Exception as e:
                print(f"   ❌ Export failed: {e}")
                print(f"   Available attributes: {dir(data)[:10]}")

except Exception as e:
    print(f"❌ Error loading mesh: {e}")

# Extract texture
print("\n🖼️  Extracting texture...")
try:
    env = UnityPy.load(texture_asset)

    for obj in env.objects:
        if obj.type.name == "Texture2D":
            data = obj.read()
            print(f"   ✅ Found texture: {data.name}")

            try:
                image = data.image
                dest = output_dir / f"{data.name}.png"
                image.save(dest)
                print(f"   💾 Saved to: {dest.name}")
            except Exception as e:
                print(f"   ❌ Save failed: {e}")

except Exception as e:
    print(f"❌ Error loading texture: {e}")

print("\n" + "=" * 60)
print("✅ Extraction complete!")
print(f"📂 Check: {output_dir}")
print("=" * 60)
