import os, requests, threading
from src.utils.basics import terminal, add_log_line

def get_imgur_clients():
    raw = os.getenv("IMGUR_CLIENTS_ID", "")
    return [cid.strip() for cid in raw.split(",") if cid.strip()]

def is_rate_limited(response):
    try:
        errors = response.json().get("errors", [])
        for err in errors:
            if err.get("code") == "429": return True
    except Exception: pass
    return False

def send_image_to_imgur(image_path, delete_after_seconds=60):
    add_log_line(f"Uploading {image_path} to Imgur...")
    clients = get_imgur_clients()
    if not clients: return terminal("e", "No valid IMGUR Client IDs found in environment.")

    for client_id in clients:
        try:
            with open(image_path, "rb") as image_file:
                response = requests.post(
                    "https://api.imgur.com/3/image",
                    headers={ "Authorization": f"Client-ID {client_id}" },
                    files={ "image": ("image.jpg", image_file, "image/jpeg") }
                )

            if response.status_code == 200:
                data = response.json()["data"]
                threading.Timer(delete_after_seconds, delete_image_from_cdn, args=[data["deletehash"]]).start()
                return data["link"]
            elif is_rate_limited(response):
                terminal("w", f"Rate limit reached for Client-ID {client_id}. Trying next...")
                continue
            else:
                terminal("e", f"Upload failed with {client_id}: {response.json()}")
                break

        except IOError as e:
            terminal("e", f"Error opening file: {e}")
            return None
        except Exception as e:
            terminal("e", f"Unexpected error: {e}")
            return None

    terminal("e", "All Imgur Client IDs exhausted or failed.")
    return None
    
def delete_image_from_cdn(delete_hash):
    try:
        IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENTS_ID")
        if not IMGUR_CLIENT_ID or len(IMGUR_CLIENT_ID) < 5:
            terminal("e", "Enter a valid IMGUR Client ID")
            return False
        response = requests.delete(f"https://api.imgur.com/3/image/{delete_hash}", headers={ "Authorization": f"Client-ID {IMGUR_CLIENT_ID}" })
        if response.status_code == 200: return True
        else:
            terminal("e", f"Error deleting image: {response.json()}")
            return False
    except requests.RequestException as e:
        terminal("e", f"Request error: {e}")
        return False
    except Exception as e:
        terminal("e", f"Unexpected error: {e}")
        return False