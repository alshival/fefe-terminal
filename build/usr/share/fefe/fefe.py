#!/usr/share/fefe/fefe-env/bin/python3

import sys
from openai import OpenAI
import os
from datetime import datetime 
import tools 
from src import functions

def format_response(text):
    color = functions.get_text_color()
    if color:
        return f"{color}{text}\033[0m"
    else:
        return text

def respond_to_chat(prompt_id, source = 'fefe'):
    api_key, org_id, os_info, personality, user_display_name = functions.get_config()
    client = OpenAI(
        api_key=api_key,
        organization=org_id
    ) 
    # Join the input arguments into a single string, treating them as a single prompt
    instructions = f'''
Your name is Fefe. You are {user_display_name}'s Ai assistant. 

Description of your personality and relationship with {user_display_name}:
```
{personality}
```

Current timestamp: {datetime.now()}

User's current working directory: {os.getcwd()}
'''
    if len(os.listdir('.')) <= 25:
        instructions += f'''
Files:
```
{os.listdir()}
```'''
        
    instructions +='''
Operating System: {os_info}

You can use the `run_commands` tool for interacting with the user's operating system. If you are executing python code, use the `run_python` tool instead. To use the `run_commands` tool, pass the commands to be run as a list in the `commands` parameter. Do not set `verbose=True` unless the user specifically requests that you show them the output.
For example, if a linux user wishes to know the path to the current directory, you can use `run_commands` with `commands=['pwd']`. 
If asked to search for files within a directory, avoid searching within subdirectories unless asked by the user to search within subdirectories. For example, if asked about files older than a week in the current directory, you would use something like `find . -maxdepth 1 -type f -mtime +7` to avoid searching within subdirectories unless the user requests that you search deeper.

You can use the `run_python` to execute python code by including your code in the `code` parameter. Use this tool when generating data visualizations, financial charts, or interacting with hardware like the user's webcam.
You can use plotly (preferred) and matplotlib to create visualizations.
If a user asks you to generate charts for stock tickers, use `run_python` with the `yfinance` package. 
If the user does not ask you to save a data visualization as an image, just `.show()` the image. 

The `view_image` tool allows the assistant to view images. If a user asks you about a specific png, jpg, or webp image on their system, use the `view_image` to view it.
Call this function only when an image has not yet been encoded and the user is asking about a specific image on their system.

The `documentReader` tool can be used to extract text from documents. If a user asks about a document, use this tool to retrieve the contents. For data files like .csv, .tsv, .xlsx, it is preferred that you analyze them using pandas and graphical libraries using the `run_python` command, even though the `documentReader` supports these files.

The `image_gen` tool allows you to generate images. Describe the image in the `prompt` parameter and provide a `filepath` to store the image, for example `filepath="./flower_garden.png"`

You can delay your final response until after the completion of any of the above tools so that you have the information needed to respond.
'''
    instruction_jsonl = [{'role':'system','content':instructions}]

    messages = functions.get_chat_history(limit = 10)
    # Check token limit.
    messages = functions.check_tokens(messages,instruction_jsonl)
    # Prepend instructions
    messages = instruction_jsonl + messages
    #print(messages)
    chat_completion = client.chat.completions.create(
        messages=messages,
        model= functions.model.name,
        tools = tools.tools,
        temperature=0.8
    )
    response = chat_completion.choices[0].message
    tool_calls = response.tool_calls
    if not tool_calls:
        functions.update_chat_history({'role':'assistant','content':response.content},source)
        formatted_response = format_response(response.content)
        print(formatted_response)
    else:
        # handle tool calls
        tools.handle_tool_calls(prompt_id,tool_calls)
def main():
    if len(sys.argv) < 2:
        print("Usage: fefe <prompt>")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])
    user_json = {'role':'user', 'content': [{'type':'text','text':prompt}]}
    prompt_id = functions.update_chat_history(user_json)

    respond_to_chat(prompt_id)

if __name__ == "__main__":
    main()

