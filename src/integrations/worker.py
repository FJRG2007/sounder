import threading, importlib

def get_function(module_name, function_name="main"):
    return getattr(importlib.import_module(f"src.integrations.{module_name}"), function_name)

presences = ["discord"]

def update_all_presences(song_name, song_path):
    threads = []
    for presence in presences:
        thread = threading.Thread(target=lambda presence=presence:get_function(presence, f"update_{presence}_presence")(song_name, song_path))
        threads.append(thread)
        thread.start()