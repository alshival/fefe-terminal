from src import run_commands
from src import functions 
from src import encode_image
from src import documentReader
from src import run_python
from src import browser 
from src import image_gen
from src import open_image
from src import music_player
from src import search_youtube
import fefe
import json 

available_tools = {
    'run_commands': run_commands.run_commands,
    'run_python': run_python.run_python,
    'encode_image': encode_image.encode_image,
    'documentReader': documentReader.documentReader,
    'browser': browser.browser,
    'search_youtube': search_youtube.search_youtube,
    'image_gen': image_gen.image_gen,
    'open_image': open_image.open_image,
    'music_player': music_player.music_player
}

tools = [
    run_commands.spec,
    run_python.spec,
    encode_image.spec,
    documentReader.spec,
    browser.spec,
    image_gen.spec,
    open_image.spec,
    music_player.spec,
    search_youtube.spec
    ]

def handle_tool_calls(prompt_id,tool_calls):

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        #print(function_name)
        function_to_call = available_tools.get(function_name,None)
        function_args = json.loads(tool_call.function.arguments)
        
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
    ''','tool_call_id': tool_call.id}, prompt_id)
            except Exception as e:
                functions.update_chat_history({'role':'tool','content':f'Error: {e}','tool_call_id': tool_call.id},prompt_id)
            
        if function_name == 'run_python':
            arguments = function_args.get('code')
            try:
                if arguments is None:
                    arguments = function_args
                code, output = function_to_call(
                    prompt_id = prompt_id,
                    code = arguments
                )
                functions.update_chat_history({'role':'tool','content':f'output: {output} \n\nDone.','tool_call_id': tool_call.id},prompt_id)
            except Exception as e:
                functions.update_chat_history({'role':'tool','content':f'An error occured while executing the script: {e}','tool_call_id':tool_call.id},prompt_id)

        if function_name == 'encode_image':
            try:
                image_content = function_to_call(
                    filepath = function_args.get('filepath')
                )
                user_json = functions.get_chat_message(prompt_id)
                user_json = {'role':'user','content': user_json['content'] + [image_content]}
                functions.update_chat_message(prompt_id,user_json)
                functions.update_chat_history({'role':'tool','content':f"Image was encoded for the user. You can now respond to their previous message..",'tool_call_id': tool_call.id},prompt_id)
            except Exception as e:
                functions.update_chat_history({'role':'tool','content':f'Error: {e}','tool_call_id':tool_call.id},prompt_id)
        
        if function_name == 'documentReader':
            try:
                document_text = function_to_call(
                    filepath = function_args.get('filepath')
                )
                functions.update_chat_history({'role':'tool','content':f'text: {document_text}','tool_call_id': tool_call.id},prompt_id)
            except Exception as e:
                functions.update_chat_history({'role':'tool','content':f'Error: {e}','tool_call_id':tool_call.id},prompt_id)

        if function_name == 'browser':
            try:
                url_data = function_to_call(
                    url = function_args.get('url'),
                    open_for_user = function_args.get('open_for_user',False)
                )
                functions.update_chat_history({"role": "tool", "content": f'url_content: {url_data}','tool_call_id': tool_call.id},prompt_id)
            except Exception as e:
                functions.update_chat_history({"role":"tool","content":f"There was an issue fetching the information from {function_args.get("url")} \n Error: \n{e}",'tool_call_id': tool_call.id},prompt_id)

        if function_name == 'image_gen':
            function_to_call(
                prompt = function_args.get('prompt'),
                filepath = function_args.get('filepath'),
                prompt_id = prompt_id,
                tool_call = tool_call
            )
        
        if function_name == 'open_image':
            try:
                function_to_call(
                    filepath = function_args.get('filepath')
                )
                functions.update_chat_history({'role':'tool','content':'Image was opened for the user.','tool_call_id': tool_call.id},prompt_id)
            except Exception as e:
                functions.update_chat_history({'role':'tool','content':f'There was an issue opening the image for the user: {e}','tool_call_id': tool_call.id},prompt_id)
        if function_name == 'music_player':
            try:
                function_to_call(
                    filepath = function_args.get('filepath',None)
                )
                functions.update_chat_history({'role':'tool','content':'The music player was opened for the user.','tool_call_id': tool_call.id},prompt_id)
            except Exception as e:
                functions.update_chat_history({'role':'tool','content':f'There was an issue opening the music player for the user: {e}','tool_call_id': tool_call.id},prompt_id)

        if function_name == 'search_youtube':
            try:
                results = function_to_call(
                    query =  function_args.get("query")
                )
                functions.update_chat_history({'role':'tool','content':f'Search Results:\n {results}','tool_call_id':tool_call.id}, prompt_id)
            except Exception as e:
                functions.update_chat_history({'role':'tool','content':f'There was an issue using the YouTube Data API: \n {e} \n\n If it is an issue with credentials, inform the user they can set their google api key using `fefe-setup google-api`. ','tool_call_id':tool_call.id},prompt_id)
    fefe.respond_to_chat(prompt_id)
    