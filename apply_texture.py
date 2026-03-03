import pygltflib
import base64
import sys
import os

def apply_texture(glb_path, img_path, out_path):
    print(f"Loading GLB: {glb_path}")
    gltf = pygltflib.GLTF2().load(glb_path)
    
    print(f"Loading Image: {img_path}")
    with open(img_path, "rb") as f:
        img_data = f.read()
    b64_data = base64.b64encode(img_data).decode("utf-8")
    
    # xbot has exactly one image at index 0. Replace it.
    img = gltf.images[0]
    
    # Update mime and uri
    mime = "image/png" if img_path.lower().endswith(".png") else "image/jpeg"
    img.mimeType = mime
    img.uri = f"data:{mime};base64,{b64_data}"
    
    # Remove bufferView reference so it uses the URI instead
    img.bufferView = None
    
    print(f"Saving new GLB: {out_path}")
    gltf.save(out_path)
    print("Done!")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python apply_texture.py <input.glb> <texture.png> <output.glb>")
        # Default test
        apply_texture("web/assets/xbot.glb", "dummy_user_face.png", "web/assets/avatar_test.glb")
    else:
        apply_texture(sys.argv[1], sys.argv[2], sys.argv[3])
