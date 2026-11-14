import streamlit as st
import pandas as pd
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.database import get_db
from backend.app.models.audit_log import AuditLog
from backend.app.services.audit_service import AuditService

st.set_page_config(page_title="Audit Trail Explorer", page_icon="📜", layout="wide")

st.title("📜 Regulatory Audit Trail & Governance Explorer")
st.markdown("Chronological, immutable audit ledger tracking all automated AI decisions, quality screenings, and authorized human reviewer actions.")

with get_db() as db:
    logs = AuditService.get_all_logs(db, limit=300)

    if not logs:
        st.info("No audit logs recorded yet. Once applications are submitted and verified, all events will appear here.")
        st.stop()

    # Search & Filter Bar
    c_search, c_actor = st.columns([2, 1])
    with c_search:
        search_query = st.text_input("Search by Application ID or Reason:", placeholder="e.g. Vikramaditya or ID prefix...")
    with c_actor:
        actor_options = ["ALL"] + sorted(list(set([l.actor for l in logs])))
        selected_actor = st.selectbox("Filter by Actor:", actor_options)

    # Filter logs
    filtered_logs = logs
    if selected_actor != "ALL":
        filtered_logs = [l for l in filtered_logs if l.actor == selected_actor]
    if search_query.strip():
        q = search_query.lower()
        filtered_logs = [
            l for l in filtered_logs
            if (l.application_id and q in l.application_id.lower())
            or (l.reason and q in l.reason.lower())
            or (l.action and q in l.action.lower())
        ]

    st.markdown(f"**Showing {len(filtered_logs)} Audit Event(s)**")

    # Table View
    log_data = []
    for l in filtered_logs:
        log_data.append({
            "Timestamp (UTC)": l.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Actor": l.actor,
            "Action": l.action,
            "Transition": f"{l.previous_state or 'None'} ➔ {l.new_state or 'None'}",
            "Application ID": l.application_id[:8] + "..." if l.application_id else "-",
            "Reason / Notes": l.reason[:65] + "..." if (l.reason and len(l.reason) > 65) else (l.reason or "-")
        })

    st.dataframe(log_data, use_container_width=True)

    st.divider()

    # Expandable Detailed Event Viewer
    st.markdown("### Detailed Event Inspection")
    for l in filtered_logs[:15]:
        with st.expander(f"[{l.timestamp.strftime('%H:%M:%S')}] {l.action} by {l.actor} (App #{l.application_id[:8] if l.application_id else 'N/A'})"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Action:** `{l.action}`")
                st.write(f"**Actor:** `{l.actor}`")
                st.write(f"**State Transition:** `{l.previous_state}` ➔ `{l.new_state}`")
            with c2:
                st.write(f"**Timestamp:** `{l.timestamp.isoformat()}`")
                st.write(f"**Application ID:** `{l.application_id}`")
                st.write(f"**Reason:** {l.reason}")
            if l.metadata_json:
                st.markdown("**Event Payload Metadata:**")
                st.json(l.metadata_json)

