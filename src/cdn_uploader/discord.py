import os, discord, requests
from discord.ext import commands
from src.utils.basics import add_log_line

def send_image_to_discord_via_webhook(file_path):
    add_log_line(f"Uploading {file_path} to Discord via webhook...")
    with open(file_path, "rb") as f:
        response = requests.post(os.getenv("DISCORD_WEBHOOK_URL"), files={ "file": f })
    response.raise_for_status()
    res = response.json()
    url = res.get("attachments", [{}])[0].get("proxy_url") or res.get("attachments", [{}])[0].get("url")
    add_log_line(f"Uploaded {file_path} to Discord via webhook. URL: {url}")
    return url

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="sounder", intents=intents)

async def send_image_to_discord_via_bot(ctx, file_path):
    add_log_line(f"Uploading {file_path} to Discord via bot...")
    url = await ctx.send(file=discord.File(file_path)).attachments[0].url
    add_log_line(f"Uploaded {file_path} to Discord via bot. URL: {url}")
    return url 

if __name__ == "__main__":
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if DISCORD_BOT_TOKEN and len(DISCORD_BOT_TOKEN) > 7: bot.run(DISCORD_BOT_TOKEN)