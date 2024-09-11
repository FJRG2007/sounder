from src.lib.config import config
from src.utils.basics import terminal
import time, src.lib.globals as globals, platform, threading, importlib
try: from evdev import InputDevice, list_devices, ecodes
except ImportError: InputDevice = list_devices = ecodes = None
from pynput import keyboard

last_call_time = 0

def get_function(function_name="main"):
    global is_playing, last_call_time
    current_time = time.time()
    if current_time - last_call_time < 0.7: return lambda: None # Return a lambda that does nothing.
    # Update the timestamp of the last function call.
    last_call_time = current_time
    try:
        module = importlib.import_module("main")
        func = getattr(module, function_name, lambda: None)
        if callable(func): return func
        else:
            terminal("e", f"Function '{function_name}' is not callable or does not exist.")
            return lambda: None
    except ImportError as e:
        terminal("e", f"Error importing module: {e}")
        return lambda: None

def macros_button_listener_linux(device_path):
    try:
        device = InputDevice(device_path)
        if config.macros.prioritize_media_buttons: device.grab() # Grab the device exclusively so that the system doesn't receive the events.
        for event in device.read_loop():
            if event.type == ecodes.EV_KEY and event.value == 1: # Key press.
                function_name = {
                    ecodes.KEY_PLAYPAUSE: "play_sound" if not globals.is_playing else "stop_sound",
                    ecodes.KEY_NEXTSONG: "next_sound"
                }.get(event.code)
                if function_name: get_function(function_name)()
    except Exception as e: terminal("e", f"Error in headphone button listener: {e}")

def find_macros_device_linux():
    for device in [InputDevice(path) for path in list_devices()]:
        if "headphone" in device.name.lower() or "media" in device.name.lower(): return device.path
    return None

def on_press(key):
    try:
        function_name = {
            keyboard.Key.media_play_pause: "play_sound" if not globals.is_playing else "stop_sound",
            keyboard.Key.media_next: "next_sound",
            keyboard.Key.media_previous: "prev_sound"
        }.get(key)
        if function_name: get_function(function_name)()
    except ZeroDivisionError: pass
    except Exception as e: terminal("e", f"Error in keyboard listener: {e}")

def start_macros():
    if not config.macros.status: return
    def run_macros():
        os_name = platform.system()
        if os_name == "Linux" and evdev:
            macros_device_path = find_macros_device_linux()
            if macros_device_path: threading.Thread(target=macros_button_listener_linux, args=(macros_device_path,)).start()
        elif os_name in ["Darwin", "Windows"]:
            try:
                listener = keyboard.Listener(on_press=on_press)
                listener.start()
                listener.join()
            except Exception as e: terminal("e", f"Error in keyboard listener: {e}")
            finally:
                if listener and listener.running: listener.stop()
    # Run the above logic in a separate thread.
    threading.Thread(target=run_macros).start()