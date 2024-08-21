import pexpect 
import subprocess 
from src import functions 
import os 
import getpass
import re


spec = {
        "type": "function",
        "function": {
            "name": "run_commands",
            "description": 
f"""
The `run_commands` tool allows you to run command line commands for the user. The user's operating system is {functions.get_system_info()}.
Run multiple commands by listing them within the `commands` parameter. For example, `commands=['pwd','ls -A']` will first run `pwd` followed by `ls -A`.
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "commands": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "A single command to run in the terminal."
                        },
                        "description": "List of commands to run in the terminal."
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "If false, suppresses the terminal output for a cleaner response. If false, returns the output. Defaults to `False`. Set value to True only if the user requests the output.",
                        "default": False,
                        "enum": [True, False]
                    }
                },
                "required": ["commands"]
            }
        }
    }

def run_command(command,verbose):
    shell_command = f'/bin/bash -c "{command}"'
    child = pexpect.spawn(shell_command, timeout=500)
    output = ""
    error_output = ""

    while True:
        try:
            i = child.expect([pexpect.TIMEOUT, pexpect.EOF, r'[Pp]assword', r'[Yy]es/[Nn]o', r'Enter.*:', r'.*\? $'], timeout=600)

            output += child.before.decode('utf-8')
            
            if i == 0:  # TIMEOUT
                print("Command timed out.")
                error_output += "Command timed out."
                break 
            
            elif i == 1:  # EOF
                break
            
            elif i == 2:  # Password prompt
                sudo_pass = functions.get_sudo()
                if sudo_pass:
                    child.sendline(sudo_pass)
                # Securely get the password from the user
                else:
                    password = getpass.getpass(f"[sudo] password for {os.getlogin()}: ").strip()
                    child.sendline(password)
            
            elif i == 3:  # Yes/No prompt
                response = input(f"Command {command} asks for confirmation (Yes/No): ")
                child.sendline(response)
            
            elif i == 4:  # Generic prompt ending with ':'
                response = input(f"Command {command} asks for input: ")
                child.sendline(response)
                
        except pexpect.exceptions.EOF:
            output += child.before.decode('utf-8')
            break
        
        except pexpect.TIMEOUT:
            error_output += "Command timed out unexpectedly."
            print("Command timed out unexpectedly.")
            break
        
        except pexpect.ExceptionPexpect as e:
            error_message = f"An error occurred: {str(e)}"
            error_output += error_message
            print(error_message)
            output += child.before.decode('utf-8')
            break

    # Combine the standard output and error output
    if len(error_output)>1:
        final_output = output + "\n" + error_output +"\n"
    else:
        final_output = output
    if verbose:
        print(final_output)
    return final_output

def run_command_v2(command,verbose=False):
    password = functions.get_sudo()
    if password is not None:
        try:
            # Prepare the command to echo the password and pipe it to sudo
            full_command = f'echo {password} | sudo -S {command}'
            result = subprocess.run(full_command, shell=True, check=True, text=True, capture_output=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error executing command: {e}\n{e.output}"
    else:
        run_command(command,verbose)


def run_commands(commands,verbose=False):
    outputs = []
    for command in commands:
        print(f"\nRunning command: {command}\n")
        command_output = run_command(command, verbose)
        outputs.append(command_output)
    
    outputs.append("Done.")
    return outputs
