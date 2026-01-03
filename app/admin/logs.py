from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional
from datetime import datetime, timedelta
import csv
import json
from io import StringIO

from app.models.message import SessionLocal, ConversationLog, LeadCapture, MessageType

admin_router = APIRouter()

# Logging functions
def log_message(
    message_id: str,
    user_id: str,
    platform: str,
    message_type: MessageType,
    content: str,
    metadata: Optional[dict] = None
):
    """Log a message to database"""
    
    db = SessionLocal()
    try:
        log = ConversationLog(
            message_id=message_id,
            user_id=user_id,
            platform=platform,
            message_type=message_type,
            content=content,
            metadata=metadata or {}
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error logging message: {e}")
    finally:
        db.close()

def capture_lead(user_id: str, user_name: str, platform: str, interest: str):
    """Capture a lead"""
    
    db = SessionLocal()
    try:
        # Check if lead already exists
        existing = db.query(LeadCapture).filter(
            LeadCapture.user_id == user_id,
            LeadCapture.contacted == False
        ).first()
        
        if existing:
            return  # Lead already captured
        
        lead = LeadCapture(
            user_id=user_id,
            user_name=user_name,
            platform=platform,
            interest=interest,
            contact_info={}  # Will be filled when user provides contact
        )
        db.add(lead)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error capturing lead: {e}")
    finally:
        db.close()

# Admin endpoints
@admin_router.get("/logs")
async def get_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    user_id: Optional[str] = None,
    platform: Optional[str] = None,
    message_type: Optional[str] = None
):
    """Get conversation logs"""
    
    db = SessionLocal()
    try:
        query = db.query(ConversationLog)
        
        if user_id:
            query = query.filter(ConversationLog.user_id == user_id)
        if platform:
            query = query.filter(ConversationLog.platform == platform)
        if message_type:
            query = query.filter(ConversationLog.message_type == message_type)
        
        total = query.count()
        logs = query.order_by(ConversationLog.timestamp.desc()).offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "logs": [log.to_dict() for log in logs]
        }
    
    finally:
        db.close()

@admin_router.get("/logs/export")
async def export_logs(
    format: str = Query("json", regex="^(json|csv)$"),
    days: int = Query(7, ge=1, le=365)
):
    """Export logs in JSON or CSV format"""
    
    db = SessionLocal()
    try:
        since_date = datetime.utcnow() - timedelta(days=days)
        
        logs = db.query(ConversationLog).filter(
            ConversationLog.timestamp >= since_date
        ).order_by(ConversationLog.timestamp.desc()).all()
        
        if format == "json":
            return {
                "export_date": datetime.utcnow().isoformat(),
                "days": days,
                "total_logs": len(logs),
                "logs": [log.to_dict() for log in logs]
            }
        
        elif format == "csv":
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "ID", "Message ID", "User ID", "Platform", "Type", 
                "Content", "Timestamp", "AI Provider", "AI Model"
            ])
            
            # Write rows
            for log in logs:
                metadata = log.metadata or {}
                writer.writerow([
                    log.id,
                    log.message_id,
                    log.user_id,
                    log.platform,
                    log.message_type,
                    log.content.replace('\n', ' ').replace('\r', ' ')[:500],
                    log.timestamp.isoformat(),
                    metadata.get('ai_provider', ''),
                    metadata.get('ai_model', '')
                ])
            
            return {
                "filename": f"chat_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
                "content": output.getvalue(),
                "content_type": "text/csv"
            }
    
    finally:
        db.close()

@admin_router.get("/leads")
async def get_leads(contacted: Optional[bool] = None):
    """Get captured leads"""
    
    db = SessionLocal()
    try:
        query = db.query(LeadCapture)
        
        if contacted is not None:
            query = query.filter(LeadCapture.contacted == contacted)
        
        leads = query.order_by(LeadCapture.captured_at.desc()).all()
        
        return {
            "total": len(leads),
            "contacted": sum(1 for lead in leads if lead.contacted),
            "leads": [lead.to_dict() for lead in leads]
        }
    
    finally:
        db.close()

@admin_router.delete("/user/{user_id}")
async def delete_user_data(user_id: str):
    """GDPR-compliant user data deletion"""
    
    db = SessionLocal()
    try:
        # Delete conversation logs
        log_count = db.query(ConversationLog).filter(
            ConversationLog.user_id == user_id
        ).delete()
        
        # Delete leads
        lead_count = db.query(LeadCapture).filter(
            LeadCapture.user_id == user_id
        ).delete()
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Deleted {log_count} messages and {lead_count} leads for user {user_id}",
            "user_id": user_id,
            "deleted_at": datetime.utcnow().isoformat(),
            "compliance": "GDPR Article 17 - Right to erasure"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()

@admin_router.get("/stats")
async def get_stats(days: int = 7):
    """Get bot statistics"""
    
    db = SessionLocal()
    try:
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Message statistics
        total_messages = db.query(ConversationLog).filter(
            ConversationLog.timestamp >= since_date
        ).count()
        
        incoming = db.query(ConversationLog).filter(
            ConversationLog.timestamp >= since_date,
            ConversationLog.message_type == MessageType.INCOMING
        ).count()
        
        outgoing = db.query(ConversationLog).filter(
            ConversationLog.timestamp >= since_date,
            ConversationLog.message_type == MessageType.OUTGOING
        ).count()
        
        # Platform statistics
        platforms = db.query(
            ConversationLog.platform,
            db.func.count(ConversationLog.id)
        ).filter(
            ConversationLog.timestamp >= since_date
        ).group_by(ConversationLog.platform).all()
        
        # AI provider statistics
        ai_stats = db.query(
            db.func.json_extract(ConversationLog.metadata, '$.ai_provider').label('provider'),
            db.func.count(ConversationLog.id)
        ).filter(
            ConversationLog.timestamp >= since_date,
            ConversationLog.message_type == MessageType.OUTGOING
        ).group_by('provider').all()
        
        # Lead statistics
        total_leads = db.query(LeadCapture).filter(
            LeadCapture.captured_at >= since_date
        ).count()
        
        new_leads = db.query(LeadCapture).filter(
            LeadCapture.captured_at >= since_date,
            LeadCapture.contacted == False
        ).count()
        
        return {
            "period": f"last_{days}_days",
            "messages": {
                "total": total_messages,
                "incoming": incoming,
                "outgoing": outgoing,
                "response_rate": (outgoing / incoming * 100) if incoming > 0 else 0
            },
            "platforms": dict(platforms),
            "ai_providers": dict(ai_stats),
            "leads": {
                "total": total_leads,
                "new": new_leads,
                "contacted": total_leads - new_leads
            }
        }
    
    finally:
        db.close()