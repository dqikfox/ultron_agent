import os


def simple_model_check():
    """Simple check for models directory"""
    models_path = r"D:\models\hub"
    output_dir = r"C:\Users\ultro\OneDrive\Pictures\STABLED"

    print("🖼️  ULTRON Agent - Simple Model Check")
    print("=" * 50)

    # Check models directory
    print(f"Checking models path: {models_path}")
    if os.path.exists(models_path):
        print("✅ Models directory exists")
        try:
            items = os.listdir(models_path)
            print(f"📁 Contents: {len(items)} items")

            ckpt = [f for f in items if f.endswith('.ckpt')]
            safetensors = [f for f in items if f.endswith('.safetensors')]

            print(f"  CKPT files: {len(ckpt)}")
            print(f"  SafeTensors files: {len(safetensors)}")

            if ckpt or safetensors:
                print("✅ Models found - ready for generation!")
                return True
            else:
                print("⚠️  No model files found")
        except Exception as e:
            print(f"❌ Error reading directory: {e}")
    else:
        print("❌ Models directory does not exist")

    # Check output directory
    print(f"\nChecking output path: {output_dir}")
    if os.path.exists(output_dir):
        print("✅ Output directory exists")
        try:
            files = os.listdir(output_dir)
            images = [f for f in files if f.endswith(
                ('.png', '.jpg', '.jpeg'))]
            print(f"📸 Existing images: {len(images)}")
        except Exception as e:
            print(f"❌ Error reading output directory: {e}")
    else:
        print("❌ Output directory does not exist")
        try:
            os.makedirs(output_dir, exist_ok=True)
            print("✅ Created output directory")
        except Exception as e:
            print(f"❌ Could not create output directory: {e}")

    return False


if __name__ == "__main__":
    success = simple_model_check()
    print("\n" + "=" * 50)
    if success:
        print("🎉 System ready for image generation!")
    else:
        print("⚠️  Setup needed for image generation")
