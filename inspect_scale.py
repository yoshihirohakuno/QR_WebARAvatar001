import pygltflib
import sys

def inspect_scale(glb_path):
    gltf = pygltflib.GLTF2().load(glb_path)
    
    print("--- Nodes ---")
    for i, node in enumerate(gltf.nodes):
        if node.mesh is not None or node.skin is not None or node.scale is not None:
             print(f"Node {i}: name={node.name}, scale={node.scale}, translation={node.translation}")
    
    print("\n--- Accessors (Position Min/Max) ---")
    for i, mesh in enumerate(gltf.meshes):
        for j, primitive in enumerate(mesh.primitives):
            pos_acc_idx = primitive.attributes.POSITION
            if pos_acc_idx is not None:
                acc = gltf.accessors[pos_acc_idx]
                print(f"Mesh {i} Primitive {j}: min={acc.min}, max={acc.max}")

if __name__ == "__main__":
    inspect_scale("web/assets/avatar.glb")
