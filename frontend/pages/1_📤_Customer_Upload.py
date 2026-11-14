import streamlit as st
from pathlib import Path
import sys
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.database import get_db
from backend.app.config import UPLOADS_DIR, SAMPLE_DATA_DIR
from backend.app.services.routing_service import OnboardingOrchestrator
from frontend.components.ui_helpers import render_status_badge, render_risk_badge

st.set_page_config(page_title="Customer Document Upload", page_icon="📤", layout="wide")

st.title("📤 Customer Document Upload & AI Intake")
st.markdown("Submit customer KYC documents for automated quality verification, AI data extraction, and verification routing.")

tab1, tab2 = st.tabs(["📁 Custom Document Upload", "🧪 Run Pre-built Business Scenario"])

with tab1:
    with st.form("custom_upload_form", clear_on_submit=False):
        st.subheader("1. Customer Profile Information")
        c1, c2, c3 = st.columns(3)
        with c1:
            full_name = st.text_input("Full Legal Name *", placeholder="e.g. Vikramaditya Sharma")
        with c2:
            email = st.text_input("Email Address", placeholder="e.g. vikram@example.com")
        with c3:
            phone = st.text_input("Mobile Number", placeholder="e.g. +91 9876543210")

        st.subheader("2. Upload KYC Documents (PDF or Images)")
        col_pan, col_aadhaar, col_stmt = st.columns(3)
        with col_pan:
            pan_file = st.file_uploader("Identity Proof (PAN Card) *", type=["png", "jpg", "jpeg", "pdf"], key="pan_upload")
        with col_aadhaar:
            aadhaar_file = st.file_uploader("Address Proof (Aadhaar Card) *", type=["png", "jpg", "jpeg", "pdf"], key="aadhaar_upload")
        with col_stmt:
            stmt_file = st.file_uploader("Financial Proof (Bank Statement)", type=["png", "jpg", "jpeg", "pdf"], key="stmt_upload")

        submitted = st.form_submit_button("Submit Application for AI Verification", type="primary", use_container_width=True)

    if submitted:
        if not full_name.strip():
            st.error("Please provide the customer's legal name.")
        else:
            import time
            saved_paths = []
            hints = []
            UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
            ts = int(time.time())

            if pan_file:
                p_path = UPLOADS_DIR / f"pan_{ts}_{pan_file.name}"
                with open(p_path, "wb") as f:
                    f.write(pan_file.getbuffer())
                saved_paths.append(p_path)
                hints.append("PAN")

            if aadhaar_file:
                a_path = UPLOADS_DIR / f"aadhaar_{ts}_{aadhaar_file.name}"
                with open(a_path, "wb") as f:
                    f.write(aadhaar_file.getbuffer())
                saved_paths.append(a_path)
                hints.append("AADHAAR")

            if stmt_file:
                s_path = UPLOADS_DIR / f"stmt_{ts}_{stmt_file.name}"
                with open(s_path, "wb") as f:
                    f.write(stmt_file.getbuffer())
                saved_paths.append(s_path)
                hints.append("BANK_STATEMENT")

            if not saved_paths:
                st.warning("Please upload at least one KYC document.")
            else:
                with st.spinner("Processing documents with AI Quality & Extraction Engine..."):
                    with get_db() as db:
                        orchestrator = OnboardingOrchestrator(db)
                        app = orchestrator.process_onboarding_application(
                            customer_name=full_name,
                            email=email,
                            phone=phone,
                            uploaded_file_paths=saved_paths,
                            doc_type_hints=hints
                        )
                        st.success(f"Application created successfully! (ID: {app.id})")
                        st.markdown(f"**Assigned Status:** {render_status_badge(app.status)} &nbsp; **Risk:** {render_risk_badge(app.risk_level, app.risk_score)}", unsafe_allow_html=True)
                        if app.verification_results:
                            vr = app.verification_results[0]
                            st.info(f"**Engine Note:** {vr.ai_explanation}")

with tab2:
    st.subheader("⚡ Execute Specific Business Test Scenario")
    st.markdown("Quickly test any of the 5 problem statement scenarios using pre-generated synthetic documents:")

    sc_choice = st.selectbox(
        "Select Scenario to Test:",
        [
            "Scenario 1: Valid PAN + Aadhaar + Statement (Clean Pass)",
            "Scenario 2: Unclear / Blurry Document (Quality Exception)",
            "Scenario 3: Duplicate PAN Application (Duplicate Fraud Flag)",
            "Scenario 4: Name & DOB Inconsistency (AI Cross-Match Alert)",
            "Scenario 5: Missing Address Proof (Completeness Exception)"
        ]
    )

    if st.button("Run Selected Scenario", type="primary"):
        with st.spinner("Executing verification pipeline for selected scenario..."):
            with get_db() as db:
                orchestrator = OnboardingOrchestrator(db)
                if "Scenario 1" in sc_choice:
                    sc_dir = SAMPLE_DATA_DIR / "scenario_1_valid"
                    app = orchestrator.process_onboarding_application(
                        customer_name="Vikramaditya Sharma",
                        email="vikram@example.com",
                        phone="+91-9876543210",
                        uploaded_file_paths=[sc_dir / "pan_card.png", sc_dir / "aadhaar_card.png", sc_dir / "bank_statement.png"]
                    )
                elif "Scenario 2" in sc_choice:
                    sc_dir = SAMPLE_DATA_DIR / "scenario_2_unclear"
                    app = orchestrator.process_onboarding_application(
                        customer_name="Priya Nair",
                        email="priya@example.com",
                        phone="+91-9123456780",
                        uploaded_file_paths=[sc_dir / "blurry_pan_card.png", sc_dir / "aadhaar_card.png"]
                    )
                elif "Scenario 3" in sc_choice:
                    sc_dir = SAMPLE_DATA_DIR / "scenario_3_duplicate"
                    app = orchestrator.process_onboarding_application(
                        customer_name="Vikramaditya Sharma (Re-submission)",
                        email="vikram.dup@example.com",
                        phone="+91-9876543210",
                        uploaded_file_paths=[sc_dir / "duplicate_pan_card.png", sc_dir / "aadhaar_card.png"]
                    )
                elif "Scenario 4" in sc_choice:
                    sc_dir = SAMPLE_DATA_DIR / "scenario_4_inconsistency"
                    app = orchestrator.process_onboarding_application(
                        customer_name="Ananya Deshmukh",
                        email="ananya@example.com",
                        phone="+91-9845012345",
                        uploaded_file_paths=[sc_dir / "pan_card.png", sc_dir / "aadhaar_card.png"]
                    )
                else: # Scenario 5
                    sc_dir = SAMPLE_DATA_DIR / "scenario_5_missing_doc"
                    app = orchestrator.process_onboarding_application(
                        customer_name="Rahul Verma",
                        email="rahul@example.com",
                        phone="+91-9765432109",
                        uploaded_file_paths=[sc_dir / "pan_card.png"]
                    )

                st.success(f"Execution Completed! Application ID: {app.id}")
                st.markdown(f"**Current Status:** {render_status_badge(app.status)} &nbsp; **Risk:** {render_risk_badge(app.risk_level, app.risk_score)}", unsafe_allow_html=True)
                if app.verification_results:
                    vr = app.verification_results[0]
                    st.info(f"**Decision Summary:** {vr.ai_explanation}")

