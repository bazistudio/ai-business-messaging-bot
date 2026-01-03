from fastapi import APIRouter, HTTPException
from typing import Dict, List

faq_router = APIRouter()

class FAQService:
    def __init__(self):
        self.faqs = {
            "What are your business hours?": f"We're open from 9 AM to 5 PM, Monday to Friday.",
            "How can I track my order?": "Use /order command and provide your order number.",
            "Do you offer refunds?": "Yes, we offer 30-day refunds for unused products.",
            "How long does shipping take?": "Shipping takes 3-5 business days domestically.",
            "Can I change my order?": "Order changes are possible within 24 hours of placement.",
            "Do you ship internationally?": "Yes, we ship to 50+ countries.",
            "What payment methods do you accept?": "We accept credit cards, PayPal, and bank transfers.",
            "How do I make a booking?": "Use /booking command or visit our website.",
            "Are there any discounts?": "We offer 10% off for first-time customers.",
            "How do I contact support?": f"Email us at support@example.com or message here."
        }
    
    def get_faqs(self) -> Dict[str, str]:
        return self.faqs
    
    def search_faqs(self, query: str) -> List[Dict[str, str]]:
        """Search FAQs by keyword"""
        query = query.lower()
        results = []
        
        for question, answer in self.faqs.items():
            if query in question.lower() or query in answer.lower():
                results.append({"question": question, "answer": answer})
        
        return results

@faq_router.get("/faqs")
async def get_all_faqs():
    """Get all FAQs"""
    service = FAQService()
    return {"faqs": service.get_faqs()}

@faq_router.get("/faqs/search")
async def search_faqs(query: str):
    """Search FAQs"""
    service = FAQService()
    results = service.search_faqs(query)
    return {"query": query, "results": results}