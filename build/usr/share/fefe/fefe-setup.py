#!/usr/share/fefe/fefe-env/bin/python3

import sqlite3
import os
import getpass
import sys
from src import functions
from src import user_info
import subprocess 

default_personality = f"""
Tsundere, yet loving
"""

def print_help():
    help_message = """
    Usage: fefe-setup [OPTION]

    Options:
      --help, -h            Show this help message and exit
      text-color            Choose a text color for your fefe configuration.
                            This will prompt you to select a color and save it to your configuration.
      sudo                  Update your stored sudo password.
      api-key               Update your OpenAI API key.
      organization-id       Update your Organization ID.
      personality           Update the personality for your fefe configuration.
      wipe-memory           Wipe Fefe's memory. Clears the chat history.
      wls            Enable or disable WLS (Windows Linux Subsystem) support.
      (no option)           Run the setup process to configure your OpenAI API key,
                            Organization ID, system information, sudo password, 
                            text color, and personality.

    Description:
      The fefe-setup command is used to initialize or update the configuration
      for the 'fefe' command-line tool. You can set or update your OpenAI API key,
      Organization ID, system information, sudo password, text color, personality, 
      and WLS (Windows Linux Subsystem) support.
      
    Examples:
      fefe-setup            Starts the setup process.
      fefe-setup text-color Allows you to choose a new text color for your output.
      fefe-setup sudo       Updates your stored sudo password.
      fefe-setup api-key    Updates your OpenAI API key.
      fefe-setup organization-id
                           Updates your Organization ID.
      fefe-setup personality
                           Updates the personality for your fefe configuration.
      fefe-setup wipe-memory
                           Wipe Fefe's memory. Useful when bot becomes confused or when you wish to start fresh.
      fefe-setup wls Enable or disable WLS support.
    """
    print(help_message)

def initialize_db():
    conn = functions.db_connect()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    api_key TEXT, 
                    org_id TEXT, 
                    os_info TEXT,
                    text_color TEXT,
                    sudo_password TEXT,
                    personality TEXT,
                    user_display_name TEXT,
                    wls INTEGER
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jsonl TEXT,
                    role TEXT,
                    source TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
              );''')
    conn.commit()
    conn.close()

def set_config(api_key=None, org_id=None, os_info=None, text_color=None, sudo_password=None, personality=None, user_display_name = None, wls = None):
    conn = functions.db_connect()
    c = conn.cursor()
    c.execute("DELETE FROM config")  # Ensure only one entry is stored
    c.execute("""INSERT INTO config (api_key, org_id, os_info, text_color, sudo_password, personality, user_display_name, wls) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (api_key, org_id, os_info, text_color, sudo_password, personality, user_display_name, wls))
    conn.commit()
    conn.close()
    print("Configuration has been saved.")

def setup():
    os_info = functions.get_system_info()

    api_key = getpass.getpass("Please enter your OpenAI API key: ").strip()
    if not api_key:
        print("API key cannot be empty.")
        return

    org_id = input("Please enter your Organization ID (optional): ").strip()
    org_id = org_id if org_id else None

    # Optionally store sudo password
    sudo_password = getpass.getpass("Please enter your sudo password (optional): ").strip()
    sudo_password = sudo_password if sudo_password else None

    answer = input("Are you using Ubuntu with Windows Linux Subsystem? (Yes/No): ").strip()
    if answer.lower() in ['y', 'yes']:
        wls = 1
        install_tkinter()  # Install tkinter if WLS is enabled
        print('WLS support enabled.')
    else:
        wls = 0

    # Ask user to choose a text color
    print("Please choose a text color:")
    for color_name in functions.COLOR_OPTIONS:
        print(f"{functions.COLOR_OPTIONS[color_name]}{color_name}\033[0m")
    
    color_choice = input("Enter your color choice: ").strip()
    if color_choice not in functions.COLOR_OPTIONS:
        print("Invalid choice.")
        color_choice = None

    initialize_db()
    user_display_name = user_info.get_display_name()
    set_config(api_key, org_id, os_info, color_choice, sudo_password, default_personality, user_display_name, wls)
    print(f"Setup complete. You can now use the 'fefe' command.")


def choose_text_color():
    print("Please choose a text color:")
    for color_name in functions.COLOR_OPTIONS:
        print(f"{functions.COLOR_OPTIONS[color_name]}{color_name}\033[0m")
    
    color_choice = input("Enter your color choice: ").strip()
    if color_choice not in functions.COLOR_OPTIONS:
        print("Invalid choice. No changes were made.")
        return

    conn = functions.db_connect()
    c = conn.cursor()
    c.execute("UPDATE config SET text_color = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)", (color_choice,))
    conn.commit()
    conn.close()
    
    print(f"Text color set to {color_choice}.")

def update_api_key():
    api_key = getpass.getpass("Please enter your new OpenAI API key: ").strip()
    if not api_key:
        print("API key cannot be empty. No changes were made.")
        return

    conn = functions.db_connect()
    c = conn.cursor()
    c.execute("UPDATE config SET api_key = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)", (api_key,))
    conn.commit()
    conn.close()
    
    print("API key updated successfully.")

def update_org_id():
    org_id = input("Please enter your new Organization ID: ").strip()
    if not org_id:
        org_id = None  # Allow empty organization ID

    conn = functions.db_connect()
    c = conn.cursor()
    c.execute("UPDATE config SET org_id = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)", (org_id,))
    conn.commit()
    conn.close()
    
    print("Organization ID updated successfully.")


def update_sudo_password():
    sudo_password = getpass.getpass("Please enter your new sudo password: ").strip()
    if not sudo_password:
        print("Sudo password cannot be empty. No changes were made.")
        return

    conn = functions.db_connect()
    c = conn.cursor()
    c.execute("UPDATE config SET sudo_password = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)", (sudo_password,))
    conn.commit()
    conn.close()
    
    print("Sudo password updated successfully.")


def update_personality():
    print("Please enter your desired personality for the fefe configuration:")
    personality = input("Personality (default is 'Tsundere'): ").strip()
    if not personality:
        personality = default_personality

    conn = functions.db_connect()
    c = conn.cursor()
    c.execute("UPDATE config SET personality = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)", (personality,))
    conn.commit()
    conn.close()
    
    print(f"Personality set to '{personality}'.")


def update_wsl():
    print("Are you using Fefe on Windows Linux Subsystem? (Yes/No): ")
    answer = input("Yes/No: ").strip()
    conn = functions.db_connect()
    c = conn.cursor()
    
    if answer.lower() in ['y', 'yes']:
        # Set WLS support to enabled
        c.execute('UPDATE config SET wls = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)', (1,))
        conn.commit()
        conn.close()
        
        # Install python-tk to enable TkAgg backend for matplotlib
        install_tkinter()
        print("WLS support enabled and Tkinter installed.")
    else:
        # Set WLS support to disabled
        c.execute('UPDATE config SET wls = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)', (0,))
        conn.commit()
        conn.close()
        
        print("WLS support disabled.")

def clear_chat_history():
    print("Would you like to wipe Fefe's memory?")
    answer = input("Yes/No: ").strip()
    if answer.lower() in ['y', 'yes']:
        conn = functions.db_connect()
        c = conn.cursor()
        c.execute("DELETE FROM chat_history")
        conn.commit()
        conn.close()
        print("Fefe's memory was wiped.")
    else:
        print("Fefe's memory was not wiped.")

def install_tkinter():
    """Function to install python-tk package if not already installed."""
    try:
        import tkinter
        print("Tkinter is already installed.")
    except ImportError:
        print("Tkinter not found. Installing python-tk...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-tk"])
        print("Tkinter installation complete.")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        setup()
    elif len(sys.argv) == 2:
        if sys.argv[1] in ["--help", "-h"]:
            print_help()
        elif sys.argv[1] == "text-color":
            choose_text_color()
        elif sys.argv[1] == "sudo":
            update_sudo_password()
        elif sys.argv[1] == "api-key":
            update_api_key()
        elif sys.argv[1] == "organization-id":
            update_org_id()
        elif sys.argv[1] == "personality":
            update_personality()
        elif sys.argv[1] == "wls":
            update_wsl()
        elif sys.argv[1] == "wipe-memory":
            clear_chat_history()
        else:
            print("Invalid option. Use --help or -h for usage information.")
    else:
        print("Usage: fefe-setup [text-color | sudo | api-key | organization-id | personality | wipe-memory | wls | --help | -h]")
