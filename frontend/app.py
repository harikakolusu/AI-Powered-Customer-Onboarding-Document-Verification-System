import streamlit as st
from pathlib import Path
import sys
from dotenv import load_dotenv

# Ensure backend package is on Python sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Load frontend-specific .env
_FRONTEND_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=_FRONTEND_DIR / ".env")

from backend.app.database import init_db, get_db
from backend.app.config import SAMPLE_DATA_DIR
from backend.app.utils.synthetic_data import generate_all_scenario_documents
from backend.app.services.routing_service import OnboardingOrchestrator
from backend.app.models.customer import Application, Customer
from frontend.components.ui_helpers import render_status_badge, render_risk_badge

# Page Config
st.set_page_config(
    page_title="Apex AI KYC & Onboarding",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database
init_db()

# Load Custom CSS
css_file = BASE_DIR / "frontend" / "assets" / "style.css"
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Main Banner
st.title("🏦 Apex Commercial Banking")
st.subheader("AI-Powered Customer Onboarding & KYC Document Verification System")
st.markdown("""
Welcome to the intelligent onboarding control center. This platform automates document intake, quality screening, 
multimodal LLM data extraction, duplicate fraud prevention, and cross-document discrepancy detection while enforcing 
**Human-in-the-Loop** approval workflows.
""")

st.divider()

# Quick Overview Columns
col1, col2, col3, col4 = st.columns(4)

with get_db() as db:
    total_apps = db.query(Application).count()
    pending_review = db.query(Application).filter(Application.status.in_(["READY_FOR_REVIEW", "FLAGGED_UNCLEAR", "FLAGGED_DUPLICATE", "FLAGGED_INCONSISTENCY"])).count()
    approved = db.query(Application).filter(Application.status == "APPROVED").count()
    exceptions = db.query(Application).filter(Application.status.like("FLAGGED%")).count()

col1.metric("Total Applications", total_apps)
col2.metric("Pending Human Review", pending_review)
col3.metric("Approved Onboardings", approved)
col4.metric("Flagged Exceptions", exceptions)

st.divider()

# Scenario Demo Seeder
st.markdown("### 🚀 Interactive Scenario Test Bench")
st.markdown("""
Pre-load synthetic documents to demonstrate all 5 core business requirements instantly:
- **Scenario 1**: Valid PAN + Aadhaar + Bank Statement $\\rightarrow$ Extracted & moved to review.
- **Scenario 2**: Blurry / Unclear document $\\rightarrow$ Laplacian variance flags quality exception.
- **Scenario 3**: Duplicate PAN submission $\\rightarrow$ System flags duplicate fraud risk.
- **Scenario 4**: Name & DOB mismatch between documents $\\rightarrow$ AI cross-document inconsistency alert.
- **Scenario 5**: Missing address proof $\\rightarrow$ System detects incomplete bundle and requests missing document.
""")

if st.button("⚡ Seed All 5 Demo Scenarios into Database", type="primary", use_container_width=True):
    with st.spinner("Generating synthetic documents and executing AI verification pipeline..."):
        generate_all_scenario_documents()
        with get_db() as db:
            orchestrator = OnboardingOrchestrator(db)
            
            # Scenario 1
            sc1_dir = SAMPLE_DATA_DIR / "scenario_1_valid"
            orchestrator.process_onboarding_application(
                customer_name="Vikramaditya Sharma",
                email="vikram@example.com",
                phone="+91-9876543210",
                uploaded_file_paths=[sc1_dir / "pan_card.png", sc1_dir / "aadhaar_card.png", sc1_dir / "bank_statement.png"]
            )
            
            # Scenario 2
            sc2_dir = SAMPLE_DATA_DIR / "scenario_2_unclear"
            orchestrator.process_onboarding_application(
                customer_name="Priya Nair",
                email="priya@example.com",
                phone="+91-9123456780",
                uploaded_file_paths=[sc2_dir / "blurry_pan_card.png", sc2_dir / "aadhaar_card.png"]
            )
            
            # Scenario 3 (Duplicate PAN of Vikramaditya)
            sc3_dir = SAMPLE_DATA_DIR / "scenario_3_duplicate"
            orchestrator.process_onboarding_application(
                customer_name="Vikramaditya Sharma (Re-apply)",
                email="vikram.duplicate@example.com",
                phone="+91-9876543210",
                uploaded_file_paths=[sc3_dir / "duplicate_pan_card.png", sc3_dir / "aadhaar_card.png"]
            )

            # Scenario 4 (Name Mismatch)
            sc4_dir = SAMPLE_DATA_DIR / "scenario_4_inconsistency"
            orchestrator.process_onboarding_application(
                customer_name="Ananya Deshmukh",
                email="ananya@example.com",
                phone="+91-9845012345",
                uploaded_file_paths=[sc4_dir / "pan_card.png", sc4_dir / "aadhaar_card.png"]
            )

            # Scenario 5 (Missing Document)
            sc5_dir = SAMPLE_DATA_DIR / "scenario_5_missing_doc"
            orchestrator.process_onboarding_application(
                customer_name="Rahul Verma",
                email="rahul@example.com",
                phone="+91-9765432109",
                uploaded_file_paths=[sc5_dir / "pan_card.png"]
            )

        st.success("Successfully processed all 5 business scenarios! Use the sidebar navigation to inspect the Review Queue, Analytics Dashboard, and Audit Log.")
        st.rerun()

st.divider()

# System Modules Guide
st.markdown("### 🧭 System Navigation")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("#### 1. 📤 Upload Portal")
    st.caption("Upload new customer documents or trigger single scenario simulations.")
with c2:
    st.markdown("#### 2. 📋 Reviewer Queue")
    st.caption("Side-by-side inspection, AI discrepancy analyzer, and Human approval actions.")
with c3:
    st.markdown("#### 3. 📊 Dashboard")
    st.caption("Managerial KPIs, SLA times, Straight-Through-Processing rate & Plotly charts.")
with c4:
    st.markdown("#### 4. 📜 Audit Trail")
    st.caption("Chronological immutable event ledger for full regulatory traceability.")

