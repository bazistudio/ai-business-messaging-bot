from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv

from app.config import settings
from app.bot.telegram import telegram_router
from app.admin.logs import admin_router
from app.services.faq_service import faq_router
from app.services.order_service import order_router
from app.services.booking_service import booking_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Business Messaging Bot",
    description="AI-powered customer support bot for Telegram",
    version="1.0.0",
    docs_url="/admin/docs",
    redoc_url="/admin/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(telegram_router, prefix="/webhook", tags=["Telegram Bot"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(faq_router, prefix="/api", tags=["FAQ"])
app.include_router(order_router, prefix="/api", tags=["Orders"])
app.include_router(booking_router, prefix="/api", tags=["Booking"])

@app.get("/", response_class=HTMLResponse)
async def root():
    return f"""
    <html>
        <head>
            <title>{settings.BOT_NAME} - AI Business Bot</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .container {{ background: #f5f5f5; padding: 30px; border-radius: 10px; }}
                h1 {{ color: #2563eb; }}
                .status {{ background: #10b981; color: white; padding: 10px; border-radius: 5px; }}
                .endpoints {{ margin-top: 30px; }}
                .endpoint {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #2563eb; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 {settings.BOT_NAME}</h1>
                <p>AI-powered customer support bot for {settings.BUSINESS_NAME}</p>
                
                <div class="status">
                    ✅ Bot is running successfully
                </div>
                
                <div class="endpoints">
                    <h3>Available Endpoints:</h3>
                    <div class="endpoint">
                        <strong>📱 Telegram Webhook:</strong> POST /webhook/telegram
                    </div>
                    <div class="endpoint">
                        <strong>👨‍💼 Admin Dashboard:</strong> <a href="/admin/docs">/admin/docs</a>
                    </div>
                    <div class="endpoint">
                        <strong>📊 Message Logs:</strong> GET /admin/logs
                    </div>
                    <div class="endpoint">
                        <strong>🗑️ GDPR Delete:</strong> DELETE /admin/user/{'{user_id}'}
                    </div>
                    <div class="endpoint">
                        <strong>🔧 Health Check:</strong> GET /health
                    </div>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                    <h4>📞 Support</h4>
                    <p>Email: {settings.SUPPORT_EMAIL}</p>
                    <p>Business Hours: {settings.BUSINESS_HOURS_START} - {settings.BUSINESS_HOURS_END} ({settings.BUSINESS_TIMEZONE})</p>
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-business-messaging-bot",
        "version": "1.0.0",
        "ai_provider": settings.AI_PROVIDER,
        "business": settings.BUSINESS_NAME,
        "bot_name": settings.BOT_NAME
    }

@app.get("/privacy")
async def privacy_policy():
    return {
        "privacy_policy": f"""
        Privacy Policy for {settings.BUSINESS_NAME}
        
        1. Data Collection: We store conversation logs to improve our services.
        2. Data Usage: Messages are processed by AI to provide customer support.
        3. Data Retention: Logs are retained for 30 days unless deleted earlier.
        4. User Rights: You can request deletion of your data via DELETE /admin/user/{{user_id}}
        5. Contact: {settings.SUPPORT_EMAIL}
        
        This bot complies with GDPR requirements. For data deletion, contact us.
        """
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG_MODE
    )