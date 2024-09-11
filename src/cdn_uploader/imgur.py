import os, requests, threading
from src.utils.basics import terminal

def send_image_to_imgur(image_path, delete_after_seconds=60):
    try:
        IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
        if not IMGUR_CLIENT_ID or len(IMGUR_CLIENT_ID) < 5: return terminal("e", "Enter a IMGUR Client ID")
        with open(image_path, "rb") as image_file:
            response = requests.post("https://api.imgur.com/3/image", headers={"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}, files={"image": ("image.jpg", image_file, "image/jpeg")})
        if response.status_code == 200:
            data = response.json()["data"]
            threading.Timer(delete_after_seconds, delete_image_from_cdn, args=[data["deletehash"]]).start()
            return data["link"]
        else:
            terminal("e", f"Error uploading image: {response.json()}")
            return None
    except IOError as e:
        terminal("e", f"Error opening file: {e}")
        return None
    except Exception as e:
        terminal("e", f"Unexpected error: {e}")
        return None
    
def delete_image_from_cdn(delete_hash):
    try:
        IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
        if not IMGUR_CLIENT_ID or len(IMGUR_CLIENT_ID) < 5:
            terminal("e", "Enter a valid IMGUR Client ID")
            return False
        response = requests.delete(f"https://api.imgur.com/3/image/{delete_hash}", headers={"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"})
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