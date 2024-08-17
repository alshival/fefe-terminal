from src import run_commands
from src import functions 
from src import view_image
from src import pdfReader
from src import run_python
from src import browser 
from src import image_gen

import fefe
import json 

available_tools = {
    'run_commands': run_commands.run_commands,
    'run_python': run_python.run_python,
    'view_image': view_image.view_image,
    'pdfReader': pdfReader.pdfReader,
    'browser': browser.browser,
    'image_gen': image_gen.image_gen,
}

tools = [
    run_commands.spec,
    run_python.spec,
    view_image.spec,
    pdfReader.spec,
    browser.spec,
    image_gen.spec,
    ]

def handle_tool_calls(prompt_id,tool_calls,source='fefe'):
    assistant_content = []
    system_content = []

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        #print(function_name)
        function_to_call = available_tools.get(function_name,None)
        try:
            function_args = json.loads(tool_call.function.arguments)
        except Exception as e:
            function_args = {'code':tool_call.function.arguments}
        # print(f'arguments: {function_args}')
        functions.update_chat_history({'role':'assistant','content':f'''
tool call: {function_name}

arguments: {function_args}
'''})
        
        if function_name == 'run_commands':
            function_response = function_to_call(
                commands = function_args.get("commands"),
                verbose = function_args.get("verbose",False)
            )
            system_content.append({'role':'system','content':f'''

Result of `run_commands` executed by the assistant:
```
{function_response}
```
Let the user know how the command execution went. If the command requires intervention, notify the user.
'''})
            
        if function_name == 'run_python':
            arguments = function_args.get('code')
            if arguments is None:
                arguments = function_args
            code, output = function_to_call(
                prompt_id = prompt_id,
                code = arguments
            )
            assistant_content.append({'role':'assistant','content': f'Executed python code:\n```\n{code}\n```'})
            system_content.append({'role':'system','content':f'''Output of code run by assistant:\n```\n{output}\n```'''})
            
        if function_name == 'view_image':
            image_content = function_to_call(
                filepath = function_args.get('filepath')
            )
            user_json = functions.get_chat_message(prompt_id)
            user_json = {'role':'user','content': user_json['content'] + [image_content]}
            functions.update_chat_message(prompt_id,user_json)
            system_content.append({'role':'system','content':f"Image encoded for the user: {function_args.get('filepath')}"})
        
        if function_name == 'pdfReader':
            pdfText = function_to_call(
                filepath = function_args.get('filepath')
            )
            system_content.append({'role':'system','content':f"The content of the PDF {function_args.get('filepath')}:\n\n{pdfText}"})

        if function_name == 'browser':
            try:
                url_data = function_to_call(
                    url = function_args.get('url'),
                    open_for_user = function_args.get('open_for_user',False)
                )
                system_content.append({"role": "system", "content": f'''
Contents of {function_args.get("url")}:
{url_data}
'''
})
            except Exception as e:
                system_content.append({"role":"system","content":f"There was an issue fetching the information from {function_args.get("url")} \n Error: \n{e}"})

        if function_name == 'image_gen':
            code, error = function_to_call(
                prompt = function_args.get('prompt'),
                filepath = function_args.get('filepath')
            )
            if code:
                system_content.append({'role':'system','content':'Image generation complete.'})
            else:
                system_content.append({'role':'system','content':f'There was an error generating the image: {e}'})

    if len(assistant_content) > 0:
        for x in assistant_content:
            functions.update_chat_history(x,source)
    if len(system_content) > 0:
        for x in system_content:
            functions.update_chat_history(x,source)
        fefe.respond_to_chat(prompt_id)
    