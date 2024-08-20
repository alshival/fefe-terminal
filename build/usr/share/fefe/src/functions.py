import sqlite3
import os 
import json 
import platform
import sys
import tiktoken 
from openai.types import CompletionUsage
from openai.types.chat import ChatCompletion, ChatCompletionMessage,ChatCompletionMessageToolCall
from openai.types.chat.chat_completion_message_tool_call import Function
from openai.types.chat.chat_completion import Choice

class Model:
    def __init__(self, name, context_limit, response_limit):
        self.name = name
        self.context_limit = context_limit
        self.response_limit = response_limit

        # Define token_limit based on model.name
        if self.name == 'gpt-3.5-turbo':
            self.token_limit = 4096
        elif self.name == 'gpt-4':
            self.token_limit = 8000
        elif self.name == 'gpt-4o-mini':
            self.token_limit = 128000
        else:
            self.token_limit = None  # or some default value or raise an error


# Create an instance of the Model class using the dictionary values
model_data = {"name": "gpt-4o-mini", "context_limit": 30000, "response_limit": 5000}
model = Model(**model_data)

def check_tokens(messages,instructions = None):
    enc = tiktoken.encoding_for_model(model.name)
    if instructions:
        instruction_tokens = len(enc.encode(json.dumps(instructions)))
    else:
        instruction_tokens = 0
    messages_string = str(messages)
    tokens = len(enc.encode(messages_string))
    
    while tokens > model.token_limit - model.response_limit - instruction_tokens:
        # Remove the first message from the JSON list
        messages = messages[1:]
        
        # Update the messages string and token count
        messages_string = str(messages)
        tokens = len(enc.encode(messages_string))
    
    return messages
#######################################################################
# Common functions 
#######################################################################
def filetype(filepath):
    _, file_extension = os.path.splitext(filepath)
    if file_extension:
        return file_extension.lower().lstrip('.')
    else:
        return None

def get_system_info():
    # Get the basic operating system information
    if platform.system() == 'Linux':
        freedesktop_os_release = platform.freedesktop_os_release()
        os_info = f'{freedesktop_os_release['NAME']} {freedesktop_os_release['VERSION']}'
    else:
        os_info = f'{platform.system()} {platform.version()} {platform.release()}'

    return os_info

def get_home_path():
    # Determine the home directory path based on the OS
    system = platform.system()

    if system == 'Linux' or system == 'Darwin':  # Darwin is the system name for macOS
        home_path = os.path.expanduser('~')
    elif system == 'Windows':
        user_login = os.getlogin()
        home_path = f'C:\\Users\\{user_login}\\'
    else:
        raise ValueError(f"Unsupported operating system: {system}")

    return home_path

def get_config():
    conn = db_connect()
    c = conn.cursor()
    c.execute("SELECT api_key, org_id, os_info, personality, user_display_name, wsl FROM config LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row:
        return row[0], row[1], row[2], row[3], row[4], row[5]
    else:
        print("API key not found. Please run 'fefe-setup' to configure.")
        sys.exit(1)

def is_wsl():
    conn = db_connect()
    c = conn.cursor()
    c.execute("SELECT wsl FROM config LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row:
        if row[0] == 1:
            return True
        else:
            return False
    else:
        print("API key not found. Please run 'fefe-setup' to configure.")
        sys.exit(1)

def is_wsl_subprocess():
    import subprocess
    try:
        # Run the uname -r command
        output = subprocess.check_output(['uname', '-r'], text=True).strip()
        
        # Check if "microsoft" or "WSL" is in the output
        if 'microsoft' in output.lower() or 'wsl' in output.lower():
            return True
        return False
    except subprocess.CalledProcessError:
        return False

COLOR_OPTIONS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright black": "\033[90m",
    "bright red": "\033[91m",
    "bright green": "\033[92m",
    "bright yellow": "\033[93m",
    "bright blue": "\033[94m",
    "bright magenta": "\033[95m",
    "bright cyan": "\033[96m",
    "bright white": "\033[97m",
    "orange": "\033[38;5;214m",  # Approximate orange
    "lime": "\033[38;5;154m",    # Approximate lime
    "pink": "\033[38;5;213m",    # Approximate pink
    "purple": "\033[38;5;141m",  # Approximate purple
    "teal": "\033[38;5;37m",     # Approximate teal
    "olive": "\033[38;5;100m",   # Approximate olive
    "brown": "\033[38;5;94m",    # Approximate brown
    "gold": "\033[38;5;220m",    # Approximate gold
    "silver": "\033[38;5;250m",  # Approximate silver
    "navy": "\033[38;5;18m",     # Approximate navy
    "maroon": "\033[38;5;52m",   # Approximate maroon
}

def get_text_color():
    conn = db_connect()
    c = conn.cursor()
    
    # Fetch the text_color from the config table
    c.execute("SELECT text_color FROM config ORDER BY id DESC LIMIT 1")
    result = c.fetchone()
    
    conn.close()
    
    if result:
        try:
            response = COLOR_OPTIONS[result[0]]
        except:
            response = None
        return response
    else:
        return None  # Return None if no color is found

def get_sudo():
    conn = db_connect()
    c = conn.cursor()
    
    # Fetch the sudo_password from the config table
    c.execute("SELECT sudo_password FROM config ORDER BY id DESC LIMIT 1")
    result = c.fetchone()
    
    conn.close()
    
    if result:
        return result[0]  # Return the sudo password if found
    else:
        return None  # Return None if no sudo password is found

#######################################################################
# Database functions
#######################################################################

def db_connect():
    db_path = os.path.expanduser(os.path.join(get_home_path(),".fefe.db"))
    conn = sqlite3.connect(db_path)
    return conn

#----------------------------------------------------------------------
# Chat History
#----------------------------------------------------------------------
def update_chat_history(message, source=None):
    message_string = str(message)
    db = db_connect()
    cursor = db.cursor()

    cursor.execute("""
    INSERT INTO chat_history (message, source)
    VALUES (?,?)
    """, (message_string, source,))

    # Retrieve the id of the newly inserted row
    chat_id = cursor.lastrowid

    db.commit()
    db.close()

    return chat_id

def get_chat_history(limit=6):
    db = db_connect()
    cursor = db.cursor()
    
    cursor.execute("""
    with tbl as (
        SELECT id, message, source, timestamp
        FROM chat_history
        ORDER BY timestamp desc LIMIT ?
    )
    select * from tbl order by timestamp
    """, (limit,))  # Pass limit as a tuple
    
    # Fetch all results
    results = cursor.fetchall()
    
    db.close()
    
    # # Convert the JSON strings back to Python dictionaries (if applicable)
    # chat_history = []
    # for row in results:
    #     json_data = eval(row[0])
    #     chat_history.append(json_data)
    
    return results

def get_chat_message(chat_id):
    db = db_connect()
    cursor = db.cursor()

    cursor.execute("""
    SELECT message FROM chat_history
    WHERE id = ?
    """, (chat_id,))

    result = cursor.fetchone()
    db.close()

    if result:
        message = eval(result[0])  # Convert JSON string back to a dictionary
        return message
    else:
        return None  # Return None if no record is found


def update_chat_message(chat_id, new_message):
    new_message_string = str(new_message)  # Convert the new JSON data to a string
    db = db_connect()
    cursor = db.cursor()

    cursor.execute("""
    UPDATE chat_history
    SET message = ?
    WHERE id = ?
    """, (new_message_string, chat_id))

    db.commit()
    db.close()

def clear_chat_history(source = None):
    db = db_connect()
    cursor = db.cursor()
    if source is None:
        cursor.execute("delete from chat_history")
    else:
        cursor.execute("delete from chat_history where source = ?",(source,))
    db.commit()
    db.close()
def delete_chat_message(chat_id):
    db = db_connect()
    cursor = db.cursor()
    cursor.execute("delete from chat_history where id = ?",(chat_id,))
    db.commit()
    db.close()
