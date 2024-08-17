import sqlite3
import os 
import json 
import platform
import sys
import tiktoken 

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

#######################################################################
# Common functions 
#######################################################################
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
    c.execute("SELECT api_key, org_id, os_info, personality, user_display_name, wls FROM config LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row:
        return row[0], row[1], row[2], row[3], row[4], row[5]
    else:
        print("API key not found. Please run 'fefe-setup' to configure.")
        sys.exit(1)

COLOR_OPTIONS = {
    "Black": "\033[30m",
    "Red": "\033[31m",
    "Green": "\033[32m",
    "Yellow": "\033[33m",
    "Blue": "\033[34m",
    "Magenta": "\033[35m",
    "Cyan": "\033[36m",
    "White": "\033[37m",
    "Bright Black": "\033[90m",
    "Bright Red": "\033[91m",
    "Bright Green": "\033[92m",
    "Bright Yellow": "\033[93m",
    "Bright Blue": "\033[94m",
    "Bright Magenta": "\033[95m",
    "Bright Cyan": "\033[96m",
    "Bright White": "\033[97m",
    "Orange": "\033[38;5;214m",  # Approximate orange
    "Lime": "\033[38;5;154m",    # Approximate lime
    "Pink": "\033[38;5;213m",    # Approximate pink
    "Purple": "\033[38;5;141m",  # Approximate purple
    "Teal": "\033[38;5;37m",     # Approximate teal
    "Olive": "\033[38;5;100m",   # Approximate olive
    "Brown": "\033[38;5;94m",    # Approximate brown
}


def get_text_color():
    conn = db_connect()
    c = conn.cursor()
    
    # Fetch the text_color from the config table
    c.execute("SELECT text_color FROM config ORDER BY id DESC LIMIT 1")
    result = c.fetchone()
    
    conn.close()
    
    if result:
        return COLOR_OPTIONS[result[0]]
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
def update_chat_history(jsonl, source=None):
    role = jsonl.get('role', '')
    jsonl_string = json.dumps(jsonl)
    db = db_connect()
    cursor = db.cursor()

    cursor.execute("""
    INSERT INTO chat_history (jsonl, role, source)
    VALUES (?,?,?)
    """, (jsonl_string, role, source,))

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
        SELECT jsonl, role, source, timestamp
        FROM chat_history
        ORDER BY timestamp desc LIMIT ?
    )
    select * from tbl order by timestamp
    """, (limit,))  # Pass limit as a tuple
    
    # Fetch all results
    results = cursor.fetchall()
    
    db.close()
    
    # Convert the JSON strings back to Python dictionaries (if applicable)
    chat_history = []
    for row in results:
        json_data = json.loads(row[0])
        chat_history.append(json_data)
    
    
    return chat_history

def get_chat_message(chat_id):
    db = db_connect()
    cursor = db.cursor()

    cursor.execute("""
    SELECT jsonl FROM chat_history
    WHERE id = ?
    """, (chat_id,))

    result = cursor.fetchone()
    db.close()

    if result:
        jsonl_data = json.loads(result[0])  # Convert JSON string back to a dictionary
        return jsonl_data
    else:
        return None  # Return None if no record is found


def update_chat_message(chat_id, new_jsonl):
    new_jsonl_string = json.dumps(new_jsonl)  # Convert the new JSON data to a string
    db = db_connect()
    cursor = db.cursor()

    cursor.execute("""
    UPDATE chat_history
    SET jsonl = ?
    WHERE id = ?
    """, (new_jsonl_string, chat_id))

    db.commit()
    db.close()

def check_tokens(jsonl,instructions = None):
    enc = tiktoken.encoding_for_model(model.name)
    if instructions:
        instruction_tokens = len(enc.encode(json.dumps(instructions)))
    else:
        instruction_tokens = 0
    messages_string = json.dumps(jsonl)
    tokens = len(enc.encode(messages_string))
    
    while tokens > model.token_limit - model.response_limit - instruction_tokens:
        # Remove the first message from the JSON list
        jsonl = jsonl[1:]
        
        # Update the messages string and token count
        messages_string = json.dumps(jsonl)
        tokens = len(enc.encode(messages_string))
    
    return jsonl
