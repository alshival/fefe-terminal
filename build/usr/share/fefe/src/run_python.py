import contextlib
import io
import os
import re
from src import functions
from src import encode_image

spec = {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": """
The `run_python` is meant to be versatile so that you can complete requests by executing python code. You can generate data visualizations using plotly (preferred), matplotlib, and more. Snap a photo using the user's webcam using opencv. Or plot financial charts using yfinance. Calculate metrics using sklearn. And much more!
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute, wrapped in a code block."
                    }
                },
                "required": ["code"]
            }
        }
    }

def extract_code(response_text):
    pattern = r"```(?:[a-z]*\s*)?(.*?)```\s*"
    match = re.search(pattern, response_text, re.DOTALL)
    if match:
        extracted_code = match.group(1) # Get the content between the tags\n",
    else:
        return None
    return re.sub(';','',extracted_code)


def run_python(prompt_id,code):
    code_string = extract_code(code)
    
    output_buffer = io.StringIO()

    if not code_string:
        code_string = code 

    vars = {}

    with contextlib.redirect_stdout(output_buffer):
        exec(code_string,vars,vars)
    
    # Get the captured output
    captured_output = output_buffer.getvalue()
    output_buffer.close()
    
    # # Handle images generated. This allows the bot to `view` what was created. 
    # # Commenting it out for now because it does increase token usage.
    # image_content = [{"type":"text","text":f'Here are the images generated from the code.'}]
    # images = [x for x in [y for y in vars.keys() if type(vars[y]) in [str,os.PathLike, bytes]] if functions.filetype(vars[x]) in ['png', 'jpg', 'webp', 'bmp', 'tiff', 'tif', 'heif', 'heic', 'svg', 'ico']]
    # for image in images:
    #     image_content.append(encode_image.encode_image(vars[image]))

    # if len(image_content) > 1:
    #     #functions.update_chat_history({'role':'user','content':user_json['content'] + image_content})
    #     user_json = functions.get_chat_message(prompt_id)
    #     user_json = {'role':'user','content':user_json['content'] + image_content}
    #     functions.update_chat_message(prompt_id,user_json)
    return code_string, captured_output
    