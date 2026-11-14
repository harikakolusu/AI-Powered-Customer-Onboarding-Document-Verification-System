import logging
from typing import Optional, List
from pathlib import Path
import sys

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.app.database import init_db, get_db
from backend.app.config import SAMPLE_DATA_DIR, STORAGE_DIR
from backend.app.models.customer import Application, Customer
from backend.app.models.document import Document
from backend.app.models.verification import VerificationResult
from backend.app.models.audit_log import AuditLog
from backend.app.services.routing_service import OnboardingOrchestrator
from backend.app.utils.synthetic_data import generate_all_scenario_documents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("backend.api")

app = FastAPI(
    title="Apex AI Customer Onboarding API",
    description="Backend verification engine, automated OCR/LLM pipelines, and audit logging API.",
    version="1.0.0",
)

@app.on_event("startup")
def on_startup():
    logger.info("Initializing database tables...")
    init_db()
    logger.info("Generating / verifying synthetic scenario documents...")
    generate_all_scenario_documents()
    logger.info("Backend REST API ready and listening for requests.")

@app.get("/")
def root():
    return {
        "service": "Apex Customer Onboarding Backend",
        "status": "online",
        "docs_url": "http://localhost:8000/docs",
        "health_check": "http://localhost:8000/health"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected",
        "db_path": str(STORAGE_DIR / "onboarding.db")
    }

@app.get("/api/stats")
def get_stats():
    """Retrieve operational KPIs for dashboard."""
    with get_db() as db:
        total = db.query(Application).count()
        approved = db.query(Application).filter(Application.status == "APPROVED").count()
        flagged = db.query(Application).filter(Application.status.like("FLAGGED%")).count()
        rejected = db.query(Application).filter(Application.status == "REJECTED").count()
        pending = db.query(Application).filter(Application.status == "PENDING_REVIEW").count()
        return {
            "total_applications": total,
            "approved": approved,
            "flagged": flagged,
            "rejected": rejected,
            "pending_review": pending
        }

@app.get("/api/applications")
def list_applications():
    """List all onboarding applications."""
    with get_db() as db:
        apps = db.query(Application).order_by(Application.created_at.desc()).all()
        results = []
        for app in apps:
            customer = db.query(Customer).filter(Customer.id == app.customer_id).first()
            results.append({
                "id": app.id,
                "customer_name": customer.full_name if customer else "Unknown",
                "email": customer.email if customer else "",
                "status": app.status,
                "risk_score": app.risk_score,
                "risk_level": app.risk_level,
                "confidence": app.confidence_score,
                "created_at": app.created_at.isoformat() if app.created_at else None
            })
        return results

@app.get("/api/applications/{app_id}")
def get_application(app_id: str):
    """Retrieve full detail for a single application."""
    with get_db() as db:
        app = db.query(Application).filter(Application.id == app_id).first()
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")
        customer = db.query(Customer).filter(Customer.id == app.customer_id).first()
        docs = db.query(Document).filter(Document.application_id == app.id).all()
        verif = db.query(VerificationResult).filter(VerificationResult.application_id == app.id).first()
        
        return {
            "id": app.id,
            "customer": {
                "name": customer.full_name if customer else "",
                "email": customer.email if customer else "",
                "phone": customer.phone if customer else ""
            },
            "status": app.status,
            "risk_score": app.risk_score,
            "risk_level": app.risk_level,
            "confidence_score": app.confidence_score,
            "reasons": app.reasons,
            "decision_note": app.decision_note,
            "documents_count": len(docs),
            "verification": verif.summary if verif else {}
        }

@app.post("/api/seed")
def seed_demo_scenarios():
    """Seed all 5 benchmark demo scenarios."""
    logger.info("Executing 5 benchmark scenario seeding run...")
    scenarios = [
        {"name": "Rahul Sharma",  "email": "rahul@example.com",  "phone": "9876543210", "folder": "scenario_1_valid"},
        {"name": "Priya Nair",    "email": "priya@example.com",  "phone": "9876543211", "folder": "scenario_2_unclear"},
        {"name": "Amit Patel",    "email": "amit@example.com",   "phone": "9876543212", "folder": "scenario_3_duplicate"},
        {"name": "Sneha Reddy",   "email": "sneha@example.com",  "phone": "9876543213", "folder": "scenario_4_inconsistency"},
        {"name": "Vikram Singh",  "email": "vikram@example.com", "phone": "9876543214", "folder": "scenario_5_missing_doc"},
    ]
    created = []
    with get_db() as db:
        for s in scenarios:
            doc_folder = SAMPLE_DATA_DIR / s["folder"]
            doc_paths = list(doc_folder.glob("*.png")) if doc_folder.exists() else []
            orchestrator = OnboardingOrchestrator(db)
            app = orchestrator.process_onboarding_application(
                customer_name=s["name"],
                email=s["email"],
                phone=s["phone"],
                uploaded_file_paths=doc_paths
            )
            logger.info(f"Seeded Scenario: {s['name']} -> {app.status} (Risk: {app.risk_score})")
            created.append({"name": s["name"], "app_id": app.id, "status": app.status})
            
    return {"message": "All 5 benchmark scenarios processed successfully", "created": created}

class DecisionRequest(BaseModel):
    application_id: str
    decision: str
    reviewer: str = "Compliance Officer"
    notes: Optional[str] = ""

@app.post("/api/decision")
def submit_decision(req: DecisionRequest):
    """Execute human-in-the-loop decision."""
    with get_db() as db:
        orchestrator = OnboardingOrchestrator(db)
        app = orchestrator.execute_human_decision(
            application_id=req.application_id,
            decision=req.decision,
            reviewer=req.reviewer,
            notes=req.notes or ""
        )
        logger.info(f"Human decision recorded for {app.id}: {req.decision} by {req.reviewer}")
        return {"status": "success", "application_id": app.id, "new_status": app.status}

@app.get("/api/audit-logs")
def get_audit_logs(limit: int = 25):
    """Fetch recent audit log entries."""
    with get_db() as db:
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
        return [
            {
                "id": l.id,
                "application_id": l.application_id,
                "action": l.action,
                "performed_by": l.performed_by,
                "timestamp": l.timestamp.isoformat() if l.timestamp else None,
                "details": l.details
            }
            for l in logs
        ]
