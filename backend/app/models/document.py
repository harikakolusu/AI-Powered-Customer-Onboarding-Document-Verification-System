import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    document_type = Column(String(50), nullable=False) # PAN, AADHAAR, BANK_STATEMENT, UNKNOWN
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True) # SHA-256
    
    # Quality metrics
    quality_score = Column(Float, default=100.0)
    is_clear = Column(Boolean, default=True)
    quality_notes = Column(String(255), nullable=True)

    # Extraction output
    raw_text = Column(Text, nullable=True)
    extracted_data = Column(JSON, nullable=True)
    extraction_confidence = Column(Float, default=1.0)

    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    application = relationship("Application", back_populates="documents")

