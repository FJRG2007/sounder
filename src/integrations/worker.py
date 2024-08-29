import threading, importlib

def get_function(module_name, function_name="main"):
    return getattr(importlib.import_module(f"src.integrations.{module_name}"), function_name)

presences = ["discord"]

def update_all_presences(status, sound_name="", sound_path=""):
    threads = []
    for presence in presences:
        print(f"{"update" if status else "clear"}_{presence}_presence")
        thread = threading.Thread(target=lambda presence=presence:get_function(presence, f"{"update" if status else "clear"}_{presence}_presence")(*(sound_name, sound_path) if status else ()))
        threads.append(thread)
        thread.start()