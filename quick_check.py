import os

models_path = r"D:\models\hub"
print(f"Checking models directory: {models_path}")
print(f"Directory exists: {os.path.exists(models_path)}")

if os.path.exists(models_path):
    try:
        items = os.listdir(models_path)
        print(f"Items found: {len(items)}")
        ckpt = [f for f in items if f.endswith('.ckpt')]
        safetensors = [f for f in items if f.endswith('.safetensors')]
        print(f"CKPT files: {len(ckpt)}")
        print(f"SafeTensors files: {len(safetensors)}")
        if ckpt:
            print("CKPT files:", ckpt[:3])  # Show first 3
        if safetensors:
            print("SafeTensors files:", safetensors[:3])  # Show first 3
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Directory does not exist")
