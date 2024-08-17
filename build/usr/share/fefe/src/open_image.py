import os
import platform
import subprocess

def open_image(image_path):
    """
    Opens an image file using the user's default photo app based on the operating system.

    Args:
        image_path (str): The path to the image file to be opened.
    """
    system_name = platform.system()
    
    if system_name == 'Windows':
        os.startfile(image_path)
    elif system_name == 'Darwin':  # macOS
        subprocess.run(['open', image_path])
    elif system_name == 'Linux':
        subprocess.run(['xdg-open', image_path])
    else:
        raise NotImplementedError(f"Opening images is not supported on {system_name} systems.")

# Example usage:
# open_image('path/to/your/image.png')
