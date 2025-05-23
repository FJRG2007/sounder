from src.utils.basics import terminal
import os, requests, logging, threading

def send_image_to_catbox(image_path, delete_after_seconds=60):
    try:
        if not os.path.isfile(image_path): return terminal("e", "Invalid image path.")

        with open(image_path, "rb") as image_file:
            files = {
                "fileToUpload": ("image.jpg", image_file, "image/jpeg")
            }
            data = {
                "reqtype": "fileupload"
            }
            response = requests.post("https://catbox.moe/user/api.php", data=data, files=files, timeout=5)

        if response.status_code == 200:
            image_url = response.text.strip()
            threading.Timer(delete_after_seconds, lambda: logging.info("Auto-delete simulated for Catbox (not supported).")).start()
            return image_url
        else:
            terminal("e", f"Error uploading image: {response.status_code} | {response.text}")
            return None
    except requests.exceptions.Timeout:
        terminal("e", f"Timeout after 5 seconds.")
        return None
    except Exception as e:
        terminal("e", f"Unexpected error: {e}")
        return None