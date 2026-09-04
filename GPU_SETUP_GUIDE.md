# 🎨 GPU-Accelerated Stable Diffusion Setup Guide

## 📋 Prerequisites

- ✅ NVIDIA GPU (GTX 1060 6GB or better)
- ✅ Windows 10/11
- ✅ 16GB+ RAM
- ✅ 20GB+ free disk space

## 🚀 Quick Setup (3 Steps)

### Step 1: Install NVIDIA Container Toolkit (10 min)

```powershell
.\setup_gpu_stable_diffusion.ps1
```

This installs:
- Docker Desktop (if needed)
- WSL2
- NVIDIA Container Toolkit
- GPU support for Docker

### Step 2: Install Stable Diffusion (15 min)

```powershell
.\setup_stable_diffusion.ps1
```

This installs:
- Optimized Stable Diffusion (basujindal fork)
- PyTorch with CUDA support
- Stable Diffusion 1.5 model (~4GB download)

### Step 3: Test Image Generation (2 min)

```powershell
cd C:\Projects\stable-diffusion
python scripts\txt2img.py --prompt "a beautiful sunset over mountains"
```

**Output:** `outputs/samples/00000.png`

---

## 🐳 Docker GPU Setup (Alternative)

### Start GPU-Accelerated Container

```powershell
docker-compose -f docker-compose-sd.yml up -d
```

### Generate Image in Container

```powershell
docker exec ultron-stable-diffusion python txt2img.py --prompt "a cat"
```

---

## 🔧 ULTRON Integration

### Use via ULTRON Agent

```python
# In ULTRON chat or API
"generate image of a futuristic city at night"
```

The Stable Diffusion tool will:
1. Parse your prompt
2. Generate image with GPU acceleration
3. Save to `outputs/` directory
4. Return file path

### Configuration

Edit `ultron_config.json`:

```json
{
  "stable_diffusion": {
    "enabled": true,
    "model": "runwayml/stable-diffusion-v1-5",
    "default_width": 512,
    "default_height": 512,
    "default_steps": 50,
    "output_dir": "outputs/images"
  }
}
```

---

## 📊 Performance Benchmarks

| GPU | Resolution | Steps | Time |
|-----|-----------|-------|------|
| RTX 3060 | 512x512 | 50 | ~8s |
| RTX 3070 | 512x512 | 50 | ~6s |
| RTX 3080 | 512x512 | 50 | ~4s |
| RTX 4090 | 512x512 | 50 | ~2s |

---

## 🎨 Advanced Features

### High-Resolution Images (txt2imghd)

```powershell
cd C:\Projects\txt2imghd
python txt2imghd.py --prompt "detailed landscape" --W 1024 --H 1024
```

### Batch Generation

```powershell
python scripts\txt2img.py --prompt "a cat" --n_samples 4
```

### Custom Models

```python
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2-1")
```

---

## 🔍 Troubleshooting

### GPU Not Detected

```powershell
# Check NVIDIA drivers
nvidia-smi

# Update drivers
winget install NVIDIA.GeForceExperience
```

### Docker GPU Not Working

```powershell
# Restart Docker with GPU support
wsl -e bash -c "sudo systemctl restart docker"

# Test GPU in Docker
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### Out of Memory

Reduce image size or steps:
```powershell
python scripts\txt2img.py --prompt "test" --W 256 --H 256 --ddim_steps 20
```

---

## 📚 Resources

- **Optimized SD**: https://github.com/basujindal/stable-diffusion
- **txt2imghd**: https://github.com/jquesnelle/txt2imghd
- **NVIDIA Toolkit**: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/
- **Stable Diffusion Models**: https://huggingface.co/models?pipeline_tag=text-to-image

---

## ✅ Verification Checklist

- [ ] NVIDIA GPU detected (`nvidia-smi` works)
- [ ] Docker Desktop installed
- [ ] WSL2 enabled
- [ ] NVIDIA Container Toolkit installed
- [ ] Stable Diffusion cloned
- [ ] Dependencies installed
- [ ] Model downloaded (~4GB)
- [ ] Test image generated successfully
- [ ] ULTRON tool integration working

---

## 🎯 Next Steps

1. **Generate test image** - Verify GPU acceleration works
2. **Import to Langflow** - Create image generation workflow
3. **Integrate with ULTRON** - Use via voice/chat commands
4. **Optimize settings** - Tune for your GPU

**Ready to generate images!** 🚀
