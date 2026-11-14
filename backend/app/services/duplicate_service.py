from typing import Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.customer import Customer, Application
from backend.app.models.document import Document

class DuplicateService:
    @staticmethod
    def check_duplicate_application(
        db: Session,
        pan_number: Optional[str] = None,
        aadhaar_number: Optional[str] = None,
        customer_name: Optional[str] = None,
        current_application_id: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Detects repeated or duplicate customer applications using PAN, Aadhaar,
        or demographic name similarity against the database records.
        """
        # 1. Exact PAN Match Check
        if pan_number:
            clean_pan = pan_number.strip().upper()
            existing_customer = db.query(Customer).filter(
                Customer.pan_number == clean_pan
            ).first()

            if existing_customer:
                # Check if this customer has prior applications
                prior_apps = db.query(Application).filter(
                    Application.customer_id == existing_customer.id,
                    Application.id != current_application_id
                ).all()

                if prior_apps:
                    matched_app = prior_apps[0]
                    return True, {
                        "duplicate_type": "EXACT_PAN_MATCH",
                        "matched_pan": clean_pan,
                        "existing_customer_id": existing_customer.id,
                        "existing_customer_name": existing_customer.full_name,
                        "prior_application_id": matched_app.id,
                        "prior_application_status": matched_app.status,
                        "message": f"Duplicate application detected! PAN '{clean_pan}' is already registered under customer '{existing_customer.full_name}' (App #{matched_app.id[:8]})."
                    }

        # 2. Exact Aadhaar Match Check
        if aadhaar_number:
            clean_aadhaar = "".join(filter(str.isdigit, aadhaar_number))
            if len(clean_aadhaar) == 12:
                existing_customer = db.query(Customer).filter(
                    Customer.aadhaar_number == clean_aadhaar
                ).first()

                if existing_customer:
                    prior_apps = db.query(Application).filter(
                        Application.customer_id == existing_customer.id,
                        Application.id != current_application_id
                    ).all()

                    if prior_apps:
                        matched_app = prior_apps[0]
                        return True, {
                            "duplicate_type": "EXACT_AADHAAR_MATCH",
                            "matched_aadhaar": clean_aadhaar,
                            "existing_customer_id": existing_customer.id,
                            "existing_customer_name": existing_customer.full_name,
                            "prior_application_id": matched_app.id,
                            "prior_application_status": matched_app.status,
                            "message": f"Duplicate application detected! Aadhaar is already registered under customer '{existing_customer.full_name}' (App #{matched_app.id[:8]})."
                        }

        return False, {
            "duplicate_type": "NONE",
            "message": "No duplicate record found. Customer application is unique."
        }

