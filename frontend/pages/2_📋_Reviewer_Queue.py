import streamlit as st
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.database import get_db
from backend.app.models.customer import Application, Customer
from backend.app.models.document import Document
from backend.app.models.verification import VerificationResult
from backend.app.services.routing_service import OnboardingOrchestrator
from frontend.components.ui_helpers import render_status_badge, render_risk_badge, display_document_card

st.set_page_config(page_title="Reviewer Queue", page_icon="📋", layout="wide")

st.title("📋 Compliance Reviewer Queue (Human-in-the-Loop)")
st.markdown("Inspect AI-analyzed onboarding applications, review flagged exceptions, examine document scans, and execute regulatory approval actions.")

with get_db() as db:
    # Filter Controls
    c1, c2 = st.columns([1, 2])
    with c1:
        status_filter = st.selectbox(
            "Filter Queue by Status:",
            ["ALL PENDING", "READY_FOR_REVIEW", "FLAGGED_UNCLEAR", "FLAGGED_INCONSISTENCY", "FLAGGED_DUPLICATE", "MISSING_DOCUMENTS", "APPROVED", "REJECTED", "ALL"]
        )

    query = db.query(Application).join(Customer)
    if status_filter == "ALL PENDING":
        query = query.filter(Application.status.in_(["READY_FOR_REVIEW", "FLAGGED_UNCLEAR", "FLAGGED_INCONSISTENCY", "FLAGGED_DUPLICATE", "MISSING_DOCUMENTS"]))
    elif status_filter != "ALL":
        query = query.filter(Application.status == status_filter)

    applications = query.order_by(Application.created_at.desc()).all()

    if not applications:
        st.info("No applications currently found matching the selected filter.")
        st.stop()

    # Table Summary View
    st.markdown("### Applications in Queue")
    table_data = []
    for a in applications:
        table_data.append({
            "App ID": a.id[:8] + "...",
            "Customer Name": a.customer.full_name,
            "Status": a.status,
            "Risk Level": a.risk_level,
            "Risk Score": f"{a.risk_score:.0f}/100",
            "Documents Count": len(a.documents),
            "Submitted At": a.created_at.strftime("%Y-%m-%d %H:%M")
        })

    st.dataframe(table_data, use_container_width=True)

    st.divider()

    # Application Selector for In-Depth Review
    app_options = {f"{a.customer.full_name} ({a.status}) - ID: {a.id[:8]}": a.id for a in applications}
    selected_label = st.selectbox("Select Application to Inspect & Decide:", list(app_options.keys()))
    selected_app_id = app_options[selected_label]

    app = db.query(Application).filter(Application.id == selected_app_id).first()

    if app:
        st.markdown(f"## Application Details: `{app.customer.full_name}`")
        col_meta1, col_meta2, col_meta3, col_meta4 = st.columns(4)
        col_meta1.markdown(f"**Application ID:** `{app.id}`")
        col_meta2.markdown(f"**Status:** {render_status_badge(app.status)}", unsafe_allow_html=True)
        col_meta3.markdown(f"**Risk Profile:** {render_risk_badge(app.risk_level, app.risk_score)}", unsafe_allow_html=True)
        col_meta4.markdown(f"**AI Confidence:** `{app.overall_confidence * 100:.1f}%`")

        # Verification Warnings / Exceptions
        if app.verification_results:
            st.markdown("### ⚠️ AI Verification Findings & Reason Summary")
            for vr in app.verification_results:
                if vr.status == "FAILED":
                    st.error(f"**[{vr.check_type}] {vr.title}**\n\n{vr.ai_explanation}")
                elif vr.status == "WARNING":
                    st.warning(f"**[{vr.check_type}] {vr.title}**\n\n{vr.ai_explanation}")
                else:
                    st.success(f"**[{vr.check_type}] {vr.title}**\n\n{vr.ai_explanation}")

        # Submitted Documents
        st.markdown("### 📄 Submitted Document Scans & Extracted Entities")
        if not app.documents:
            st.warning("No documents attached to this application.")
        else:
            tabs = st.tabs([f"{d.document_type} ({d.original_filename})" for d in app.documents])
            for i, d in enumerate(app.documents):
                with tabs[i]:
                    display_document_card(d)

        st.divider()

        # Human-in-the-Loop Decision Form
        st.markdown("### ⚖️ Compliance Officer Decision Form")
        st.caption("Under regulatory commercial banking policy, every approval or exception resolution requires an authorized employee signature.")

        with st.form("decision_form"):
            c_rev, c_act = st.columns(2)
            with c_rev:
                reviewer_name = st.text_input("Reviewer Name / Employee ID *", value="Officer Anita")
            with c_act:
                decision_action = st.selectbox(
                    "Decision Action *",
                    ["APPROVE", "REJECT", "REQUEST_REUPLOAD"]
                )

            comments = st.text_area("Reviewer Rationale & Audit Comments", placeholder="e.g. Identity documents inspected and verified against PAN central database.")

            submit_decision = st.form_submit_button("Record Human Decision & Update State", type="primary", use_container_width=True)

        if submit_decision:
            if not reviewer_name.strip():
                st.error("Please enter your name or Employee ID for audit accountability.")
            else:
                orchestrator = OnboardingOrchestrator(db)
                updated_app = orchestrator.execute_human_decision(
                    application_id=app.id,
                    reviewer_name=reviewer_name,
                    decision=decision_action,
                    comments=comments
                )
                st.success(f"Decision recorded successfully! Application status updated to **{updated_app.status}**.")
                st.rerun()

