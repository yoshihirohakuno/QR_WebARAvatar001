import os
import urllib.request
import subprocess
import sys

# Directory setup
COMFY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ComfyUI_portable", "ComfyUI")
CUSTOM_NODES_DIR = os.path.join(COMFY_DIR, "custom_nodes")
MODELS_DIR = os.path.join(COMFY_DIR, "models")

CHECKPOINTS_DIR = os.path.join(MODELS_DIR, "checkpoints")
CLIP_VISION_DIR = os.path.join(MODELS_DIR, "clip_vision")
IPADAPTER_DIR = os.path.join(MODELS_DIR, "ipadapter")

os.makedirs(CHECKPOINTS_DIR, exist_ok=True)
os.makedirs(CLIP_VISION_DIR, exist_ok=True)
os.makedirs(IPADAPTER_DIR, exist_ok=True)

def download_file(url, target_path, desc):
    if os.path.exists(target_path):
        print(f"✅ {desc} is already downloaded: {os.path.basename(target_path)}")
        return
    print(f"⬇️ Downloading {desc}...")
    try:
        urllib.request.urlretrieve(url, target_path)
        print(f"🎉 Successfully downloaded {desc}!")
    except Exception as e:
        print(f"❌ Failed to download {desc}: {e}")

def git_clone(repo_url, target_dir, desc):
    if os.path.exists(target_dir):
        print(f"✅ {desc} is already installed.")
        return
    print(f"📦 Installing {desc}...")
    try:
        subprocess.run(["git", "clone", repo_url, target_dir], check=True)
        print(f"🎉 Successfully installed {desc}!")
    except Exception as e:
        print(f"❌ Failed to install {desc}: {e}")

def install_requirements(node_dir):
    req_file = os.path.join(node_dir, "requirements.txt")
    if os.path.exists(req_file):
        print(f"⚙️ Installing Python dependencies for {os.path.basename(node_dir)}...")
        python_exe = os.path.join(os.path.dirname(COMFY_DIR), "python_embeded", "python.exe")
        subprocess.run([python_exe, "-m", "pip", "install", "-r", req_file], check=False)

print("==================================================")
print("  🚀 Setting up ComfyUI Avatar Pipeline (IP-Adapter)")
print("==================================================")

# 1. Download Base SD1.5 Checkpoint (DreamShaper is great for avatars)
download_file(
    "https://huggingface.co/Lykon/DreamShaper/resolve/main/DreamShaper_8_pruned.safetensors",
    os.path.join(CHECKPOINTS_DIR, "dreamshaper_8_pruned.safetensors"),
    "DreamShaper 8 Checkpoint"
)

# 2. Download CLIP Vision Model (Required for IP-Adapter)
download_file(
    "https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors",
    os.path.join(CLIP_VISION_DIR, "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"),
    "CLIP Vision Model (ViT-H)"
)

# 3. Download IP-Adapter Model (Standard SD1.5)
download_file(
    "https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter_sd15.safetensors",
    os.path.join(IPADAPTER_DIR, "ip-adapter_sd15.safetensors"),
    "IP-Adapter SD1.5 Model"
)

# 4. Install IP-Adapter Plus Custom Node
ipadapter_node_dir = os.path.join(CUSTOM_NODES_DIR, "ComfyUI_IPAdapter_plus")
git_clone("https://github.com/cubiq/ComfyUI_IPAdapter_plus.git", ipadapter_node_dir, "IP-Adapter-Plus Node")

# 5. Install RemBG (Background Removal) Custom Node
rembg_node_dir = os.path.join(CUSTOM_NODES_DIR, "ComfyUI-rembg")
git_clone("https://github.com/jtydhr88/ComfyUI-rembg.git", rembg_node_dir, "RemBG Node")
install_requirements(rembg_node_dir)

print("==================================================")
print("  ✅ Setup Complete! Please restart ComfyUI.")
print("==================================================")
