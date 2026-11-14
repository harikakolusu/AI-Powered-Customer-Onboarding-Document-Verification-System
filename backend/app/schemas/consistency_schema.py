from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class FieldMatchResult(BaseModel):
    field_name: str
    match_status: Literal["MATCH", "PARTIAL_MATCH", "MISMATCH", "NOT_AVAILABLE"]
    confidence: float = 1.0
    details: str

class CrossDocumentConsistencyResult(BaseModel):
    overall_match: Literal["MATCH", "PARTIAL_MATCH", "MISMATCH"]
    name_match: bool = Field(description="True if customer names across documents represent the same person")
    name_similarity_score: float = Field(ge=0.0, le=1.0, description="Normalized similarity score 0 to 1")
    dob_match: Optional[bool] = Field(default=None, description="True if dates of birth align")
    address_match: Optional[bool] = Field(default=None, description="True if residential address aligns or is compatible")
    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = Field(description="Assessed risk level")
    discrepancies: List[str] = Field(default_factory=list, description="List of specific discrepancies found")
    ai_reasoning: str = Field(description="Detailed narrative explaining the consistency evaluation and decision logic")
    suggested_action: Literal["APPROVE", "MANUAL_REVIEW", "REJECT", "REQUEST_DOCUMENT"]

