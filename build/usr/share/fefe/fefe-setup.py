#!/usr/share/fefe/fefe-env/bin/python3

import sqlite3
import os
import getpass
import sys
from src import functions
from src import run_commands
from src import user_info
import subprocess 
import re

default_personality = f"Tsundere, yet flirty"

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
      wsl            Enable or disable wsl (Windows Linux Subsystem) support.
      (no option)           Run the setup process to configure your OpenAI API key,
                            Organization ID, system information, sudo password, 
                            text color, and personality.

    Description:
      The fefe-setup command is used to initialize or update the configuration
      for the 'fefe' command-line tool. You can set or update your OpenAI API key,
      Organization ID, system information, sudo password, text color, personality, 
      and wsl (Windows Linux Subsystem) support.
      
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
      fefe-setup WSL Enable or disable Windows Subsystem for Linux support.
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
                    wsl INTEGER
                );''')
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT,
                    source TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
              );''')

    conn.commit()
    conn.close()

def set_config(api_key=None, org_id=None, os_info=None, text_color=None, sudo_password=None, personality=None, user_display_name = None, wsl = None):
    conn = functions.db_connect()
    c = conn.cursor()
    c.execute("DELETE FROM config")  # Ensure only one entry is stored
    c.execute("""INSERT INTO config (api_key, org_id, os_info, text_color, sudo_password, personality, user_display_name, wsl) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (api_key, org_id, os_info, text_color, sudo_password, personality, user_display_name, wsl))
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

    # Check if running on Windows Subsystem for Linux
    if functions.is_wsl_subprocess():
        wsl = 1
    else:
        wsl = 0

    n = 3  # Number of colors per row
    max_length = max(len(color_name) for color_name in functions.COLOR_OPTIONS) + 2  # Calculate the max length of color names + padding
    print("Please choose a text color:")
    # Initialize a counter
    counter = 0
    # Display colors in rows of 'n'
    for color_name in functions.COLOR_OPTIONS:
        # Print the color name with its color code, and ensure consistent width with ljust
        print(f"{functions.COLOR_OPTIONS[color_name]}{color_name.ljust(max_length)}\033[0m", end="")
        counter += 1
        # Move to the next line after 'n' colors
        if counter % n == 0:
            print()  # New line
    # Handle the case if the last row has fewer than 'n' items
    if counter % n != 0:
        print()  # Ensure the cursor moves to the next line
    color_choice = input("Enter your color choice: ").strip()
    if color_choice not in functions.COLOR_OPTIONS:
        print("Invalid choice. Using default color. You can change this later using \033[1mfefe-setup text-color\033[0m")
        return

    initialize_db()
    user_display_name = user_info.get_display_name()
    set_config(api_key, org_id, os_info, color_choice, sudo_password, default_personality, user_display_name, wsl)
    print(f"Setup complete. You can now use the 'fefe' command.")


def choose_text_color():
    n = 3  # Number of colors per row
    max_length = max(len(color_name) for color_name in functions.COLOR_OPTIONS) + 2  # Calculate the max length of color names + padding
    print("Please choose a text color:")
    # Initialize a counter
    counter = 0
    # Display colors in rows of 'n'
    for color_name in functions.COLOR_OPTIONS:
        # Print the color name with its color code, and ensure consistent width with ljust
        print(f"{functions.COLOR_OPTIONS[color_name]}{color_name.ljust(max_length)}\033[0m", end="")
        counter += 1
        # Move to the next line after 'n' colors
        if counter % n == 0:
            print()  # New line
    # Handle the case if the last row has fewer than 'n' items
    if counter % n != 0:
        print()  # Ensure the cursor moves to the next line
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
    personality = input(f"Personality (default is '{default_personality}'): ").strip()
    if not personality:
        personality = default_personality

    conn = functions.db_connect()
    c = conn.cursor()
    c.execute("UPDATE config SET personality = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)", (personality,))
    conn.commit()
    conn.close()
    
    print(f"Personality set to '{personality}'.")


def update_wsl():
    wsl = functions.is_wsl_subprocess()
    if wsl:
        answer = input("Windows Subsystem for Linux (WSL) was detected. Enable support? (Yes/No [default]): ")
    else:
        answer = input("Windows Subsystem for Linux (WSL) was not detected. Enabling support may fail. Enable support anyways? (Yes/No [default]): ")

    conn = functions.db_connect()
    c = conn.cursor()
    
    if answer.lower() in ['y', 'yes']:
        # Set wsl support to enabled
        c.execute('UPDATE config SET wsl = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)', (1,))
        conn.commit()
        conn.close()
        
        # Install python-tk to enable TkAgg backend for matplotlib
        install_wsl_dependencies()
        print("wsl support enabled.")
    else:
        # Set wsl support to disabled
        c.execute('UPDATE config SET wsl = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)', (0,))
        conn.commit()
        conn.close()
        
        print("wsl support disabled.")

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

def install_wsl_dependencies():
    """Function to install python-tk package if not already installed."""
    try:
        import tkinter
        print("Tkinter is already installed.")
    except ImportError:
        print("Tkinter not found. Installing python-tk...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-tk"])
        print("Tkinter installation complete.")
    try:
        run_commands.run_commands(['sudo','apt','install','-y','wslu'])
    except Exception as e:
        print("Error installing the `wslu`, which Fefe uses to open images on Windows Subsystem for Linux. Install it manually with \033[1msudo apt install -y wslu\033[0m")


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
        elif sys.argv[1] == "wsl":
            update_wsl()
        elif sys.argv[1] == "wipe-memory":
            clear_chat_history()
        else:
            print("Invalid option. Use --help or -h for usage information.")
    else:
        print("Usage: fefe-setup [text-color | sudo | api-key | organization-id | personality | wipe-memory | wsl | --help | -h]")
