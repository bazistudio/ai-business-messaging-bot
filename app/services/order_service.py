from fastapi import APIRouter, HTTPException
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import random

order_router = APIRouter()

class OrderService:
    def __init__(self):
        # Mock order database
        self.orders = {
            "ORD-1001": {
                "order_id": "ORD-1001",
                "customer_name": "John Doe",
                "product": "Premium Widget",
                "status": "shipped",
                "tracking_number": "TRK123456789",
                "estimated_delivery": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
                "order_date": "2024-01-15",
                "total": "$99.99"
            },
            "ORD-1002": {
                "order_id": "ORD-1002",
                "customer_name": "Jane Smith",
                "product": "Basic Widget",
                "status": "processing",
                "tracking_number": None,
                "estimated_delivery": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
                "order_date": "2024-01-16",
                "total": "$49.99"
            },
            "ORD-1003": {
                "order_id": "ORD-1003",
                "customer_name": "Bob Wilson",
                "product": "Deluxe Widget Bundle",
                "status": "delivered",
                "tracking_number": "TRK987654321",
                "estimated_delivery": "2024-01-10",
                "order_date": "2024-01-05",
                "total": "$199.99"
            }
        }
    
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """Get order status by ID"""
        order_id = order_id.upper().strip()
        
        if order_id in self.orders:
            return self.orders[order_id]
        
        # If not found, create mock response for demo
        statuses = ["processing", "shipped", "delivered", "pending"]
        products = ["Premium Widget", "Basic Widget", "Deluxe Bundle", "Starter Kit"]
        
        return {
            "order_id": order_id,
            "customer_name": "Demo Customer",
            "product": random.choice(products),
            "status": random.choice(statuses),
            "tracking_number": f"TRK{random.randint(100000000, 999999999)}" if random.choice([True, False]) else None,
            "estimated_delivery": (datetime.now() + timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d"),
            "order_date": (datetime.now() - timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d"),
            "total": f"${random.randint(20, 200)}.{random.randint(0, 99):02d}",
            "note": "This is a demo response. Connect to your real order system for live data."
        }
    
    def format_order_response(self, order_data: Dict) -> str:
        """Format order data for chat response"""
        
        response = f"""
📦 Order: {order_data['order_id']}
👤 Customer: {order_data['customer_name']}
🛍️ Product: {order_data['product']}
📊 Status: {order_data['status'].upper()}
💰 Total: {order_data['total']}
📅 Ordered: {order_data['order_date']}
        """
        
        if order_data.get('tracking_number'):
            response += f"\n📮 Tracking: {order_data['tracking_number']}"
        
        if order_data.get('estimated_delivery'):
            response += f"\n📅 Est. Delivery: {order_data['estimated_delivery']}"
        
        if order_data.get('note'):
            response += f"\n\n📝 Note: {order_data['note']}"
        
        return response

@order_router.get("/orders/{order_id}")
async def get_order(order_id: str):
    """API endpoint to get order status"""
    service = OrderService()
    order_data = service.get_order_status(order_id)
    
    if not order_data:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order_data

@order_router.post("/orders/lookup")
async def lookup_order(order_id: str):
    """Lookup order and return formatted response"""
    service = OrderService()
    order_data = service.get_order_status(order_id)
    return {
        "order_id": order_id,
        "status": "found" if order_data else "not_found",
        "data": order_data,
        "formatted_response": service.format_order_response(order_data) if order_data else "Order not found"
    }