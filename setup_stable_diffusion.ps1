# Stable Diffusion Setup (Optimized versions)

Write-Host "Stable Diffusion Setup" -ForegroundColor Cyan
Write-Host ""

$SD_DIR = "C:\Projects\stable-diffusion"

# Clone optimized Stable Diffusion
Write-Host "Cloning optimized Stable Diffusion..." -ForegroundColor Yellow
if (!(Test-Path $SD_DIR)) {
    git clone https://github.com/basujindal/stable-diffusion.git $SD_DIR
}

cd $SD_DIR

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers diffusers accelerate safetensors omegaconf

# Download model (Stable Diffusion 1.5)
Write-Host "`nDownloading Stable Diffusion 1.5 model..." -ForegroundColor Yellow
python -c "from diffusers import StableDiffusionPipeline; StableDiffusionPipeline.from_pretrained('runwayml/stable-diffusion-v1-5')"

Write-Host "`nStable Diffusion installed!" -ForegroundColor Green
Write-Host "Location: $SD_DIR" -ForegroundColor Gray
Write-Host "`nTest with: python scripts/txt2img.py --prompt 'a cat'" -ForegroundColor Cyan
