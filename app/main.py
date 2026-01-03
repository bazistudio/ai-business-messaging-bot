from fastapi import FastAPI
from app.bots.telegram_bot import telegram_router

app = FastAPI(title="AI Customer Support Bot")

app.include_router(telegram_router, prefix="/webhook")

@app.get("/")
def health():
    return {"status": "running"}
