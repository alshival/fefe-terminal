import subprocess
from src import functions 

spec =     {
        "type": "function",
        "function": {
            "name": "music_player",
            "description": "Launches the user's default music player. If a path to an audio file is provided, it will begin playback of the audio file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the audio file."
                    }
                }
            }
        }
    }

def music_player(filepath = None):
    wsl = functions.is_wsl()

    if wsl:
        if filepath is None:
            subprocess.Popen(['wslopen','/usr/share/fefe/rick_roll.mp3'])
        else:
            subprocess.Popen(['wslopen', filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:        
        if filepath is None:
            subprocess.Popen(['xdg-open', '/usr/share/fefe/rick_roll.mp3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)    
        else:
            subprocess.Popen(['xdg-open', filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)