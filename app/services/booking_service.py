from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

booking_router = APIRouter()

class BookingService:
    def __init__(self):
        self.available_slots = self._generate_slots()
        self.bookings = {}
    
    def _generate_slots(self) -> List[Dict]:
        """Generate mock available time slots"""
        slots = []
        base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        for day in range(7):  # Next 7 days
            date = base_date + timedelta(days=day)
            
            for hour in range(9, 17):  # 9 AM to 5 PM
                if hour == 12:  # Skip lunch hour
                    continue
                
                slot_time = date.replace(hour=hour)
                slots.append({
                    "slot_id": f"SLOT-{len(slots)+1:04d}",
                    "date": slot_time.strftime("%Y-%m-%d"),
                    "time": slot_time.strftime("%H:%M"),
                    "available": True,
                    "duration": "60 minutes"
                })
        
        return slots
    
    def get_available_slots(self, date: Optional[str] = None) -> List[Dict]:
        """Get available booking slots"""
        if date:
            return [slot for slot in self.available_slots 
                   if slot["date"] == date and slot["available"]]
        else:
            return [slot for slot in self.available_slots if slot["available"]]
    
    def book_slot(self, slot_id: str, customer_info: Dict) -> Dict:
        """Book a time slot"""
        
        # Find the slot
        slot = next((s for s in self.available_slots if s["slot_id"] == slot_id), None)
        
        if not slot:
            return {"success": False, "error": "Slot not found"}
        
        if not slot["available"]:
            return {"success": False, "error": "Slot already booked"}
        
        # Mark as booked
        slot["available"] = False
        
        # Create booking record
        booking_id = f"BOOK-{len(self.bookings)+1:04d}"
        self.bookings[booking_id] = {
            "booking_id": booking_id,
            "slot_id": slot_id,
            "date": slot["date"],
            "time": slot["time"],
            "customer_name": customer_info.get("name", "Customer"),
            "customer_email": customer_info.get("email", ""),
            "customer_phone": customer_info.get("phone", ""),
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "booking_id": booking_id,
            "details": self.bookings[booking_id],
            "confirmation_message": self._format_confirmation(self.bookings[booking_id])
        }
    
    def _format_confirmation(self, booking: Dict) -> str:
        """Format booking confirmation message"""
        return f"""
✅ Booking Confirmed!
📋 ID: {booking['booking_id']}
📅 Date: {booking['date']}
⏰ Time: {booking['time']}
👤 Name: {booking['customer_name']}
📧 Email: {booking['customer_email']}
📞 Phone: {booking['customer_phone']}
📊 Status: {booking['status'].upper()}

A confirmation email has been sent (mock).
Please arrive 10 minutes early.
        """
    
    def cancel_booking(self, booking_id: str) -> Dict:
        """Cancel a booking"""
        if booking_id not in self.bookings:
            return {"success": False, "error": "Booking not found"}
        
        booking = self.bookings[booking_id]
        
        # Free up the slot
        slot = next((s for s in self.available_slots if s["slot_id"] == booking["slot_id"]), None)
        if slot:
            slot["available"] = True
        
        # Update booking status
        booking["status"] = "cancelled"
        
        return {
            "success": True,
            "message": f"Booking {booking_id} cancelled successfully"
        }

@booking_router.get("/booking/slots")
async def get_slots(date: Optional[str] = None):
    """Get available booking slots"""
    service = BookingService()
    slots = service.get_available_slots(date)
    return {"date": date, "available_slots": slots}

@booking_router.post("/booking/book")
async def book_appointment(slot_id: str, name: str, email: str, phone: Optional[str] = ""):
    """Book an appointment"""
    service = BookingService()
    customer_info = {"name": name, "email": email, "phone": phone}
    result = service.book_slot(slot_id, customer_info)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@booking_router.post("/booking/cancel/{booking_id}")
async def cancel_appointment(booking_id: str):
    """Cancel a booking"""
    service = BookingService()
    result = service.cancel_booking(booking_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result