import pygltflib
import sys

def inspect_animations(glb_path):
    gltf = pygltflib.GLTF2().load(glb_path)
    print(f"Total Animations: {len(gltf.animations)}")
    for i, anim in enumerate(gltf.animations):
        print(f"Animation {i}: {anim.name}")

if __name__ == "__main__":
    inspect_animations(sys.argv[1])
