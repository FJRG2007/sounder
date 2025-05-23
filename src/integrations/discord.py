import os, time
from pypresence import Presence
from src.lib.config import config
from src.lib.ignored import ignored_errors
from src.cdn_uploader.worker import upload_image_to_cdn
from src.utils.basics import terminal, get_sound_data, add_log_line

# Global variable to hold the RPC instance.
rpc = None
DiscordNotInstalledError = False

def init_discord_presence():
    global rpc, DiscordNotInstalledError
    DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
    if DISCORD_CLIENT_ID and len(DISCORD_CLIENT_ID) > 5:
        try:
            rpc = Presence(DISCORD_CLIENT_ID)
            rpc.connect()
        except Exception as e:
            if "Could not find Discord installed" in str(e) and not DiscordNotInstalledError:
                DiscordNotInstalledError = True
                rpc = False
                terminal("w", f"Discord is closed or not installed.")
            else: terminal("e", f"Error connecting to Discord Rich Presence: {e}")

def update_discord_presence(sound_name, sound_path, retries=2):
    global rpc, DiscordNotInstalledError
    if type(rpc) is not Presence: init_discord_presence()
    if DiscordNotInstalledError: return
    sound_data = get_sound_data(sound_path)
    if sound_data["duration"] is None: return
    while retries >= 0:
        try:
            image = upload_image_to_cdn(sound_data["album_art_path"], sound_data["duration"] + 15)
            add_log_line(f"Updating Discord presence: {sound_data['sound_name']} by {sound_data['artist']} with image URL {image}")
            rpc.update(
                state=sound_data["sound_name"],
                large_text=sound_data["sound_name"],
                small_text=sound_data["sound_name"],
                large_image=image,
                details=sound_data["artist"],
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
            try: 
                if type(rpc) is not Presence or rpc is False: break
            except Exception as e: pass
            if any(msg in str(e).lower() for msg in ignored_errors) and rpc:
                if config.general.developer_mode: terminal("w", "Event loop is closed. Attempting to reinitialize Discord presence...")
                init_discord_presence()
                retries -= 1
                if retries < 0: terminal("e", "Failed to update Discord presence after retry attempts."); break
            else:
                if any(msg in str(e).lower() for msg in ignored_errors) and config.general.developer_mode: terminal("i", f"Ignoring known Discord presence update error: {e}")
                else: terminal("e", f"Error updating Discord presence: {e}")
                break
        except Exception as e:
            if not any(msg in str(e).lower() for msg in ignored_errors): terminal("e", f"Error updating Discord presence: {e}")
            break

def clear_discord_presence():
    global rpc
    if isinstance(rpc, Presence):
        try: 
            rpc.close()
            rpc = False
        except Exception as e: terminal("e", f"Error clearing Discord presence: {e}")