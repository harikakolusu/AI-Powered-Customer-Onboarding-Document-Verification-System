import streamlit as st
import json
from pathlib import Path
from PIL import Image

def render_status_badge(status: str) -> str:
    status_map = {
        "APPROVED": ("#DCFCE7", "#166534", "Approved"),
        "READY_FOR_REVIEW": ("#FEF3C7", "#92400E", "Ready for Review"),
        "FLAGGED_UNCLEAR": ("#FEE2E2", "#991B1B", "Flagged: Unclear Document"),
        "FLAGGED_DUPLICATE": ("#FEE2E2", "#991B1B", "Flagged: Duplicate Application"),
        "FLAGGED_INCONSISTENCY": ("#FEE2E2", "#991B1B", "Flagged: Identity Inconsistency"),
        "MISSING_DOCUMENTS": ("#EDE9FE", "#5B21B6", "Action Required: Missing Docs"),
        "REJECTED": ("#F1F5F9", "#475569", "Rejected"),
        "SUBMITTED": ("#E0F2FE", "#0369A1", "Submitted"),
    }
    bg, fg, label = status_map.get(status, ("#E2E8F0", "#334155", status))
    return f"""<span style="background-color: {bg}; color: {fg}; padding: 4px 10px; border-radius: 9999px; font-size: 13px; font-weight: 600;">{label}</span>"""

def render_risk_badge(risk_level: str, risk_score: float) -> str:
    if risk_level == "LOW":
        bg, fg = "#DCFCE7", "#166534"
    elif risk_level == "MEDIUM":
        bg, fg = "#FEF3C7", "#92400E"
    else:
        bg, fg = "#FEE2E2", "#991B1B"
    return f"""<span style="background-color: {bg}; color: {fg}; padding: 3px 8px; border-radius: 6px; font-size: 12px; font-weight: 700;">{risk_level} ({risk_score:.0f}/100)</span>"""

def display_document_card(doc):
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"**Document Scan ({doc.document_type})**")
        file_path = Path(doc.file_path)
        if file_path.exists():
            if file_path.suffix.lower() == ".pdf":
                st.info(f"📄 **PDF Document:** {doc.original_filename}\n\nQuality Index: {doc.quality_score:.1f}")
                with open(file_path, "rb") as f_pdf:
                    st.download_button(
                        label=f"⬇️ View / Download {doc.original_filename}",
                        data=f_pdf.read(),
                        file_name=doc.original_filename,
                        mime="application/pdf",
                        key=f"dl_pdf_{doc.id}"
                    )
            else:
                st.image(str(file_path), caption=f"{doc.original_filename} (Sharpness: {doc.quality_score:.1f})", use_container_width=True)
        else:
            st.warning("File scan preview not available on disk.")
    with col2:
        st.markdown("**AI-Extracted Structured Fields**")
        if doc.extracted_data:
            st.json(doc.extracted_data)
        else:
            st.info("No extracted entity data.")
        st.caption(f"Extraction Confidence: {doc.extraction_confidence * 100:.1f}% | Quality: {'Clear' if doc.is_clear else 'Degraded'}")

