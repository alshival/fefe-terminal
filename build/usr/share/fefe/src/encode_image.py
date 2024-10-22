import json 
import base64
from src import functions

spec = {
        "type": "function",
        "function": {
            "name": "encode_image",
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
def encode_file(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def encode_image(filepath):
   base64_image = encode_file(filepath)
   filetype = functions.filetype(filepath)
   if filetype == 'jpg':
     filetype = 'jpeg'
   try:
     payload = {
       "type": "image_url",
       "image_url": {"url": f"data:image/{filetype};base64,{base64_image}"}
       }
     return payload 
   except:
     raise RuntimeError(f"Failed to encode the image from {filepath}")