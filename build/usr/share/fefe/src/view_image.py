import json 
import base64
from src import functions

spec = {
        "type": "function",
        "function": {
            "name": "view_image",
            "description": 
f"""
Allows the assistant to view image on the user's system.
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the image. For better results, use full paths."
                    }
                },
                "required": ["filepath"]
            }
        }
    }

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def view_image(filepath):
  base64_image = encode_image(filepath)
  return {
      "type": "image_url",
      "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
  }