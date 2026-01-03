from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Bot Configuration
    BOT_NAME: str = os.getenv("BOT_NAME", "BusinessAI")
    BUSINESS_NAME: str = os.getenv("BUSINESS_NAME", "Your Business")
    SUPPORT_EMAIL: str = os.getenv("SUPPORT_EMAIL", "support@example.com")
    WELCOME_MESSAGE: str = os.getenv(
        "WELCOME_MESSAGE", 
        "Hello! I'm {bot_name} from {business_name}. How can I help you today?"
    )
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_WEBHOOK_URL: str = os.getenv("TELEGRAM_WEBHOOK_URL", "")
    
    # AI Configuration
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")  # openai or gemini
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-pro")
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", 0.7))
    
    # Business Settings
    BUSINESS_TIMEZONE: str = os.getenv("BUSINESS_TIMEZONE", "UTC")
    BUSINESS_HOURS_START: str = os.getenv("BUSINESS_HOURS_START", "09:00")
    BUSINESS_HOURS_END: str = os.getenv("BUSINESS_HOURS_END", "17:00")
    AFTER_HOURS_MESSAGE: str = os.getenv(
        "AFTER_HOURS_MESSAGE",
        "Our business hours are 9 AM to 5 PM. We'll respond during business hours."
    )
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///database/logs.db")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    # Features
    ENABLE_LEAD_CAPTURE: bool = True
    ENABLE_MULTILINGUAL: bool = True
    ENABLE_EXPORT: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()