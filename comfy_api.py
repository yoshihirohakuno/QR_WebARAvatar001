import json
import urllib.request
import urllib.parse
from PIL import Image
import io
import os
import uuid
import requests
import time

class ComfyUIAPI:
    def __init__(self, server_address="127.0.0.1:8188"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())

    def queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        try:
            return json.loads(urllib.request.urlopen(req).read())
        except urllib.error.HTTPError as e:
            print(f"ComfyUI API Error: {e.code}")
            print(e.read().decode('utf-8'))
            raise

    def get_image(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(f"http://{self.server_address}/view?{url_values}") as response:
            return response.read()

    def get_history(self, prompt_id):
        with urllib.request.urlopen(f"http://{self.server_address}/history/{prompt_id}") as response:
            return json.loads(response.read())

    def upload_image(self, filepath, image_type="input", overwrite=True):
        with open(filepath, "rb") as f:
            files = {"image": f}
            data = {"type": image_type, "overwrite": str(overwrite).lower()}
            response = requests.post(f"http://{self.server_address}/upload/image", files=files, data=data)
            return response.json()

    def generate_face(self, workflow_json_path, input_image_path):
        print(f"Uploading input image: {input_image_path}")
        upload_resp = self.upload_image(input_image_path)
        uploaded_filename = upload_resp["name"]
        print(f"Uploaded as: {uploaded_filename}")
        
        with open(workflow_json_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
            
        # Modify workflow json to use uploaded image
        # Basic mapping - finding the exact LoadImage node
        for node_id in workflow:
            if workflow[node_id]["class_type"] == "LoadImage":
                workflow[node_id]["inputs"]["image"] = uploaded_filename
                
        print("Queueing prompt...")
        prompt_res = self.queue_prompt(workflow)
        prompt_id = prompt_res['prompt_id']
        
        print(f"Prompt queued, ID: {prompt_id}. Waiting for completion...")
        # Polling history
        while True:
            history = self.get_history(prompt_id)
            if prompt_id in history:
                print("Generation complete!")
                break
            time.sleep(1)
            
        # Extract Output Image
        outputs = history[prompt_id]['outputs']
        for node_id in outputs:
            node_output = outputs[node_id]
            if 'images' in node_output:
                for image in node_output['images']:
                    image_data = self.get_image(image['filename'], image['subfolder'], image['type'])
                    output_path = os.path.join(os.path.dirname(input_image_path), "generated_face.png")
                    with open(output_path, "wb") as f:
                        f.write(image_data)
                    print(f"Saved generated image to: {output_path}")
                    return output_path
        return None
