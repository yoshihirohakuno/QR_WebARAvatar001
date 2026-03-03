import pygltflib

def inspect_details(glb_path):
    gltf = pygltflib.GLTF2().load(glb_path)
    print(f"Images: {len(gltf.images)}")
    for i, img in enumerate(gltf.images):
        print(f"Image {i}: name={img.name}, mime={img.mimeType}, uri={img.uri[:30] if img.uri else 'None'}, bufferView={img.bufferView}")

    print(f"Textures: {len(gltf.textures)}")
    for i, tex in enumerate(gltf.textures):
        print(f"Texture {i}: name={tex.name}, source={tex.source}")

    for i, material in enumerate(gltf.materials):
        print(f"Material {i}: {material.name}")
        if material.pbrMetallicRoughness and material.pbrMetallicRoughness.baseColorTexture:
            print(f"  Texture index: {material.pbrMetallicRoughness.baseColorTexture.index}")

if __name__ == "__main__":
    inspect_details("web/assets/xbot.glb")
