import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    pan_number = Column(String(20), nullable=True, index=True)
    aadhaar_number = Column(String(20), nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    applications = relationship("Application", back_populates="customer", cascade="all, delete-orphan")

class Application(Base):
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    status = Column(
        String(50),
        default="SUBMITTED",
        index=True
    )  # SUBMITTED, READY_FOR_REVIEW, APPROVED, REJECTED, FLAGGED_UNCLEAR, FLAGGED_DUPLICATE, FLAGGED_INCONSISTENCY, MISSING_DOCUMENTS
    risk_level = Column(String(20), default="LOW")  # LOW, MEDIUM, HIGH
    risk_score = Column(Float, default=0.0)         # 0.0 to 100.0
    overall_confidence = Column(Float, default=1.0) # 0.0 to 1.0
    reviewer_comments = Column(Text, nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    customer = relationship("Customer", back_populates="applications")
    documents = relationship("Document", back_populates="application", cascade="all, delete-orphan")
    verification_results = relationship("VerificationResult", back_populates="application", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="application", cascade="all, delete-orphan")

