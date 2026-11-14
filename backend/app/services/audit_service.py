from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.models.audit_log import AuditLog

class AuditService:
    @staticmethod
    def record_event(
        db: Session,
        actor: str,
        action: str,
        application_id: Optional[str] = None,
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Creates an immutable, traceable audit record for regulatory compliance.
        """
        log_entry = AuditLog(
            application_id=application_id,
            actor=actor,
            action=action,
            previous_state=previous_state,
            new_state=new_state,
            reason=reason,
            metadata_json=metadata or {},
            timestamp=datetime.now(timezone.utc)
        )
        db.add(log_entry)
        db.flush()
        return log_entry

    @staticmethod
    def get_application_history(db: Session, application_id: str) -> List[AuditLog]:
        return db.query(AuditLog).filter(
            AuditLog.application_id == application_id
        ).order_by(AuditLog.timestamp.asc()).all()

    @staticmethod
    def get_all_logs(db: Session, limit: int = 200) -> List[AuditLog]:
        return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()

