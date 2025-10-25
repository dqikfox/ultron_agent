# ULTRON Model Export Script for Blender
# Run this inside Blender's Scripting tab

import bpy
import os

print("=" * 60)
print("ULTRON MODEL EXPORT SCRIPT")
print("=" * 60)

# Get the directory where the blend file is located
blend_file_path = bpy.data.filepath
if not blend_file_path:
    print("⚠️ ERROR: Please save your .blend file first!")
else:
    output_dir = os.path.dirname(blend_file_path)
    output_path = os.path.join(output_dir, "ultron_model.glb")

    print(f"\n📂 Export Directory: {output_dir}")
    print(f"📄 Output File: ultron_model.glb")
    print(f"\n🚀 Starting export...")

    try:
        # Export as GLB with all settings optimized
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            export_format='GLB',  # Binary format

            # Include everything
            export_textures=True,
            export_materials='EXPORT',
            export_colors=True,
            export_cameras=False,
            export_lights=False,

            # Transforms
            export_apply=True,
            export_yup=True,

            # Optimization
            export_draco_mesh_compression_enable=False,
            export_animations=True,
            export_skins=True,
            export_morph=True,

            # Other settings
            use_selection=False,  # Export everything
            use_visible=True,
            use_renderable=True,
            use_active_collection=False
        )

        print(f"\n✅ SUCCESS! Model exported to:")
        print(f"   {output_path}")
        print(f"\n📊 Export complete!")
        print(f"   - Format: GLB (Binary glTF 2.0)")
        print(f"   - Textures: Included")
        print(f"   - Materials: Included")
        print(f"   - Animations: Included")
        print(f"\n🌐 Next steps:")
        print(f"   1. Open or refresh: ultron_avatar_viewer.html")
        print(f"   2. Model will load automatically!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR during export:")
        print(f"   {str(e)}")
        print("\n💡 Troubleshooting:")
        print("   - Make sure you have objects in the scene")
        print("   - Try selecting objects before running")
        print("   - Check Blender console for details")
        print("=" * 60)
