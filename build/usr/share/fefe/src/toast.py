import platform
import os

def send_toast(title, text):
    if platform.system() == 'Linux':
        send_linux_toast(title, text)
    elif platform.system() == 'Windows':
        send_windows_toast(title, text)
    elif platform.system() == 'Darwin':
        send_mac_toast(title, text)
    else:
        print(f"Platform {platform.system()} not supported for toast notifications.")

def send_linux_toast(title, text):
    try:
        # Attempt to use notify-send for Linux (most common)
        os.system(f'notify-send --expire-time=5000 --icon="/usr/share/fefe/fefe.png" --app-name=Fefe "{title}" "{text}"')
    except Exception as e:
        print(f"Failed to send Linux toast: {e}")

def send_windows_toast(title, text):
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, text, duration=10)
    except ImportError:
        print("win10toast not installed. Please install it with 'pip install win10toast'")
    except Exception as e:
        print(f"Failed to send Windows toast: {e}")

def send_mac_toast(title, text):
    try:
        os.system(f'''
                  osascript -e 'display notification "{text}" with title "{title}"'
                  ''')
    except Exception as e:
        print(f"Failed to send Mac toast: {e}")
