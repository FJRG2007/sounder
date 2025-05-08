from src.utils.basics import terminal, add_log_line
import os, threading, cloudinary, cloudinary.uploader

# Configuración inicial
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def send_image_to_cloudinary(image_path, delete_after_seconds=60):
    try:
        if not os.path.isfile(image_path): return terminal("e", "Invalid image path.")
        result = cloudinary.uploader.upload(image_path)
        image_url = result.get("secure_url")
        public_id = result.get("public_id")
        if image_url and public_id:
            threading.Timer(delete_after_seconds, delete_image_from_cdn, args=[public_id]).start()
            return image_url
        else:
            terminal("e", "Upload failed: Missing URL or public_id.")
            return None
    except Exception as e:
        terminal("e", f"Unexpected error: {e}")
        return None

def delete_image_from_cdn(public_id):
    try:
        result = cloudinary.uploader.destroy(public_id)
        if result.get("result") == "ok":
            add_log_line("i", f"Image '{public_id}' deleted from Cloudinary.")
            return True
        else:
            add_log_line("e", f"Error deleting image: {result}")
            return False
    except Exception as e:
        terminal("e", f"Unexpected error during delete: {e}")
        return False
