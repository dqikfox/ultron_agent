"""
Blender script to export ULTRON model to web-compatible format
Run this inside Blender: Scripting tab > Open > Run Script
"""

import bpy
import os

# Get the directory where the blend file is located
blend_file_path = bpy.data.filepath
blend_dir = os.path.dirname(blend_file_path)

# Output path for GLB file
output_path = os.path.join(blend_dir, "ultron_model.glb")

# Select all objects
bpy.ops.object.select_all(action='SELECT')

# Export as GLB (binary GLTF)
bpy.ops.export_scene.gltf(
    filepath=output_path,
    export_format='GLB',
    export_textures=True,
    export_materials='EXPORT',
    export_colors=True,
    export_cameras=False,
    export_lights=False,
    export_apply=True,
    export_yup=True
)

print(f"✅ Model exported successfully to: {output_path}")
print("You can now use this GLB file in the web avatar!")
