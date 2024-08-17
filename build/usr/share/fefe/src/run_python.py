import contextlib
import io
import re
from src import functions
from src import view_image

spec = {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": """
The `run_python` is meant to be versatile so that you can complete requests by executing python code. You can generate data visualizations using plotly (preferred), matplotlib, and more. Snap a photo using the user's webcam using opencv. Or plot financial charts using yfinance. Calculate metrics using sklearn. And much more!
When saving a .png file, first define the path where the image will be saved within your code in a variable called png_path1 before saving. If generating more than one .png, use `png_path1`, 'png_path2`, etc.
Similarly for jpg files (`jpg_path1`, `jpg_path2`, etc.)
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
    try:
        code_string = extract_code(code)
        
        output_buffer = io.StringIO()

        if not code_string:
            code_string = code 
        with contextlib.redirect_stdout(output_buffer):
            vars = {
                'png_path1': None,
                'png_path2': None,
                'png_path3': None,
                'png_path4': None,
                'png_path5': None,
                'jpg_path1': None,
                'jpg_path2': None,
                'jpg_path3': None,
                'jpg_path4': None,
                'jpg_path5': None,
            }
            exec(code_string,vars,vars)
        
        # Get the captured output
        captured_output = output_buffer.getvalue()
        output_buffer.close()
        
        # Handle images generated. This allows the bot to `view` what was created.
        image_content = [{"type":"text","text":f'Here are the images generated from the code.'}]
        if vars['png_path1']:
            image_content.append(view_image.view_image(vars['png_path1']))
        if vars['png_path2']:
            image_content.append(view_image.view_image(vars['png_path2']))
        if vars['png_path3']:
            image_content.append(view_image.view_image(vars['png_path3']))
        if vars['png_path4']:
            image_content.append(view_image.view_image(vars['png_path4']))
        if vars['png_path5']:
            image_content.append(view_image.view_image(vars['png_path5']))
        if vars['jpg_path1']:
            image_content.append(view_image.view_image(vars['jpg_path1']))
        if vars['jpg_path2']:
            image_content.append(view_image.view_image(vars['jpg_path2']))
        if vars['jpg_path3']:
            image_content.append(view_image.view_image(vars['jpg_path3']))
        if vars['jpg_path4']:
            image_content.append(view_image.view_image(vars['jpg_path4']))
        if vars['jpg_path5']:
            image_content.append(view_image.view_image(vars['jpg_path5']))
            

        if len(image_content) > 1:
            #functions.update_chat_history({'role':'user','content':user_json['content'] + image_content})
            user_json = functions.get_chat_message(prompt_id)
            user_json = {'role':'user','content':user_json['content'] + image_content}
            functions.update_chat_message(prompt_id,user_json)
        return code_string, captured_output
        
    except Exception as e:
        result = f'''
An error arose during code execution.

code:
```
{code_string}
```

Error:
{e}
'''
        return code_string, e