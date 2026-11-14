import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.database import get_db
from backend.app.models.customer import Application, Customer
from backend.app.models.document import Document
from backend.app.models.verification import VerificationResult

st.set_page_config(page_title="Executive Dashboard", page_icon="📊", layout="wide")

st.title("📊 Executive Onboarding Analytics & SLA Dashboard")
st.markdown("Real-time operational monitoring of onboarding throughput, STP automation rates, exception volumes, and risk profiles.")

with get_db() as db:
    apps = db.query(Application).all()
    docs = db.query(Document).all()
    v_results = db.query(VerificationResult).all()

    if not apps:
        st.info("No application data available yet. Please submit an application or use the Seed button on the Home page.")
        st.stop()

    # Convert to Pandas DataFrames
    app_records = []
    for a in apps:
        app_records.append({
            "id": a.id,
            "status": a.status,
            "risk_level": a.risk_level,
            "risk_score": a.risk_score,
            "confidence": a.overall_confidence,
            "created_at": a.created_at,
            "reviewed_by": a.reviewed_by or "Unassigned"
        })
    df_apps = pd.DataFrame(app_records)

    total_count = len(df_apps)
    approved_count = len(df_apps[df_apps["status"] == "APPROVED"])
    rejected_count = len(df_apps[df_apps["status"] == "REJECTED"])
    flagged_count = len(df_apps[df_apps["status"].str.startswith("FLAGGED")])
    missing_count = len(df_apps[df_apps["status"] == "MISSING_DOCUMENTS"])
    stp_rate = ((approved_count + len(df_apps[df_apps["status"] == "READY_FOR_REVIEW"])) / total_count * 100) if total_count else 0
    avg_risk = df_apps["risk_score"].mean()

    # Top KPI Row
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Applications", total_count)
    k2.metric("Automation / STP Rate", f"{stp_rate:.1f}%")
    k3.metric("Exception Rate", f"{(flagged_count + missing_count) / total_count * 100:.1f}%")
    k4.metric("Approved Count", approved_count)
    k5.metric("Average Risk Score", f"{avg_risk:.1f}/100")

    st.divider()

    # Visualizations Row 1
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("### Application Status Breakdown")
        status_counts = df_apps["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        color_map = {
            "APPROVED": "#10B981",
            "READY_FOR_REVIEW": "#F59E0B",
            "FLAGGED_UNCLEAR": "#EF4444",
            "FLAGGED_DUPLICATE": "#DC2626",
            "FLAGGED_INCONSISTENCY": "#B91C1C",
            "MISSING_DOCUMENTS": "#8B5CF6",
            "REJECTED": "#64748B",
            "SUBMITTED": "#3B82F6"
        }

        fig_status = px.bar(
            status_counts,
            x="Status",
            y="Count",
            color="Status",
            color_discrete_map=color_map,
            text="Count"
        )
        fig_status.update_layout(xaxis_title="", yaxis_title="Applications", showlegend=False)
        st.plotly_chart(fig_status, use_container_width=True)

    with col_chart2:
        st.markdown("### Risk Level Distribution")
        risk_counts = df_apps["risk_level"].value_counts().reset_index()
        risk_counts.columns = ["Risk Level", "Count"]

        fig_risk = px.pie(
            risk_counts,
            names="Risk Level",
            values="Count",
            hole=0.45,
            color="Risk Level",
            color_discrete_map={"LOW": "#10B981", "MEDIUM": "#F59E0B", "HIGH": "#EF4444"}
        )
        st.plotly_chart(fig_risk, use_container_width=True)

    st.divider()

    # Visualizations Row 2: Exception Root Causes & Quality Analysis
    col_chart3, col_chart4 = st.columns(2)

    with col_chart3:
        st.markdown("### Exception Categories Root Causes")
        exception_apps = df_apps[df_apps["status"].isin(["FLAGGED_UNCLEAR", "FLAGGED_DUPLICATE", "FLAGGED_INCONSISTENCY", "MISSING_DOCUMENTS"])]
        if not exception_apps.empty:
            exc_counts = exception_apps["status"].value_counts().reset_index()
            exc_counts.columns = ["Exception Type", "Count"]
            fig_exc = px.bar(
                exc_counts,
                y="Exception Type",
                x="Count",
                orientation="h",
                color="Exception Type",
                color_discrete_sequence=["#EF4444", "#F97316", "#8B5CF6", "#EC4899"]
            )
            fig_exc.update_layout(showlegend=False)
            st.plotly_chart(fig_exc, use_container_width=True)
        else:
            st.info("No exceptions recorded yet.")

    with col_chart4:
        st.markdown("### Document Sharpness & Quality Index")
        if docs:
            doc_quality = [d.quality_score for d in docs if d.quality_score is not None]
            df_quality = pd.DataFrame({"Sharpness Index (Laplacian)": doc_quality})
            fig_qual = px.histogram(
                df_quality,
                x="Sharpness Index (Laplacian)",
                nbins=15,
                color_discrete_sequence=["#2563EB"]
            )
            fig_qual.add_vline(x=100.0, line_dash="dash", line_color="red", annotation_text="Quality Threshold (100.0)")
            st.plotly_chart(fig_qual, use_container_width=True)
        else:
            st.info("No document records.")

    st.divider()

    # Exportable Data Table
    st.markdown("### Exportable Applications Master Ledger")
    st.dataframe(df_apps, use_container_width=True)
    csv = df_apps.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Master Report as CSV", data=csv, file_name="onboarding_master_report.csv", mime="text/csv")

