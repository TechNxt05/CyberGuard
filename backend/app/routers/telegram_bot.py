"""
Telegram bot: forward a suspicious message or screenshot, get a ScamShield verdict back.

Setup (free):
1. Create a bot with @BotFather and copy the token.
2. Set TELEGRAM_BOT_TOKEN and TELEGRAM_WEBHOOK_SECRET (any random string) on Render.
3. Run `python scripts/set_telegram_webhook.py https://<your-backend>.onrender.com` once.
"""
import base64
import logging
import os
import time
from collections import defaultdict, deque

import httpx
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from app.schemas.common import AnalysisRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations/telegram", tags=["Telegram"])

MAX_PHOTO_BYTES = 5 * 1024 * 1024
CHAT_LIMIT, CHAT_WINDOW_SECONDS = 5, 600
_chat_hits: dict[int, deque] = defaultdict(deque)

HELP_TEXT = (
    "Hi! I'm CyberGuard. Forward me any suspicious SMS, WhatsApp message, email text or screenshot "
    "and I'll tell you if it looks like a scam and what to do.\n\n"
    "I never need your OTP, PIN or password - never share those with anyone.\n"
    "Lost money? Call 1930 right away and report at https://cybercrime.gov.in"
)


def _token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise HTTPException(status_code=404, detail="Not found")
    return token


async def _send(chat_id: int, text: str) -> None:
    async with httpx.AsyncClient(timeout=15) as client:
        await client.post(f"https://api.telegram.org/bot{_token()}/sendMessage",
                          json={"chat_id": chat_id, "text": text[:4000], "disable_web_page_preview": True})


async def _download_photo(file_id: str) -> str | None:
    async with httpx.AsyncClient(timeout=20) as client:
        info = (await client.get(f"https://api.telegram.org/bot{_token()}/getFile", params={"file_id": file_id})).json()
        result = info.get("result") or {}
        if not result.get("file_path") or result.get("file_size", 0) > MAX_PHOTO_BYTES:
            return None
        data = await client.get(f"https://api.telegram.org/file/bot{_token()}/{result['file_path']}")
        return base64.b64encode(data.content).decode() if data.status_code == 200 else None


def _rate_limited(chat_id: int) -> bool:
    now = time.monotonic()
    hits = _chat_hits[chat_id]
    while hits and now - hits[0] > CHAT_WINDOW_SECONDS:
        hits.popleft()
    if len(hits) >= CHAT_LIMIT:
        return True
    hits.append(now)
    return False


def format_reply(result) -> str:
    report = result.scout_report
    icon = {"SCAM": "🚨", "SUSPICIOUS": "⚠️", "SAFE": "✅"}[report.verdict]
    lines = [f"{icon} {report.verdict} - risk {report.risk_score}/100", ""]
    if report.analysis_status == "failed":
        lines += ["Automated analysis couldn't finish, so treat this message as unverified.", ""]
    lines.append(result.explanation.simple_explanation or report.scam_logic)
    risky_links = [c for c in report.url_checks if c["verdict"] in ("malicious", "suspicious")]
    if risky_links:
        lines += ["", "Link checks:"] + [f"• {c['domain']}: {'; '.join(c['signals'])}" for c in risky_links]
    if result.action_plan.steps:
        lines += ["", "What to do:"] + [f"• {s}" for s in result.action_plan.steps[:5]]
    if report.verdict != "SAFE":
        lines += ["", "Lost money? Call 1930 now and report at https://cybercrime.gov.in"]
    return "\n".join(lines)


async def _handle(update: dict) -> None:
    from app.workflows.scamshield_graph import scamshield_app

    message = update.get("message") or update.get("edited_message") or {}
    chat_id = (message.get("chat") or {}).get("id")
    if not chat_id:
        return
    text = (message.get("text") or message.get("caption") or "").strip()
    if text in ("/start", "/help"):
        await _send(chat_id, HELP_TEXT)
        return
    if _rate_limited(chat_id):
        await _send(chat_id, "You've sent a lot of checks - please wait a few minutes and try again.")
        return

    image_b64 = None
    if message.get("photo"):
        image_b64 = await _download_photo(message["photo"][-1]["file_id"])  # last = highest resolution
    if not text and not image_b64:
        await _send(chat_id, "Send me the suspicious message as text, or a screenshot.")
        return

    await _send(chat_id, "🔎 Checking... this can take up to a minute.")
    try:
        state = await scamshield_app.ainvoke({"request": AnalysisRequest(message=text[:8000] or None, image_base64=image_b64, source="telegram")})
        await _send(chat_id, format_reply(state["final_output"]))
    except Exception:
        logger.exception("Telegram analysis failed")
        await _send(chat_id, "Sorry, I couldn't analyse that right now. Please try again in a minute. Never share OTPs or PINs.")


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    background: BackgroundTasks,
    x_telegram_bot_api_secret_token: str | None = Header(None),
):
    _token()
    secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    if not secret or x_telegram_bot_api_secret_token != secret:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # Acknowledge immediately; analysis runs after the response so Telegram doesn't retry the update.
    background.add_task(_handle, await request.json())
    return {"ok": True}
