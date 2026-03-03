import argparse
import os
import sys
from PIL import Image
import io
import struct

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from comfy_api import ComfyUIAPI
import pygltflib

def replace_texture_in_glb(glb_path, face_image_path, output_path):
    print(f"Loading GLB model: {glb_path}")
    gltf = pygltflib.GLTF2().load(glb_path)
    
    # Process original face image to bytes
    with Image.open(face_image_path) as img:
        img = img.convert("RGB")
        # Resize face to a reasonable texture size or just apply it
        img = img.resize((512, 512))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        face_bytes = img_byte_arr.getvalue()

    if not gltf.materials:
        print("No materials found in the GLB.")
        return False
        
    print(f"Modifying GLB. Appending generated face texture...")
    
    # Append the image bytes to the binary blob
    new_byte_offset = len(gltf.binary_blob())
    gltf.set_binary_blob(gltf.binary_blob() + face_bytes)
    
    # Create BufferView
    new_buffer_view = pygltflib.BufferView(
        buffer=0,
        byteOffset=new_byte_offset,
        byteLength=len(face_bytes)
    )
    gltf.bufferViews.append(new_buffer_view)
    buffer_view_idx = len(gltf.bufferViews) - 1
    
    # Create Image
    new_image = pygltflib.Image(
        bufferView=buffer_view_idx,
        mimeType="image/jpeg"
    )
    gltf.images.append(new_image)
    image_idx = len(gltf.images) - 1
    
    # Create Sampler
    new_sampler = pygltflib.Sampler()
    gltf.samplers.append(new_sampler)
    sampler_idx = len(gltf.samplers) - 1
    
    # Create Texture
    new_texture = pygltflib.Texture(
        sampler=sampler_idx,
        source=image_idx
    )
    gltf.textures.append(new_texture)
    texture_idx = len(gltf.textures) - 1
    
    # Apply to the first material (Dummy MVP approach)
    # Target "Beta_Surface" or "Body" if known, otherwise just use material 0
    target_mat = gltf.materials[0]
    if target_mat.pbrMetallicRoughness is None:
        target_mat.pbrMetallicRoughness = pygltflib.PbrMetallicRoughness()
    target_mat.pbrMetallicRoughness.baseColorTexture = pygltflib.TextureInfo(index=texture_idx)
    target_mat.pbrMetallicRoughness.baseColorFactor = [1.0, 1.0, 1.0, 1.0]
    
    print(f"Texture applied to material '{target_mat.name}'. Saving to {output_path}")
    gltf.save(output_path)
    
    # Check size requirement (3MB limit)
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Output GLB size: {size_mb:.2f} MB")
    if size_mb > 3.0:
        print("WARNING: Output exceeds 3MB requirement!")
    return True

def main():
    parser = argparse.ArgumentParser(description="WebAR Avatar Generation Pipeline")
    parser.add_argument("--input", required=True, help="Path to input face image")
    parser.add_argument("--gender", choices=["male", "female"], default="male", help="Gender of the person")
    parser.add_argument("--base_model", default="web/assets/avatar.glb", help="Path to the base 3D glb model")
    
    args = parser.parse_args()
    
    print(f"Starting pipeline for input image: {args.input}")
    
    comfy = ComfyUIAPI()
    workflow_path = "workflow_avatar.json"
    
    generated_face_path = comfy.generate_face(workflow_path, args.input)
    
    if not generated_face_path:
        print("Error during face generation.")
        return
        
    print(f"Face generation successful: {generated_face_path}")
    
    print("Step 2: Processing 3D Model...")
    output_glb_path = "web/assets/avatar_generated.glb"
    
    success = replace_texture_in_glb(args.base_model, generated_face_path, output_glb_path)
    
    if success:
        print("Step 3: Updating frontend configuration...")
        # Since frontend loads avatar.glb, we replace it or rename
        import shutil
        shutil.copyfile(output_glb_path, "web/assets/avatar.glb")
        print("Pipeline finished successfully. WebAR is ready to test.")
    else:
        print("Failed to process 3D model.")

if __name__ == "__main__":
    main()
