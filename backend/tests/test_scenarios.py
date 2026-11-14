import pytest
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.models.customer import Customer, Application
from backend.app.services.routing_service import OnboardingOrchestrator
from backend.app.config import SAMPLE_DATA_DIR
from backend.app.utils.synthetic_data import generate_all_scenario_documents

# Setup in-memory test database for isolated testing
TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session", autouse=True)
def setup_sample_docs():
    generate_all_scenario_documents()

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    yield session
    session.close()

def test_scenario_1_happy_path(db_session):
    """
    Scenario 1: Customer uploads valid PAN, Aadhaar and Bank Statement.
    System extracts details, verifies consistency, and moves application to READY_FOR_REVIEW.
    Reviewer then approves application -> status becomes APPROVED.
    """
    orchestrator = OnboardingOrchestrator(db_session)
    sc1_dir = SAMPLE_DATA_DIR / "scenario_1_valid"
    docs = [
        sc1_dir / "pan_card.png",
        sc1_dir / "aadhaar_card.png",
        sc1_dir / "bank_statement.png"
    ]

    app = orchestrator.process_onboarding_application(
        customer_name="Vikramaditya Sharma",
        email="vikram@example.com",
        phone="+91-9876543210",
        uploaded_file_paths=docs
    )

    assert app.status == "READY_FOR_REVIEW"
    assert app.risk_level == "LOW"
    assert app.customer.pan_number == "ABCPS1234D"

    # Human reviewer approves
    app_approved = orchestrator.execute_human_decision(
        application_id=app.id,
        reviewer_name="Officer Ramesh",
        decision="APPROVE",
        comments="Identity and address verified cleanly."
    )
    assert app_approved.status == "APPROVED"
    assert app_approved.reviewed_by == "Officer Ramesh"

def test_scenario_2_unclear_document(db_session):
    """
    Scenario 2: Customer uploads an unclear/blurry document.
    Quality evaluation flags Laplacian blur and routes application to FLAGGED_UNCLEAR.
    """
    orchestrator = OnboardingOrchestrator(db_session)
    sc2_dir = SAMPLE_DATA_DIR / "scenario_2_unclear"
    docs = [
        sc2_dir / "blurry_pan_card.png",
        sc2_dir / "aadhaar_card.png"
    ]

    app = orchestrator.process_onboarding_application(
        customer_name="Priya Nair",
        email="priya@example.com",
        phone="+91-9123456780",
        uploaded_file_paths=docs
    )

    assert app.status == "FLAGGED_UNCLEAR"
    assert app.risk_level == "HIGH"
    assert len(app.verification_results) > 0
    assert app.verification_results[0].check_type == "QUALITY"

def test_scenario_3_duplicate_application(db_session):
    """
    Scenario 3: Customer submits two applications with the same PAN number.
    System detects duplicate and sets status to FLAGGED_DUPLICATE.
    """
    orchestrator = OnboardingOrchestrator(db_session)
    sc1_dir = SAMPLE_DATA_DIR / "scenario_1_valid"
    sc3_dir = SAMPLE_DATA_DIR / "scenario_3_duplicate"

    # First application
    app1 = orchestrator.process_onboarding_application(
        customer_name="Vikramaditya Sharma",
        email="vikram@example.com",
        phone="+91-9876543210",
        uploaded_file_paths=[sc1_dir / "pan_card.png", sc1_dir / "aadhaar_card.png"]
    )
    assert app1.status == "READY_FOR_REVIEW"

    # Second application with exact same PAN
    app2 = orchestrator.process_onboarding_application(
        customer_name="Vikramaditya Sharma",
        email="vikram.alt@example.com",
        phone="+91-9876543210",
        uploaded_file_paths=[sc3_dir / "duplicate_pan_card.png", sc3_dir / "aadhaar_card.png"]
    )

    assert app2.status == "FLAGGED_DUPLICATE"
    assert app2.risk_level == "HIGH"
    assert "Duplicate application detected" in app2.verification_results[0].ai_explanation

def test_scenario_4_inconsistency_alert(db_session):
    """
    Scenario 4: Customer name differs between documents (PAN: Ananya Deshmukh vs Aadhaar: Pooja Sharma).
    AI cross-document consistency engine generates an inconsistency alert.
    """
    orchestrator = OnboardingOrchestrator(db_session)
    sc4_dir = SAMPLE_DATA_DIR / "scenario_4_inconsistency"
    docs = [
        sc4_dir / "pan_card.png",
        sc4_dir / "aadhaar_card.png"
    ]

    app = orchestrator.process_onboarding_application(
        customer_name="Ananya Deshmukh",
        email="ananya@example.com",
        phone="+91-9845012345",
        uploaded_file_paths=docs
    )

    assert app.status == "FLAGGED_INCONSISTENCY"
    assert app.risk_level == "HIGH"
    assert app.verification_results[0].check_type == "CROSS_MATCH"
    assert "Discrepancy" in app.verification_results[0].ai_explanation

def test_scenario_5_missing_document(db_session):
    """
    Scenario 5: Customer forgets to upload address proof (only uploads PAN).
    System detects missing mandatory document and requests missing document.
    """
    orchestrator = OnboardingOrchestrator(db_session)
    sc5_dir = SAMPLE_DATA_DIR / "scenario_5_missing_doc"
    docs = [
        sc5_dir / "pan_card.png"
        # Notice Aadhaar is missing!
    ]

    app = orchestrator.process_onboarding_application(
        customer_name="Rahul Verma",
        email="rahul@example.com",
        phone="+91-9765432109",
        uploaded_file_paths=docs
    )

    assert app.status == "MISSING_DOCUMENTS"
    assert app.risk_level == "HIGH"
    assert app.verification_results[0].check_type == "COMPLETENESS"
    assert "AADHAAR" in app.verification_results[0].details["missing"]

def test_pdf_document_intake(db_session, tmp_path):
    """
    Test that PDF documents are accepted and processed without errors.
    """
    from pypdf import PdfWriter

    pdf_path = tmp_path / "sample_pan.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with open(pdf_path, "wb") as f:
        writer.write(f)

    orchestrator = OnboardingOrchestrator(db_session)
    sc1_dir = SAMPLE_DATA_DIR / "scenario_1_valid"
    docs = [
        pdf_path,
        sc1_dir / "aadhaar_card.png"
    ]

    app = orchestrator.process_onboarding_application(
        customer_name="Test PDF User",
        email="pdf@example.com",
        phone="+91-9999999999",
        uploaded_file_paths=docs,
        doc_type_hints=["PAN", "AADHAAR"]
    )
    assert app is not None
    assert len(app.documents) == 2
    assert app.documents[0].document_type == "PAN"

