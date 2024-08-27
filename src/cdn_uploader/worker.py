import os, json, importlib

config = None

def get_function(module_name, function_name="main"):
    return getattr(importlib.import_module(f"src.cdn_uploader.{module_name}"), function_name)

def upload_image_to_cdn(image_path, delete_after_seconds=60):
    IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    with open("./config.json", "r") as f:
        config = json.load(f)
        cdn_preference = config.get("CDN_preference", [])
    for cdn in cdn_preference:
        if cdn == "imgur" and IMGUR_CLIENT_ID and len(IMGUR_CLIENT_ID) > 5: return get_function("imgur", "send_image_to_imgur")(image_path, delete_after_seconds)
        elif cdn == "discordWebHook" and DISCORD_WEBHOOK_URL and len(DISCORD_WEBHOOK_URL) > 7: return get_function("discord", "send_image_to_discord_via_webhook")(image_path)
        elif cdn == "discordBot" and DISCORD_BOT_TOKEN and len(DISCORD_BOT_TOKEN) > 7: return get_function("discord", "send_image_to_discord_via_bot")(image_path)