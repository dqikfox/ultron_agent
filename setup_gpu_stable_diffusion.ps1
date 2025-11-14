# GPU-Accelerated Stable Diffusion Setup
# Installs NVIDIA Container Toolkit + Stable Diffusion

Write-Host "GPU-Accelerated Stable Diffusion Setup" -ForegroundColor Cyan
Write-Host ""

# Check NVIDIA GPU
Write-Host "Checking NVIDIA GPU..." -ForegroundColor Yellow
nvidia-smi
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No NVIDIA GPU detected or drivers not installed" -ForegroundColor Red
    exit 1
}

# Install Docker Desktop (if not installed)
Write-Host "`nChecking Docker..." -ForegroundColor Yellow
docker --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing Docker Desktop..." -ForegroundColor Yellow
    winget install Docker.DockerDesktop
    Write-Host "Restart required after Docker installation" -ForegroundColor Red
    exit 0
}

# Enable WSL2 (required for Docker GPU support)
Write-Host "`nEnabling WSL2..." -ForegroundColor Yellow
wsl --install
wsl --set-default-version 2

# Install NVIDIA Container Toolkit in WSL2
Write-Host "`nInstalling NVIDIA Container Toolkit in WSL2..." -ForegroundColor Yellow
wsl -e bash -c "curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg"
wsl -e bash -c "curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list"
wsl -e bash -c "sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit"
wsl -e bash -c "sudo nvidia-ctk runtime configure --runtime=docker"
wsl -e bash -c "sudo systemctl restart docker"

Write-Host "`nNVIDIA Container Toolkit installed!" -ForegroundColor Green
Write-Host "`nNext: Run setup_stable_diffusion.ps1" -ForegroundColor Cyan
