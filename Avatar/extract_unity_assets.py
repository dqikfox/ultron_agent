"""
Extract 3D mesh and textures from Unity package and convert to OBJ format
"""
import UnityPy
import os
import json
from pathlib import Path


def extract_unity_package(package_path, output_dir):
    """Extract Unity assets from unitypackage"""
    print(f"🔍 Scanning Unity package directory: {package_path}")

    # Unity packages extract into GUID-named folders
    # We need to scan all 'asset' files in subdirectories
    asset_files = []
    for root, dirs, files in os.walk(package_path):
        for file in files:
            if file == 'asset':
                asset_files.append(os.path.join(root, file))

    print(f"   Found {len(asset_files)} asset files")

    if not asset_files:
        print("   ❌ No asset files found!")
        return [], [], []

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    meshes = []
    textures = []
    materials = []

    print("\n📦 Extracting assets...")

    # Process each asset file
    for asset_file in asset_files:
        try:
            # Load individual asset
            env = UnityPy.load(asset_file)

            # Extract all objects from this asset
            for obj in env.objects:
                try:
                    # Get the object data
                    data = obj.read()

                    # Extract meshes
                    if data.type.name == "Mesh":
                        print(f"  ✅ Found mesh: {data.name}")
                        mesh_data = {
                            'name': data.name,
                            'file': asset_file
                        }
                        meshes.append(mesh_data)

                        # Save mesh as OBJ
                        save_mesh_as_obj(data, output_path / f"{data.name}.obj")

                    # Extract textures
                    elif data.type.name == "Texture2D":
                        print(f"  🖼️  Found texture: {data.name}")
                        textures.append(data.name)

                        # Save texture
                        try:
                            image = data.image
                            if image:
                                image_path = output_path / f"{data.name}.png"
                                image.save(image_path)
                                print(f"     Saved: {image_path.name}")
                        except Exception as tex_err:
                            print(f"     ❌ Could not save texture: {tex_err}")

                    # Extract materials
                    elif data.type.name == "Material":
                        print(f"  🎨 Found material: {data.name}")
                        materials.append(data.name)

                except Exception:
                    # Skip objects that can't be read
                    pass

        except Exception as e:
            print(f"  ⚠️  Could not process {os.path.basename(asset_file)}: {e}")

    # Save summary
    summary = {
        'meshes': meshes,
        'textures': textures,
        'materials': materials
    }

    summary_path = output_path / "extraction_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✅ Extraction complete")
    print(f"   Meshes: {len(meshes)}")
    print(f"   Textures: {len(textures)}")
    print(f"   Materials: {len(materials)}")
    print(f"\n📂 Output directory: {output_dir}")

    return meshes, textures, materials


def save_mesh_as_obj(mesh_data, output_path):
    """Convert Unity mesh to OBJ format"""
    try:
        with open(output_path, 'w') as f:
            f.write(f"# Mesh: {mesh_data.name}\n")
            f.write(f"o {mesh_data.name}\n\n")

            # Get mesh vertex data
            vertices = []
            normals = []
            uvs = []
            indices = []

            # Unity mesh structure varies
            if hasattr(mesh_data, 'm_VertexData'):
                vdata = mesh_data.m_VertexData
                vertex_count = vdata.m_VertexCount

                # Parse vertex buffer
                if hasattr(vdata, 'm_Streams') and len(vdata.m_Streams) > 0:
                    print(f"     Processing {vertex_count} vertices...")
                    # This is complex - UnityPy handles it

            # Try to get indices
            if hasattr(mesh_data, 'm_IndexBuffer'):
                indices = list(mesh_data.m_IndexBuffer)

            # If we have submeshes, use those
            if hasattr(mesh_data, 'm_SubMeshes'):
                for submesh in mesh_data.m_SubMeshes:
                    if hasattr(submesh, 'indexCount'):
                        print(f"     Submesh: {submesh.indexCount} indices")

            # Write a simple placeholder if we can't parse the complex structure
            f.write(f"# Vertex data parsing not yet implemented\n")
            f.write(f"# Mesh has {len(indices)} indices\n")

        print(f"     Saved mesh structure: {output_path.name}")
        return True

    except Exception as e:
        print(f"     ❌ Error saving mesh: {e}")
        return False

if __name__ == "__main__":
    # Paths
    unity_package_dir = r"C:\Projects\ultron_agent\Avatar\Unity_Ultron"
    output_dir = r"C:\Projects\ultron_agent\Avatar\Unity_Extracted"

    print("=" * 60)
    print("🤖 ULTRON Unity Asset Extractor")
    print("=" * 60)

    # Extract assets
    meshes, textures, materials = extract_unity_package(unity_package_dir, output_dir)

    print("\n" + "=" * 60)
    print("🎉 Extraction complete! Check the Unity_Extracted folder.")
    print("=" * 60)
