import os
import sys

def check_models_directory():
    """Check the models directory and available models"""
    models_path = r"D:\models\hub"

    print("🔍 Checking Stable Diffusion Models Directory")
    print(f"Path: {models_path}")
    print("-" * 50)

    # Check if directory exists
    if not os.path.exists(models_path):
        print("❌ Models directory does not exist")
        return False

    print("✅ Models directory exists")

    try:
        # List contents
        items = os.listdir(models_path)
        print(f"📁 Found {len(items)} items:")

        ckpt_files = []
        safetensors_files = []

        for item in items:
            item_path = os.path.join(models_path, item)
            if os.path.isdir(item_path):
                print(f"  📂 {item}/")
            else:
                size_mb = os.path.getsize(item_path) / (1024 * 1024)
                if item.endswith('.ckpt'):
                    ckpt_files.append((item, size_mb))
                    print(f"  📄 {item} ({size_mb:.1f} MB) - CKPT")
                elif item.endswith('.safetensors'):
                    safetensors_files.append((item, size_mb))
                    print(f"  📄 {item} ({size_mb:.1f} MB) - SafeTensors")
                else:
                    print(f"  📄 {item} ({size_mb:.1f} MB)")

        print("\n🎯 Stable Diffusion Models Found:")
        print(f"  CKPT files: {len(ckpt_files)}")
        for name, size in ckpt_files:
            print(f"    - {name} ({size:.1f} MB)")

        print(f"  SafeTensors files: {len(safetensors_files)}")
        for name, size in safetensors_files:
            print(f"    - {name} ({size:.1f} MB)")

        if ckpt_files or safetensors_files:
            print("\n✅ Models available for image generation!")
            return True
        else:
            print("\n⚠️  No standard model files found (.ckpt or .safetensors)")
            return False

    except Exception as e:
        print(f"❌ Error accessing directory: {e}")
        return False

def check_output_directory():
    """Check the output directory"""
    output_dir = r"C:\Users\ultro\OneDrive\Pictures\STABLED"

    print("\n📂 Checking Output Directory")
    print(f"Path: {output_dir}")
    print("-" * 50)

    try:
        os.makedirs(output_dir, exist_ok=True)
        print("✅ Output directory ready")

        # Check existing files
        if os.path.exists(output_dir):
            files = [f for f in os.listdir(output_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
            print(f"📸 Existing images: {len(files)}")
            if files:
                print("  Recent files:")
                for file in sorted(files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)), reverse=True)[:3]:
                    file_path = os.path.join(output_dir, file)
                    size = os.path.getsize(file_path) / 1024  # KB
                    print(f"    - {file} ({size:.1f} KB)")
    except Exception as e:
        print(f"❌ Error with output directory: {e}")

if __name__ == "__main__":
    print("🖼️  ULTRON Agent - Stable Diffusion Setup Check")
    print("=" * 60)

    models_ok = check_models_directory()
    check_output_directory()

    print("\n" + "=" * 60)
    if models_ok:
        print("🎉 Ready for image generation!")
        print("💡 Try: 'generate image of a beautiful landscape'")
    else:
        print("⚠️  Models need to be set up for image generation")
        print("💡 Consider installing Automatic1111 WebUI or downloading models")
