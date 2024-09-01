import os, time
from pypresence import Presence
from src.utils.basics import terminal, get_sound_data
from src.cdn_uploader.worker import upload_image_to_cdn

# Global variable to hold the RPC instance.
rpc = None

def init_discord_presence():
    global rpc
    DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
    if DISCORD_CLIENT_ID and len(DISCORD_CLIENT_ID) > 5:
        try:
            rpc = Presence(DISCORD_CLIENT_ID)
            rpc.connect()
        except Exception as e: terminal("e", f"Error connecting to Discord Rich Presence: {e}")

def update_discord_presence(song_name, song_path, retries=2):
    global rpc
    if rpc is None: init_discord_presence()
    sound_data = get_sound_data(song_path)
    if sound_data["duration"] is None: return
    while retries >= 0:
        try:
            rpc.update(
                state=song_name,
                large_text=song_name,
                small_text=song_name,
                large_image=upload_image_to_cdn(sound_data["album_art_path"], sound_data["duration"] + 15),
                details="Enjoying some tunes!",
                start=int(time.time()),
                end=int(time.time()) + sound_data["duration"],
                buttons=[
                    {
                        "label": "View on GitHub",
                        "url": "https://github.com/FJRG2007/sounder"
                    }
                ]
            )
            break
        except RuntimeError as e:
            if rpc is False: break
            if "Event loop is closed" in str(e) and rpc:
                terminal("w", "Event loop is closed. Attempting to reinitialize Discord presence...")
                init_discord_presence()
                retries -= 1
                if retries < 0: terminal("e", "Failed to update Discord presence after retry attempts"); break
            else: terminal("e", f"Error updating Discord presence: {e}"); break
        except Exception as e: terminal("e", f"Error updating Discord presence: {e}"); break

def clear_discord_presence():
    global rpc
    if rpc is not None and rpc is not False:
        try: 
            rpc.close()
            rpc = False
        except Exception as e: terminal("e", f"Error clearing Discord presence: {e}")