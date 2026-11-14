import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=True, index=True)
    actor = Column(String(100), nullable=False) # SYSTEM_AI, SYSTEM_RULE, REVIEWER_<NAME>, CUSTOMER
    action = Column(String(100), nullable=False) # APPLICATION_CREATED, DOCUMENT_UPLOADED, QUALITY_CHECK, AI_EXTRACTION, DUPLICATE_CHECK, INCONSISTENCY_CHECK, HUMAN_APPROVED, HUMAN_REJECTED, RE_UPLOAD_REQUESTED
    previous_state = Column(String(50), nullable=True)
    new_state = Column(String(50), nullable=True)
    reason = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)

    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    application = relationship("Application", back_populates="audit_logs")

