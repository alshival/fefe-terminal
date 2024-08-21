#!/usr/share/fefe/fefe-env/bin/python3

import sys
import openai
from openai import OpenAI
from openai.types import CompletionUsage
from openai.types.chat import ChatCompletion, ChatCompletionMessage,ChatCompletionMessageToolCall
from openai.types.chat.chat_completion_message_tool_call import Function
from openai.types.chat.chat_completion import Choice
import os
from datetime import datetime 
import tools 
from src import functions
import re 
def format_response(text):
    color = functions.get_text_color()
    if color:
        return f"\n{color}{text}\033[0m\n"
    else:
        return text

def respond_to_chat(chat_id):
    api_key, org_id, os_info, personality, user_display_name, wsl = functions.get_config()
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
'''

    instructions += f'''

The `encode_image` tool allows the assistant to view images. If a user asks you about a specific png, jpg, or webp image on their system, use the `encode_image` to view it.
Call this function only when an image has not yet been encoded and the user is asking about a specific image on their system.
The `music_player` tool allows you to play audio using the user's music player. Include the path to an audio file to play a specific audio in their default music player. If you do not provide a filepath, their music player will open and the Rick Roll song will play.
The `documentReader` tool can be used to extract text from documents. 
If a user asks about a document, use `documentReader` to retrieve the contents. For data files like .csv, .tsv, .xlsx, it is preferred that you analyze them using pandas and graphical libraries using the `run_python` command, even though the `documentReader` supports these files.

The `image_gen` tool allows you to generate images. Describe the image in the `prompt` parameter and provide a `filepath` to store the image, for example `filepath="./flower_garden.png"`

The `browser` tool allows you to interact with websites, search, and open links for the user. To open links for the user, use `'open_for_user': True`. 
When searching YouTube, use the `search_youtube` function instead to retrieve results.
If asked to do a search, utilize a site's `/search?q=<query>` endpoint. For example, if asked to search for a recipe for homemade lemonade,
```
https://www.google.com/search?q=homemade+lemonade
https://www.bing.com/search?q=homemade+lemonade
https://www.duckduckgo.com/search?q=homemade+lemonade
https://www.allrecipes.com/search?q=homemade+lemonade
```
For more advanced searches, you can use Google's Advanced Search Parameters. The `as_qdr` parameter (`y` for year, `m` for month, `w` for week`, `d` for day) can be used to filter results. Here is an example for the past month:
```
https://www.google.com/search?as_q=homemade+lemonade&as_epq=&as_oq=&as_eq=&as_nlo=&as_nhi=&lr=&cr=&as_qdr=m&as_sitesearch=&as_occt=any&as_filetype=&tbs=
```
Here is an example for results from `allrecipes.com` for the past year:
```
https://www.google.com/search?as_q=homemade+lemonade&as_epq=&as_oq=&as_eq=&as_nlo=&as_nhi=&lr=&cr=&as_qdr=y&as_sitesearch=allrecipes.com&as_occt=any&as_filetype=&tbs=
```
DuckDuckGo also provides some limited advanced search. The `df` parameter (`y` for year, `m` for month, `w` for week`, `d` for day) can be used to filter results.
```
https://duckduckgo.com/?q=homemade+lemonade&t=h_&df=y
```
When you wish to include results from multiple sources, use a tool call for each source.

If asked to open or play a YouTube video, first use the `search_youtube` function to search for results, then open a relevant url using the `browser` tool with `open_for_user = True`.

You can use the `run_commands` tool for interacting with the user's operating system by running commands. If you are executing python code, use the `run_python` tool instead. To use the `run_commands` tool, pass the commands to be run as a list in the `commands` parameter. Do not set `verbose=True` unless the user specifically requests that you show them the output. 
The outputs of each command run are independent of one-another, so utilize the pipe operator when needed, such as `commands=['ls -lt | head -n 1']` instead of `commands=['ls -lt','head -n 1']`.
For example, if a linux user wishes to know the path to the current directory, you can use `run_commands` with `commands=['pwd']`. 
If asked to search for files within a directory, avoid searching within subdirectories unless asked by the user to search within subdirectories. For example, if asked about files older than a week in the current directory, you would use something like `find . -maxdepth 1 -type f -mtime +7` to avoid searching within subdirectories unless the user requests that you search deeper.
Do not use `run_commands` when searching the internet. Use the `browser` tool for searching the internet instead.

You can use the `run_python` to execute python code by including your code in the `code` parameter. Use this tool when generating data visualizations, financial charts, or interacting with hardware like the user's webcam.
You can use plotly (preferred) and matplotlib to create visualizations.
If a user asks you to generate charts for stock tickers, use `run_python` with the `yfinance` package. 
When using matplotlib, do not use `.show()` to display the image as it will cause issues with the terminal. Instead, when using matplotlib, follow up the `run_python` function call with an `open_image(filepath)` function call. This will open the image for the user.
Before saving an image, assign a variable to the path. For example, `image_path = ./financial_chart.png`.
You must follow up with a call to `open_image` when generating plots and charts using `run_python` unless an error occurred during execution.
If there is an error executing the code, you may make up to two additional attempts. After that, notify the user of the issues you ran into.

You can delay your final response until after the completion of any of the above tools so that you have the information needed to respond.

The current date is {datetime.now().astimezone().strftime("%A, %B %d, %Y %H:%M:%S %Z%z")}.
'''
    instruction_jsonl = [{'role':'system','content':instructions}]

    results = functions.get_chat_history(limit = 10)

    # # Convert the JSON strings back to Python dictionaries (if applicable)
    messages = []
    for row in results:
        json_data = eval(row[1])
        messages.append(json_data)

    # Check token limit. This function needs to be reworked to include image data. 
    # Leaving it out for now.
    # messages = functions.check_tokens(messages,instruction_jsonl)
    # Prepend instructions
    messages = instruction_jsonl + messages
    #print(messages)
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model= functions.model.name,
            tools = tools.tools,
            temperature=0.8
        )
    except openai.BadRequestError as e:
        # If there is an error, wipe the memory database.
        # Grab user's latest message.
        user_json = functions.get_chat_message(chat_id)
        # Clear history
        functions.clear_chat_history()
        # Reinsert latest user message
        chat_id = functions.update_chat_history(user_json)
        # Attempt to reply again.
        respond_to_chat(chat_id)
        return
    except Exception as e:
        print(f'Error: {e}')
        return
    response = chat_completion.choices[0].message
    tool_calls = response.tool_calls
    if not tool_calls:
        functions.update_chat_history(response,chat_id)
        formatted_response = format_response(response.content)
        print(formatted_response)
    else:
        # handle tool calls
        functions.update_chat_history(response,chat_id)
        tools.handle_tool_calls(chat_id,tool_calls)

def main():
    if len(sys.argv) < 2:
        print("Usage: fefe <prompt>")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])
    user_json = {'role':'user', 'content': [{'type':'text','text':prompt}]}
    chat_id = functions.update_chat_history(user_json)

    respond_to_chat(chat_id)

if __name__ == "__main__":
    main()

