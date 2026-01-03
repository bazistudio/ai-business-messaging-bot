from enum import Enum
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

Base = declarative_base()

class MessageType(str, Enum):
    INCOMING = "incoming"
    OUTGOING = "outgoing"
    SYSTEM = "system"

class ConversationLog(Base):
    __tablename__ = "conversation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    platform = Column(String)  # telegram, whatsapp
    message_type = Column(String)  # incoming, outgoing
    content = Column(Text)
    metadata = Column(JSON)  # AI provider, model, tokens, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "message_id": self.message_id,
            "user_id": self.user_id,
            "platform": self.platform,
            "message_type": self.message_type,
            "content": self.content[:200] + "..." if len(self.content) > 200 else self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }

class LeadCapture(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    user_name = Column(String)
    platform = Column(String)
    contact_info = Column(JSON)  # email, phone, etc.
    interest = Column(Text)
    captured_at = Column(DateTime, default=datetime.utcnow)
    contacted = Column(Boolean, default=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "platform": self.platform,
            "contact_info": self.contact_info,
            "interest": self.interest,
            "captured_at": self.captured_at.isoformat(),
            "contacted": self.contacted
        }

# Database setup
engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)