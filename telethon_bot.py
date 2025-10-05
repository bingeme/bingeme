import os
import asyncio
import requests
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ.get('API_ID', '0'))
API_HASH = os.environ.get('API_HASH', '')
SESSION = os.environ.get('TELEGRAM_SESSION', None)
CHANNELS = os.environ.get('CHANNELS', '')  
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK', '')  

if not (API_ID and API_HASH and SESSION):
    raise SystemExit("Missing API_ID / API_HASH / TELEGRAM_SESSION env vars")

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

def post_to_discord(file_path, text=""):
    if not DISCORD_WEBHOOK:
        return
    try:
        with open(file_path, "rb") as f:
            data = {"content": text[:1900]} if text else {}
            resp = requests.post(DISCORD_WEBHOOK, data=data, files={"file": f}, timeout=60)
        print("Discord upload status:", resp.status_code)
    except Exception as e:
        print("Discord upload error:", e)

@client.on(events.NewMessage(chats=CHANNELS))
async def handler(event):
    try:
        msg = event.message
        text = msg.message or ""
        if msg.media:
            print("Media detected, downloading...")
            path = await msg.download_media(file="/tmp")
            if path:
                print("Downloaded:", path)
                post_to_discord(path, text)
                try:
                    os.remove(path)
                except Exception as e:
                    print("Cleanup error:", e)
        else:
            if DISCORD_WEBHOOK and text.strip():
                requests.post(DISCORD_WEBHOOK, json={"content": text})
    except Exception as e:
        print("Handler exception:", e)

async def main():
    await client.start()
    print("Telethon client started. Listening...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
