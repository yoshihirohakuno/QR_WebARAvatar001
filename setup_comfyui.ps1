# ComfyUI Portable Environment Setup Script (Windows)

$ComfyUIUrl = "https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia_cu121_or_cpu.7z"
$ZipName = "ComfyUI_windows_portable.7z"
$InstallDir = "C:\Users\yoshi\.gemini\antigravity\playground\tachyon-apogee\webar-avatar\ComfyUI_portable"

Write-Host "Creating directory..."
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

Write-Host "Downloading ComfyUI Portable (This may take a while, it is over 1GB)..."
# Using Invoke-WebRequest for downloading
Invoke-WebRequest -Uri $ComfyUIUrl -OutFile "$InstallDir\$ZipName"

Write-Host "Please extract the downloaded 7z file ($InstallDir\$ZipName) using 7-Zip."
Write-Host "After extraction, you can run run_nvidia_gpu.bat in the extracted folder to start ComfyUI."
Write-Host "Setup script finished."
