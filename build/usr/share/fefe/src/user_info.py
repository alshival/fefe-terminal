import platform
import os
import ctypes
import subprocess
import pwd

def get_display_name():
    system = platform.system()
    
    if system == "Windows":
        return get_windows_display_name()
    elif system == "Darwin":  # macOS
        return get_mac_display_name()
    elif system == "Linux":
        return get_linux_display_name()
    else:
        return None

def get_windows_display_name():
    GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
    NameDisplay = 3  # This corresponds to the display name
    size = ctypes.pointer(ctypes.c_ulong(0))
    GetUserNameEx(NameDisplay, None, size)
    buffer = ctypes.create_unicode_buffer(size.contents.value)
    GetUserNameEx(NameDisplay, buffer, size)
    return buffer.value

def get_mac_display_name():
    result = subprocess.run(['osascript', '-e', 'long user name of (system info)'],
                            stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()

def get_linux_display_name():
    user_name = os.getenv("USER") or os.getenv("USERNAME")
    user_info = pwd.getpwnam(user_name)
    return user_info.pw_gecos.split(',')[0]