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
      --help, -h            Show this help message and exit.
      text-color            Choose a text color for your fefe configuration.
                            This will prompt you to select a color and save it to your configuration.
      sudo                  Update your stored sudo password.
      openai-api            Update your OpenAI API key.
      google-api            Update your Google API key.
      personality           Update the personality for your fefe configuration.
      wipe-memory           Wipe Fefe's memory. Clears the chat history.
      wsl                   Enable or disable WSL (Windows Subsystem for Linux) support.
      (no option)           Run the setup process to configure your OpenAI API key,
                            Organization ID, system information, sudo password, 
                            text color, and personality.

    Description:
      The fefe-setup command is used to initialize or update the configuration
      for the 'fefe' command-line tool. You can set or update your OpenAI API key,
      Google API key, Organization ID, system information, sudo password, 
      text color, personality, and WSL (Windows Subsystem for Linux) support.
      
    Examples:
      fefe-setup            Starts the setup process.
      fefe-setup text-color Allows you to choose a new text color for your output.
      fefe-setup sudo       Updates your stored sudo password.
      fefe-setup openai-api Updates your OpenAI API credentials.
      fefe-setup google-api Updates your Google API credentials.
      fefe-setup personality
                           Updates the personality for your fefe configuration.
      fefe-setup image-gen  Set output size for image generator (default 1024x1024)
      fefe-setup wipe-memory
                           Wipe Fefe's memory. Useful when bot becomes confused or when you wish to start fresh.
      fefe-setup wsl        Enable or disable Windows Subsystem for Linux support.
    """
    print(help_message)


def initialize_db():
    conn = functions.db_connect()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    openai_api_key TEXT, 
                    org_id TEXT, 
                    os_info TEXT,
                    text_color TEXT,
                    sudo_password TEXT,
                    personality TEXT,
                    user_display_name TEXT,
                    wsl INTEGER
                );''')
    
    c.execute("SELECT COUNT(*) FROM CONFIG")
    count = c.fetchone()[0]

    if count == 0:
        os_info = functions.get_system_info()
        wsl = 1 if functions.is_wsl_subprocess() else 0
        user_display_name = user_info.get_display_name()
        c.execute("""INSERT INTO config (openai_api_key, org_id, os_info, text_color, sudo_password, personality, user_display_name, wsl) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (None, None, os_info, None, None, default_personality, user_display_name, wsl))


    c.execute('''CREATE TABLE IF NOT EXISTS config_extras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    google_api_key TEXT,
                    image_gen_size TEXT
                );''')
    
    # Check if config_extras table is empty
    c.execute("SELECT COUNT(*) FROM config_extras")
    count = c.fetchone()[0]
    
    if count == 0:
        # Insert an empty row into config_extras if the table is empty
        c.execute("INSERT INTO config_extras (google_api_key, image_gen_size) VALUES (NULL,'1024x1024')")

    c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT,
                    source_id INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
              );''')
    
    conn.commit()
    conn.close()

def setup():
    # Now call the individual update functions
    update_openai_api(quiet=True)
    update_sudo_password(quiet=True)
    choose_text_color(quiet=True)
    update_personality(quiet=True)

    print(f"Setup complete. You can now use the 'fefe' command.")

def choose_text_color(quiet = False):
    initialize_db()
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
    if not quiet:
        print(f"Text color set to {color_choice}.")


def update_openai_api(quiet = False):
    initialize_db()
    openai_api_key = getpass.getpass("Please enter your OpenAI API key: ").strip()
    if not openai_api_key:
        print("API key cannot be empty. No changes were made.")
        return
    org_id = input("Please enter your Organization ID (Optional): ").strip()
    if not org_id:
        org_id = None  # Allow empty organization ID

    conn = functions.db_connect()
    c = conn.cursor()
    c.execute("UPDATE config SET openai_api_key = ?, org_id WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)", (openai_api_key,org_id,))
    conn.commit()
    conn.close()
    if not quiet:
        print("OpenAI API credentials updated successfully.")

def update_google_api_key(quiet = False):
    initialize_db()
    google_api_key = getpass.getpass("Please enter your Google API key: ").strip()
    if not google_api_key:
        print("API key cannot be empty. No changes were made.")
        return

    conn = functions.db_connect()
    c = conn.cursor()
    c.execute("UPDATE config_extras SET google_api_key = ? WHERE id = (SELECT id FROM config_extras ORDER BY id DESC LIMIT 1)", (google_api_key,))
    conn.commit()
    conn.close()
    if not quiet:
        print("Google API key updated successfully.")

def update_sudo_password(quiet = False):
    initialize_db()
    sudo_password = getpass.getpass("Please enter your sudo password (Optional): ").strip()
    if not sudo_password:
        print("Sudo password cannot be empty. No changes were made.")
        return

    conn = functions.db_connect()
    c = conn.cursor()
    c.execute("UPDATE config SET sudo_password = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)", (sudo_password,))
    conn.commit()
    conn.close()
    if not quiet:
        print("Sudo password updated successfully.")


def update_personality(quiet = False):
    initialize_db()
    personality = input(f"Set Fefe's personality (default is '{default_personality}'): ").strip()

    if not personality:
        personality = default_personality

    conn = functions.db_connect()
    c = conn.cursor()
    c.execute("UPDATE config SET personality = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)", (personality,))
    conn.commit()
    conn.close()
    if not quiet:
        print(f"Personality set to '{personality}'.")


def update_wsl(quiet = False):
    initialize_db()
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
        if not quiet:
            print("wsl support enabled.")
    else:
        # Set wsl support to disabled
        c.execute('UPDATE config SET wsl = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)', (0,))
        conn.commit()
        conn.close()
        if not quiet:
            print("wsl support disabled.")

def clear_chat_history(quiet = False):
    initialize_db()
    print("Would you like to wipe Fefe's memory?")
    answer = input("Yes/No: ").strip()
    if answer.lower() in ['y', 'yes']:
        functions.clear_chat_history()
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

def select_image_gen_size(quiet = False):
    choices = ["1024x1024", "1024x1792", "1792x1024"]
    
    print("Set output size for image generator:")
    for i, choice in enumerate(choices, start=1):
        print(f"{i}. {choice}")
    
    while True:
        try:
            selection = int(input("Choose 1, 2, or 3: "))
            if 1 <= selection <= len(choices):
                return choices[selection - 1]
            else:
                print("Invalid selection, please choose a number between 1 and 3.")
        except ValueError:
            print("Invalid input, please enter a number.")

def configure_image_gen(quiet = False):
    image_size = select_image_gen_size()
    db = functions.db_connect()
    cursor = db.cursor()
    cursor.execute("UPDATE config_extras SET image_gen_size = ? WHERE id = (SELECT id FROM config_extras ORDER BY id DESC LIMIT 1)", (image_size,))
    db.commit()
    db.close()
    if not quiet:
        print(f"Output size of image generator set to: {image_size}")

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
        elif sys.argv[1] == "openai-api":
            update_openai_api()
        elif sys.argv[1] == "personality":
            update_personality()
        elif sys.argv[1] == "wsl":
            update_wsl()
        elif sys.argv[1] == "wipe-memory":
            clear_chat_history()
        elif sys.argv[1] == "google-api":
            update_google_api_key()
        elif sys.argv[1] == "image-gen":
            configure_image_gen()
        else:
            print("Invalid option. Use --help or -h for usage information.")
    else:
        print("Usage: fefe-setup [text-color | sudo | api-key | organization-id | personality | wipe-memory | wsl | --help | -h]")
