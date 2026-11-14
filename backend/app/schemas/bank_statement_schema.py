from typing import Optional, List
from pydantic import BaseModel, Field

class BankStatementExtraction(BaseModel):
    document_type: str = Field(default="BANK_STATEMENT", description="Type of document, must be BANK_STATEMENT")
    account_holder_name: str = Field(description="Name of the bank account holder")
    account_number: str = Field(description="Bank account number")
    ifsc_code: Optional[str] = Field(default=None, description="11-character bank IFSC code")
    bank_name: Optional[str] = Field(default=None, description="Name of the financial institution/bank")
    statement_period: Optional[str] = Field(default=None, description="Period covered by the statement")
    confidence_score: float = Field(default=0.90, ge=0.0, le=1.0, description="Overall extraction confidence")
    anomalies: List[str] = Field(default_factory=list, description="Any detected anomalies or irregularities")

