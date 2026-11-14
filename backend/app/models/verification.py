import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class VerificationResult(Base):
    __tablename__ = "verification_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    check_type = Column(String(50), nullable=False) # QUALITY, FORMAT, DUPLICATE, CROSS_MATCH, COMPLETENESS
    status = Column(String(20), nullable=False)     # PASSED, FAILED, WARNING
    title = Column(String(255), nullable=False)
    details = Column(JSON, nullable=True)
    ai_explanation = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    application = relationship("Application", back_populates="verification_results")

