"""
Blender script to export ULTRON model to GLB with materials
"""
import bpy
import os

print("=" * 60)
print("🤖 ULTRON Blender GLB Exporter")
print("=" * 60)

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import the blend file
blend_file = r"C:\Projects\ultron_agent\Avatar\ultron+xps.blend"
print(f"\n📂 Loading: {os.path.basename(blend_file)}")

# Load objects from blend file
with bpy.data.libraries.load(blend_file, link=False) as (data_from, data_to):
    data_to.objects = data_from.objects
    print(f"   Found {len(data_from.objects)} objects")

# Add loaded objects to scene
print("\n📦 Adding objects to scene...")
for obj in data_to.objects:
    if obj is not None:
        bpy.context.collection.objects.link(obj)
        print(f"   ✅ {obj.name}")

# Select all objects
bpy.ops.object.select_all(action='SELECT')

# Export to GLB
output_file = r"C:\Projects\ultron_agent\Avatar\ultron_exported.glb"
print(f"\n💾 Exporting to: {os.path.basename(output_file)}")

# Use minimal, guaranteed-to-work parameters
bpy.ops.export_scene.gltf(
    filepath=output_file,
    export_format='GLB'
)

print("\n✅ Export complete!")
print(f"📂 Saved to: {output_file}")
print("=" * 60)
