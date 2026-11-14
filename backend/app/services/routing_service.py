import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.app.models.customer import Customer, Application
from backend.app.models.document import Document
from backend.app.models.verification import VerificationResult
from backend.app.services.quality_service import QualityService
from backend.app.services.llm_service import LLMService
from backend.app.services.validation_service import ValidationService
from backend.app.services.duplicate_service import DuplicateService
from backend.app.services.audit_service import AuditService

class OnboardingOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService()

    def process_onboarding_application(
        self,
        customer_name: str,
        email: Optional[str],
        phone: Optional[str],
        uploaded_file_paths: List[str | Path],
        doc_type_hints: Optional[List[str]] = None
    ) -> Application:
        """
        End-to-end automated processing pipeline for customer onboarding applications.
        Coordinates quality checks, LLM extraction, validation, duplicate detection,
        cross-document consistency, exception routing, and audit logging.
        """
        # 1. Initialize or find customer & create Application record
        customer = Customer(
            full_name=customer_name,
            email=email,
            phone=phone
        )
        self.db.add(customer)
        self.db.flush()

        app = Application(
            customer_id=customer.id,
            status="SUBMITTED",
            risk_level="LOW",
            risk_score=0.0,
            overall_confidence=1.0
        )
        self.db.add(app)
        self.db.flush()

        AuditService.record_event(
            db=self.db,
            actor="CUSTOMER",
            action="APPLICATION_CREATED",
            application_id=app.id,
            new_state="SUBMITTED",
            reason=f"Customer '{customer_name}' initiated onboarding application.",
            metadata={"file_count": len(uploaded_file_paths)}
        )

        extracted_docs_data = []
        submitted_doc_types = []
        has_blurry_doc = False
        lowest_confidence = 1.0
        risk_penalties = 0.0

        # 2. Process each uploaded document
        for idx, file_path in enumerate(uploaded_file_paths):
            path = Path(file_path)
            hint = doc_type_hints[idx] if doc_type_hints and idx < len(doc_type_hints) else None

            # Calculate SHA-256 hash
            hasher = hashlib.sha256()
            with open(path, "rb") as f:
                hasher.update(f.read())
            file_hash = hasher.hexdigest()

            # 2a. Quality Assessment
            quality_info = QualityService.evaluate_image_quality(path)
            if not quality_info["is_clear"]:
                has_blurry_doc = True
                risk_penalties += 35.0

            # 2b. AI / OCR Extraction
            extracted = self.llm_service.extract_document(path, doc_type_hint=hint)
            doc_type = extracted.get("document_type", hint or "UNKNOWN").upper()
            submitted_doc_types.append(doc_type)

            conf = extracted.get("confidence_score", 0.90)
            lowest_confidence = min(lowest_confidence, conf)

            # Create Document entity
            doc_record = Document(
                application_id=app.id,
                document_type=doc_type,
                original_filename=path.name,
                file_path=str(path),
                file_hash=file_hash,
                quality_score=quality_info["quality_score"],
                is_clear=quality_info["is_clear"],
                quality_notes=quality_info["quality_notes"],
                raw_text=str(extracted),
                extracted_data=extracted,
                extraction_confidence=conf
            )
            self.db.add(doc_record)
            extracted_docs_data.append(extracted)

            # Update customer identifiers if extracted
            if doc_type == "PAN" and "pan_number" in extracted:
                customer.pan_number = extracted["pan_number"].strip().upper()
            elif doc_type == "AADHAAR" and "aadhaar_number" in extracted:
                customer.aadhaar_number = "".join(filter(str.isdigit, extracted["aadhaar_number"]))

        self.db.flush()

        # 3. Check Completeness (Scenario 5: Missing Document)
        is_complete, missing_docs = ValidationService.verify_document_completeness(submitted_doc_types)
        if not is_complete:
            app.status = "MISSING_DOCUMENTS"
            app.risk_level = "HIGH"
            app.risk_score = 75.0
            v_res = VerificationResult(
                application_id=app.id,
                check_type="COMPLETENESS",
                status="FAILED",
                title="Missing Mandatory Documents",
                details={"missing": missing_docs, "submitted": submitted_doc_types},
                ai_explanation=f"Application lacks required KYC documents: {', '.join(missing_docs)}. Please request re-upload."
            )
            self.db.add(v_res)
            AuditService.record_event(
                db=self.db,
                actor="SYSTEM_RULE",
                action="MISSING_DOCUMENTS_DETECTED",
                application_id=app.id,
                previous_state="SUBMITTED",
                new_state="MISSING_DOCUMENTS",
                reason=f"Applicant omitted required document: {', '.join(missing_docs)}"
            )
            self.db.commit()
            return app

        # 4. Check Document Quality (Scenario 2: Unclear Document)
        if has_blurry_doc:
            app.status = "FLAGGED_UNCLEAR"
            app.risk_level = "HIGH"
            app.risk_score = min(100.0, risk_penalties + 40.0)
            app.overall_confidence = lowest_confidence
            v_res = VerificationResult(
                application_id=app.id,
                check_type="QUALITY",
                status="FAILED",
                title="Document Quality Degradation / Blur Detected",
                details={"quality_issue": True},
                ai_explanation="One or more uploaded documents failed the sharpness threshold (Laplacian variance < 100). Routed to manual verification."
            )
            self.db.add(v_res)
            AuditService.record_event(
                db=self.db,
                actor="SYSTEM_AI",
                action="QUALITY_EXCEPTION_RAISED",
                application_id=app.id,
                previous_state="SUBMITTED",
                new_state="FLAGGED_UNCLEAR",
                reason="Unreadable or low-clarity document detected."
            )
            self.db.commit()
            return app

        # 5. Check Duplicate Applications (Scenario 3: Duplicate PAN/Aadhaar)
        is_duplicate, dup_info = DuplicateService.check_duplicate_application(
            db=self.db,
            pan_number=customer.pan_number,
            aadhaar_number=customer.aadhaar_number,
            current_application_id=app.id
        )
        if is_duplicate:
            app.status = "FLAGGED_DUPLICATE"
            app.risk_level = "HIGH"
            app.risk_score = 95.0
            v_res = VerificationResult(
                application_id=app.id,
                check_type="DUPLICATE",
                status="FAILED",
                title="Duplicate Application Detected",
                details=dup_info,
                ai_explanation=dup_info["message"]
            )
            self.db.add(v_res)
            AuditService.record_event(
                db=self.db,
                actor="SYSTEM_RULE",
                action="DUPLICATE_APPLICATION_FLAGGED",
                application_id=app.id,
                previous_state="SUBMITTED",
                new_state="FLAGGED_DUPLICATE",
                reason=dup_info["message"],
                metadata=dup_info
            )
            self.db.commit()
            return app

        # 6. Check Cross-Document Inconsistencies via AI (Scenario 4: Name/DOB Mismatch)
        consistency_result = self.llm_service.analyze_cross_document_consistency(extracted_docs_data)
        if not consistency_result.name_match or consistency_result.risk_level == "HIGH":
            app.status = "FLAGGED_INCONSISTENCY"
            app.risk_level = "HIGH"
            app.risk_score = 80.0
            app.overall_confidence = consistency_result.name_similarity_score
            v_res = VerificationResult(
                application_id=app.id,
                check_type="CROSS_MATCH",
                status="FAILED",
                title="Cross-Document Identity Inconsistency",
                details={
                    "discrepancies": consistency_result.discrepancies,
                    "similarity_score": consistency_result.name_similarity_score
                },
                ai_explanation=consistency_result.ai_reasoning
            )
            self.db.add(v_res)
            AuditService.record_event(
                db=self.db,
                actor="SYSTEM_AI",
                action="INCONSISTENCY_FLAGGED",
                application_id=app.id,
                previous_state="SUBMITTED",
                new_state="FLAGGED_INCONSISTENCY",
                reason=consistency_result.ai_reasoning,
                metadata={"discrepancies": consistency_result.discrepancies}
            )
            self.db.commit()
            return app

        # 7. Scenario 1: Clean & Valid Documents -> Move to Review Queue
        app.status = "READY_FOR_REVIEW"
        app.risk_level = "LOW"
        app.risk_score = 5.0
        app.overall_confidence = lowest_confidence

        v_res = VerificationResult(
            application_id=app.id,
            check_type="CROSS_MATCH",
            status="PASSED",
            title="All Verification Checks Passed",
            details={"discrepancies": []},
            ai_explanation="All identity details match across submitted documents. Document formats and clarity validated successfully."
        )
        self.db.add(v_res)
        AuditService.record_event(
            db=self.db,
            actor="SYSTEM_AI",
            action="VERIFICATION_PASSED",
            application_id=app.id,
            previous_state="SUBMITTED",
            new_state="READY_FOR_REVIEW",
            reason="All automated AI and rule validations passed successfully. Ready for human approval."
        )
        self.db.commit()
        return app

    def execute_human_decision(
        self,
        application_id: str,
        reviewer_name: str,
        decision: str, # "APPROVE", "REJECT", "REQUEST_REUPLOAD"
        comments: Optional[str] = None
    ) -> Application:
        """
        Executes authorized human review decision in compliance with human-in-the-loop mandate.
        """
        app = self.db.query(Application).filter(Application.id == application_id).first()
        if not app:
            raise ValueError(f"Application {application_id} not found.")

        old_state = app.status
        if decision == "APPROVE":
            app.status = "APPROVED"
            action_name = "HUMAN_APPROVED"
        elif decision == "REJECT":
            app.status = "REJECTED"
            action_name = "HUMAN_REJECTED"
        elif decision == "REQUEST_REUPLOAD":
            app.status = "MISSING_DOCUMENTS"
            action_name = "RE_UPLOAD_REQUESTED"
        else:
            raise ValueError(f"Unknown decision: {decision}")

        app.reviewed_by = reviewer_name
        app.reviewer_comments = comments
        app.reviewed_at = datetime.now(timezone.utc)

        AuditService.record_event(
            db=self.db,
            actor=f"REVIEWER_{reviewer_name.upper().replace(' ', '_')}",
            action=action_name,
            application_id=app.id,
            previous_state=old_state,
            new_state=app.status,
            reason=comments or f"Human decision: {decision}",
            metadata={"reviewer": reviewer_name, "decision": decision}
        )

        self.db.commit()
        return app

