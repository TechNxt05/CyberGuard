"""
Registers the bot's webhook with Telegram (run once after deploying).

    python scripts/set_telegram_webhook.py https://your-backend.onrender.com
"""
import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

if len(sys.argv) != 2:
    raise SystemExit(__doc__)
token, secret = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_WEBHOOK_SECRET")
if not token or not secret:
    raise SystemExit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_WEBHOOK_SECRET first.")

url = sys.argv[1].rstrip("/") + "/integrations/telegram/webhook"
resp = httpx.post(f"https://api.telegram.org/bot{token}/setWebhook",
                  json={"url": url, "secret_token": secret, "allowed_updates": ["message", "edited_message"]})
print(resp.json())
