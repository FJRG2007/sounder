import requests, threading
from src.utils.basics import terminal

def send_image_to_fileio(image_path, delete_after_seconds=60):
    try:
        with open(image_path, "rb") as image_file:
            response = requests.post("https://file.io", files={ "file": image_file })

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("success"):
                    file_url = data["link"]
                    file_id = data["key"]
                    threading.Timer(delete_after_seconds, delete_image_from_fileio, args=[file_id]).start()
                    return file_url
                else: terminal("e", f"Error uploading image: {data}")
            except ValueError: terminal("e", "Empty or invalid JSON in upload response.")
        else:
            try: terminal("e", f"Error uploading image: {response.json()}")
            except ValueError: terminal("e", f"Error uploading image: Non-JSON response with status {response.status_code}")

        return None
    except IOError as e:
        terminal("e", f"Error opening file: {e}")
        return None
    except Exception as e:
        terminal("e", f"Unexpected error: {e}")
        return None

def delete_image_from_fileio(file_id):
    try:
        response = requests.delete(f"https://file.io/{file_id}")
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("success"): return True
                else: terminal("e", f"Error deleting image: {data}")
            except ValueError: terminal("e", "Empty or invalid JSON in delete response.")
        else:
            try: terminal("e", f"Error deleting image: {response.json()}")
            except ValueError: terminal("e", f"Error deleting image: Non-JSON response with status {response.status_code}")

        return False
    except requests.RequestException as e:
        terminal("e", f"Request error: {e}")
        return False
    except Exception as e:
        terminal("e", f"Unexpected error: {e}")
        return False