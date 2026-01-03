from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel
import requests
import json
import uuid
from datetime import datetime
from typing import Optional

from app.config import settings
from app.ai.openai_client import ai_client
from app.services.faq_service import FAQService
from app.services.order_service import OrderService
from app.services.booking_service import BookingService
from app.admin.logs import log_message, capture_lead
from app.models.message import MessageType

# Models
class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[dict] = None
    callback_query: Optional[dict] = None

class TelegramUser(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None

# Router
telegram_router = APIRouter()

# Services
faq_service = FAQService()
order_service = OrderService()
booking_service = BookingService()

# Webhook verification
@telegram_router.get("/telegram")
async def verify_webhook(request: Request):
    """Verify Telegram webhook"""
    return {"status": "Telegram webhook endpoint ready"}

@telegram_router.post("/telegram")
async def handle_telegram_webhook(
    request: Request, 
    background_tasks: BackgroundTasks
):
    """Handle incoming Telegram messages"""
    
    try:
        update = await request.json()
        
        if "message" in update:
            message = update["message"]
            
            # Extract message details
            chat_id = message["chat"]["id"]
            user_id = message["from"]["id"]
            user_name = message["from"].get("first_name", "User")
            text = message.get("text", "")
            
            # Generate unique message ID
            message_id = str(uuid.uuid4())
            
            # Log incoming message
            background_tasks.add_task(
                log_message,
                message_id=message_id,
                user_id=str(user_id),
                platform="telegram",
                message_type=MessageType.INCOMING,
                content=text,
                metadata={
                    "user_name": user_name,
                    "chat_id": chat_id,
                    "update_id": update["update_id"]
                }
            )
            
            # Process message in background
            background_tasks.add_task(
                process_telegram_message,
                chat_id=chat_id,
                user_id=user_id,
                user_name=user_name,
                text=text,
                message_id=message_id
            )
        
        return {"status": "ok"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_telegram_message(
    chat_id: int,
    user_id: int,
    user_name: str,
    text: str,
    message_id: str
):
    """Process Telegram message and send response"""
    
    try:
        # Check if it's a command
        if text.startswith("/"):
            response_text = await handle_command(text, user_id)
        else:
            # Detect language
            language = ai_client.detect_language(text)
            
            # Get AI response
            ai_response = await ai_client.generate_response(text, language=language)
            response_text = ai_response["text"]
            
            # Check for lead capture opportunities
            if settings.ENABLE_LEAD_CAPTURE and any(
                keyword in text.lower() for keyword in 
                ["interested", "contact me", "email", "phone", "callback"]
            ):
                response_text += "\n\n📝 Could you share your email or phone number so we can follow up?"
                capture_lead(str(user_id), user_name, "telegram", text)
        
        # Send response
        await send_telegram_message(chat_id, response_text)
        
        # Log outgoing message
        log_message(
            message_id=f"resp_{message_id}",
            user_id=str(user_id),
            platform="telegram",
            message_type=MessageType.OUTGOING,
            content=response_text,
            metadata={
                "ai_provider": ai_response["provider"],
                "ai_model": ai_response["model"],
                "language": language
            }
        )
    
    except Exception as e:
        error_message = f"Sorry, I encountered an error: {str(e)}"
        await send_telegram_message(chat_id, error_message)

async def handle_command(command: str, user_id: int) -> str:
    """Handle bot commands"""
    
    command = command.lower()
    
    if command == "/start":
        welcome = settings.WELCOME_MESSAGE.format(
            bot_name=settings.BOT_NAME,
            business_name=settings.BUSINESS_NAME
        )
        return welcome
    
    elif command == "/help":
        return """Available commands:
/start - Start conversation
/help - Show this help
/order - Check order status
/booking - Make a booking
/faq - Frequently asked questions
/hours - Business hours
/privacy - Privacy policy"""
    
    elif command == "/order":
        return "Please share your order number, and I'll check the status for you."
    
    elif command == "/booking":
        return "I can help you make a booking. What date and time are you looking for?"
    
    elif command == "/faq":
        faqs = faq_service.get_faqs()
        return "\n\n".join([f"Q: {q}\nA: {a}" for q, a in faqs.items()])
    
    elif command == "/hours":
        return f"Business Hours: {settings.BUSINESS_HOURS_START} to {settings.BUSINESS_HOURS_END} ({settings.BUSINESS_TIMEZONE})"
    
    elif command == "/privacy":
        return f"Privacy Policy: https://yourdomain.com/privacy"
    
    else:
        return "I didn't recognize that command. Type /help for available commands."

async def send_telegram_message(chat_id: int, text: str):
    """Send message to Telegram"""
    
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return None

# Webhook setup endpoint
@telegram_router.post("/telegram/setup")
async def setup_telegram_webhook():
    """Set up Telegram webhook"""
    
    if not settings.TELEGRAM_BOT_TOKEN:
        return {"error": "TELEGRAM_BOT_TOKEN not configured"}
    
    if not settings.TELEGRAM_WEBHOOK_URL:
        return {"error": "TELEGRAM_WEBHOOK_URL not configured"}
    
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook"
    
    payload = {
        "url": f"{settings.TELEGRAM_WEBHOOK_URL}/webhook/telegram"
    }
    
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        
        if result.get("ok"):
            return {
                "status": "success",
                "message": "Telegram webhook set up successfully",
                "webhook_url": payload["url"]
            }
        else:
            return {
                "status": "error",
                "message": result.get("description", "Unknown error")
            }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}