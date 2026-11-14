from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class ApplicationCreateRequest(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    document_type: str
    quality_score: float
    is_clear: bool
    status: str

class ReviewDecisionRequest(BaseModel):
    application_id: str
    action: str = Field(description="APPROVE, REJECT, or REQUEST_REUPLOAD")
    reviewer_name: str
    comments: Optional[str] = None
    missing_document_type: Optional[str] = None

class ApplicationSummary(BaseModel):
    application_id: str
    customer_name: str
    status: str
    risk_level: str
    risk_score: float
    overall_confidence: float
    created_at: str

