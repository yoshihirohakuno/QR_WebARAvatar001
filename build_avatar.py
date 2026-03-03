import os
import glob
import sys
import pygltflib
import base64

def get_latest_avatar_image(output_dir):
    search_pattern = os.path.join(output_dir, "avatar_face_out_*.png")
    list_of_files = glob.glob(search_pattern)
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def apply_texture(glb_path, img_path, out_path):
    print(f"Loading GLB: {glb_path}")
    gltf = pygltflib.GLTF2().load(glb_path)
    
    print(f"Loading Image: {img_path}")
    with open(img_path, "rb") as f:
        img_data = f.read()
    b64_data = base64.b64encode(img_data).decode("utf-8")
    mime = "image/png" if img_path.lower().endswith(".png") else "image/jpeg"
    uri = f"data:{mime};base64,{b64_data}"
    
    # 1. Add Image
    new_image = pygltflib.Image(mimeType=mime, uri=uri)
    gltf.images.append(new_image)
    image_idx = len(gltf.images) - 1
    
    # 2. Add Texture
    new_texture = pygltflib.Texture(source=image_idx)
    gltf.textures.append(new_texture)
    texture_idx = len(gltf.textures) - 1
    
    # 3. Apply Texture to Materials
    texture_info = pygltflib.TextureInfo(index=texture_idx)
    
    for i, material in enumerate(gltf.materials):
        if not material.pbrMetallicRoughness:
            material.pbrMetallicRoughness = pygltflib.PbrMetallicRoughness()
        material.pbrMetallicRoughness.baseColorTexture = texture_info
        print(f"Applied texture to material {i}: {material.name}")
    
    print(f"Saving final 3D Avatar GLB: {out_path}")
    gltf.save(out_path)
    print("Avatar generation success!")

if __name__ == "__main__":
    output_dir = os.path.join("ComfyUI_portable", "ComfyUI", "output")
    latest_img = get_latest_avatar_image(output_dir)
    
    if not latest_img:
        print("Error: No avatar image found. Please generate one using ComfyUI first.")
        sys.exit(1)
        
    print(f"Found latest face image: {latest_img}")
    
    base_glb = os.path.join("web", "assets", "xbot.glb")
    final_glb = os.path.join("web", "assets", "avatar.glb")
    
    if not os.path.exists(base_glb):
        print(f"Error: Base GLB model not found at {base_glb}")
        sys.exit(1)
        
    apply_texture(base_glb, latest_img, final_glb)
