from src import run_commands
from src import functions 
from src import view_image
from src import documentReader
from src import run_python
from src import browser 
from src import image_gen
from src import open_image

import fefe
import json 

available_tools = {
    'run_commands': run_commands.run_commands,
    'run_python': run_python.run_python,
    'view_image': view_image.view_image,
    'documentReader': documentReader.documentReader,
    'browser': browser.browser,
    'image_gen': image_gen.image_gen,
    'open_image': open_image.open_image
}

tools = [
    run_commands.spec,
    run_python.spec,
    view_image.spec,
    documentReader.spec,
    browser.spec,
    image_gen.spec,
    open_image.spec
    ]

def handle_tool_calls(prompt_id,tool_calls,source='fefe'):

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        #print(function_name)
        function_to_call = available_tools.get(function_name,None)
        try:
            function_args = json.loads(tool_call.function.arguments)
        except Exception as e:
            function_args = {'code':tool_call.function.arguments}
        
        if function_name == 'run_commands':
            try:
                function_response = function_to_call(
                    commands = function_args.get("commands"),
                    verbose = function_args.get("verbose",False)
                )
                # Add tool call to content
                functions.update_chat_history({'role':'tool','content':f'''

    Result of `run_commands` executed by the assistant:
    ```
    {function_response}
    ```
    ''','tool_call_id': tool_call.id},'run_commands')
            except Exception as e:
                functions.update_chat_history({'role':'tool','content':f'Error: {e}','tool_call_id': tool_call.id},'run_commands')
            
        if function_name == 'run_python':
            arguments = function_args.get('code')
            try:
                if arguments is None:
                    arguments = function_args
                code, output = function_to_call(
                    prompt_id = prompt_id,
                    code = arguments
                )
                functions.update_chat_history({'role':'tool','content':f'output: {output} \n\nDone.','tool_call_id': tool_call.id},'run_python')
            except Exception as e:
                functions.update_chat_history({'role':'tool','content':f'Error: {e}','tool_call_id':tool_call.id},'run_python')

        if function_name == 'view_image':
            try:
                image_content = function_to_call(
                    filepath = function_args.get('filepath')
                )
                user_json = functions.get_chat_message(prompt_id)
                user_json = {'role':'user','content': user_json['content'] + [image_content]}
                functions.update_chat_message(prompt_id,user_json)
                functions.update_chat_history({'role':'tool','content':f"Image was encoded for the user",'tool_call_id': tool_call.id},'view_image')
            except Exception as e:
                functions.update_chat_history({'role':'tool','content':f'Error: {e}','tool_call_id':tool_call.id},'view_image')
        
        if function_name == 'documentReader':
            try:
                document_text = function_to_call(
                    filepath = function_args.get('filepath')
                )
                functions.update_chat_history({'role':'tool','content':f'text: {document_text}','tool_call_id': tool_call.id},'documentReader')
            except Exception as e:
                functions.update_chat_history({'role':'tool','content':f'Error: {e}','tool_call_id':tool_call.id},'documentReader')

        if function_name == 'browser':
            try:
                url_data = function_to_call(
                    url = function_args.get('url'),
                    open_for_user = function_args.get('open_for_user',False)
                )
                functions.update_chat_history({"role": "tool", "content": f'url_content: {url_data}','tool_call_id': tool_call.id},'browser')
            except Exception as e:
                functions.update_chat_history({"role":"tool","content":f"There was an issue fetching the information from {function_args.get("url")} \n Error: \n{e}",'tool_call_id': tool_call.id},'browser')

        if function_name == 'image_gen':
            function_to_call(
                prompt = function_args.get('prompt'),
                filepath = function_args.get('filepath'),
                tool_call = tool_call
            )
        
        if function_name == 'open_image':
            try:
                function_to_call(
                    filepath = function_args.get('filepath')
                )
                functions.update_chat_history({'role':'tool','content':'Image was opened for the user.','tool_call_id': tool_call.id},'open_image')
            except Exception as e:
                functions.update_chat_history({'role':'tool','content':f'There was an issue opening the image for the user: {e}','tool_call_id': tool_call.id},'open_image')

    fefe.respond_to_chat(prompt_id)
    