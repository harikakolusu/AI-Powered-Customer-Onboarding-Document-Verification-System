from typing import Optional, List
from pydantic import BaseModel, Field

class PanCardExtraction(BaseModel):
    document_type: str = Field(default="PAN", description="Type of document, must be PAN")
    pan_number: str = Field(description="10-character alphanumeric PAN number (e.g. ABCDE1234F)")
    full_name: str = Field(description="Full name printed on the PAN card")
    father_name: Optional[str] = Field(default=None, description="Father's name if present on PAN")
    date_of_birth: Optional[str] = Field(default=None, description="Date of birth in DD/MM/YYYY or YYYY-MM-DD format")
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0, description="Overall extraction confidence")
    anomalies: List[str] = Field(default_factory=list, description="Any detected visual anomalies or tampering signs")

