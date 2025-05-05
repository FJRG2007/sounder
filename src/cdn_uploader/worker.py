import os, importlib
from src.lib.config import config
from src.utils.basics import terminal

FAILED_CDNS = set()

def get_function(module_name, function_name="main"):
    return getattr(importlib.import_module(f"src.cdn_uploader.{module_name}"), function_name)

def upload_image_to_cdn(image_path, delete_after_seconds=60):
    IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    
    for cdn in config.presences.cdns:
        if cdn in FAILED_CDNS: continue

        try:
            if cdn == "fileio": result = get_function("fileio", "send_image_to_fileio")(image_path, delete_after_seconds)
            elif cdn == "catbox": result = get_function("catbox", "send_image_to_catbox")(image_path, delete_after_seconds)
            elif cdn == "cloudinary" and os.getenv("CLOUDINARY_CLOUD_NAME") and os.getenv("CLOUDINARY_API_KEY") and os.getenv("CLOUDINARY_API_SECRET"): result = get_function("cloudinary", "send_image_to_cloudinary")(image_path, delete_after_seconds)
            elif cdn == "imgur" and IMGUR_CLIENT_ID and len(IMGUR_CLIENT_ID) > 5: result = get_function("imgur", "send_image_to_imgur")(image_path, delete_after_seconds)
            elif cdn == "discordWebhook" and DISCORD_WEBHOOK_URL and len(DISCORD_WEBHOOK_URL) > 7: result = get_function("discord", "send_image_to_discord_via_webhook")(image_path)
            elif cdn == "discordBot" and DISCORD_BOT_TOKEN and len(DISCORD_BOT_TOKEN) > 7: result = get_function("discord", "send_image_to_discord_via_bot")(image_path)
            else: continue
            if result and isinstance(result, str): return result
            else: FAILED_CDNS.add(cdn)
        except Exception as e: 
            terminal("e", f"Error uploading image to {cdn} CDN: {e}")
            FAILED_CDNS.add(cdn)
        
    return "https://raw.githubusercontent.com/FJRG2007/sounder/refs/heads/main/defaults/album_art_path.png" # Default.