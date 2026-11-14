from typing import Optional, List
from pydantic import BaseModel, Field

class AadhaarCardExtraction(BaseModel):
    document_type: str = Field(default="AADHAAR", description="Type of document, must be AADHAAR")
    aadhaar_number: str = Field(description="12-digit Aadhaar UID number or masked (e.g. 1234 5678 9012 or XXXX XXXX 9012)")
    full_name: str = Field(description="Full name printed on the Aadhaar card")
    gender: Optional[str] = Field(default=None, description="Gender (MALE / FEMALE / TRANSGENDER)")
    date_of_birth: Optional[str] = Field(default=None, description="Date of birth or Year of birth")
    address: Optional[str] = Field(default=None, description="Complete residential address printed on the card")
    pincode: Optional[str] = Field(default=None, description="6-digit postal pincode")
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0, description="Overall extraction confidence")
    anomalies: List[str] = Field(default_factory=list, description="Any detected visual anomalies or tampering signs")

