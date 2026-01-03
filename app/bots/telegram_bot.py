from fastapi import APIRouter, Request
import requests
from app.config import TELEGRAM_BOT_TOKEN, AI_PROVIDER
from app.ai.openai_client import get_ai_response

telegram_router = APIRouter()

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

@telegram_router.post("/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()
    chat_id = data["message"]["chat"]["id"]
    user_text = data["message"]["text"]

    reply = get_ai_response(user_text)

    requests.post(TELEGRAM_API, json={
        "chat_id": chat_id,
        "text": reply
    })

    return {"ok": True}
