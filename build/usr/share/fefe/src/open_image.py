import os
import platform
import subprocess
from src import functions 

spec =     {
        "type": "function",
        "function": {
            "name": "open_image",
            "description": "Opens an image for a user in their default photo viewer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the image."
                    }
                },
                "required": ["filepath"]
            }
        }
    }

def open_image(filepath):
    """
    Opens an image file using the user's default photo app based on the operating system.

    Args:
        image_path (str): The path to the image file to be opened.
    """
    system_name = platform.system()
    
    if system_name == 'Windows':
        os.startfile(filepath)
    elif system_name == 'Darwin':  # macOS
        subprocess.run(['open', filepath])
    elif system_name == 'Linux':
        wsl = functions.is_wsl()
        if wsl:
            subprocess.run(['wslview',filepath])
        else:
            subprocess.run(['xdg-open', filepath])
    else:
        raise NotImplementedError(f"Opening images is not supported on {system_name} systems.")

# Example usage:
# open_image('path/to/your/image.png')
