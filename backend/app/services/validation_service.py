import re
from typing import Dict, Any, List, Tuple
from backend.app.config import MANDATORY_DOCUMENTS

# Verhoeff algorithm multiplication and permutation tables for Aadhaar checksum verification
VERHOEFF_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
]

VERHOEFF_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
]

class ValidationService:
    @staticmethod
    def validate_pan(pan_number: str) -> Tuple[bool, str]:
        if not pan_number:
            return False, "PAN number is missing."
        clean_pan = pan_number.strip().upper()
        pan_regex = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
        if not re.match(pan_regex, clean_pan):
            return False, f"Invalid PAN format '{clean_pan}'. Must be 5 letters, 4 digits, 1 letter."
        return True, "Valid PAN structure."

    @staticmethod
    def validate_aadhaar(aadhaar_number: str) -> Tuple[bool, str]:
        if not aadhaar_number:
            return False, "Aadhaar number is missing."
        digits = re.sub(r"\D", "", aadhaar_number)
        if len(digits) != 12:
            return False, f"Aadhaar number must contain exactly 12 digits (found {len(digits)})."
        return True, "Valid Aadhaar structure."

    @staticmethod
    def validate_ifsc(ifsc: str) -> Tuple[bool, str]:
        if not ifsc:
            return False, "IFSC code is missing."
        clean_ifsc = ifsc.strip().upper()
        ifsc_regex = r"^[A-Z]{4}0[A-Z0-9]{6}$"
        if not re.match(ifsc_regex, clean_ifsc):
            return False, f"Invalid IFSC code format '{clean_ifsc}'."
        return True, "Valid IFSC code."

    @staticmethod
    def verify_document_completeness(submitted_doc_types: List[str]) -> Tuple[bool, List[str]]:
        """
        Checks whether all mandatory KYC documents (e.g. Identity Proof + Address Proof)
        are present.
        """
        types_upper = [t.upper() for t in submitted_doc_types]
        missing = [doc for doc in MANDATORY_DOCUMENTS if doc not in types_upper]
        if missing:
            return False, missing
        return True, []

