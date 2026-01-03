import openai
import google.generativeai as genai
from typing import Dict, Any, Optional
from app.config import settings
import json

class AIClient:
    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower()
        
        if self.provider == "openai":
            openai.api_key = settings.OPENAI_API_KEY
        elif self.provider == "gemini":
            genai.configure(api_key=settings.GEMINI_API_KEY)
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
    
    async def generate_response(
        self, 
        user_message: str, 
        context: Optional[str] = None,
        language: str = "English"
    ) -> Dict[str, Any]:
        """Generate AI response with context awareness"""
        
        system_prompt = self._build_system_prompt(context, language)
        
        try:
            if self.provider == "openai":
                return await self._openai_response(user_message, system_prompt)
            else:
                return await self._gemini_response(user_message, system_prompt)
        except Exception as e:
            return self._fallback_response(str(e))
    
    def _build_system_prompt(self, context: Optional[str], language: str) -> str:
        """Build system prompt with business context"""
        
        base_prompt = f"""You are {settings.BOT_NAME}, an AI assistant for {settings.BUSINESS_NAME}.
        You provide customer support via messaging.
        
        BUSINESS CONTEXT:
        - Business: {settings.BUSINESS_NAME}
        - Support Email: {settings.SUPPORT_EMAIL}
        - Business Hours: {settings.BUSINESS_HOURS_START} to {settings.BUSINESS_HOURS_END} ({settings.BUSINESS_TIMEZONE})
        
        CAPABILITIES:
        1. Answer FAQs about products/services
        2. Check order status (ask for order number)
        3. Help with bookings/appointments
        4. Collect leads (email/phone if customer interested)
        5. Handle after-hours queries
        
        RESPONSE GUIDELINES:
        - Be friendly, professional, concise
        - Ask clarifying questions if needed
        - For order status: Ask for order number
        - For bookings: Ask for preferred date/time
        - For leads: Ask for email/phone politely
        - If unsure: Offer to connect with human support
        - After hours: Mention business hours politely
        
        Current Language: Respond in {language}
        """
        
        if context:
            base_prompt += f"\n\nCONVERSATION CONTEXT:\n{context}"
        
        return base_prompt
    
    async def _openai_response(self, user_message: str, system_prompt: str) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        
        response = await openai.ChatCompletion.acreate(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=settings.AI_TEMPERATURE,
            max_tokens=500
        )
        
        return {
            "text": response.choices[0].message.content,
            "provider": "openai",
            "model": settings.OPENAI_MODEL,
            "tokens_used": response.usage.total_tokens
        }
    
    async def _gemini_response(self, user_message: str, system_prompt: str) -> Dict[str, Any]:
        """Generate response using Google Gemini"""
        
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        prompt = f"{system_prompt}\n\nUser Message: {user_message}"
        
        response = await model.generate_content_async(prompt)
        
        return {
            "text": response.text,
            "provider": "gemini",
            "model": settings.GEMINI_MODEL,
            "tokens_used": len(prompt) + len(response.text)
        }
    
    def _fallback_response(self, error: str) -> Dict[str, Any]:
        """Fallback response when AI fails"""
        
        return {
            "text": f"I apologize, but I'm having trouble processing your request. "
                   f"Please try again or contact {settings.SUPPORT_EMAIL} for assistance. "
                   f"[Error: {error}]",
            "provider": "fallback",
            "model": "none",
            "tokens_used": 0
        }
    
    def detect_language(self, text: str) -> str:
        """Simple language detection (can be enhanced later)"""
        
        # Simple keyword-based detection for Phase 1
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["hola", "gracias", "por favor"]):
            return "Spanish"
        elif any(word in text_lower for word in ["bonjour", "merci", "s'il vous plaît"]):
            return "French"
        elif any(word in text_lower for word in ["hallo", "danke", "bitte"]):
            return "German"
        else:
            return "English"

ai_client = AIClient()