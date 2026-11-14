import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette
    BG_DARK = RGBColor(15, 23, 42)      # Deep Navy #0F172A
    CARD_BG = RGBColor(30, 41, 59)      # Slate Dark #1E293B
    TEXT_LIGHT = RGBColor(248, 250, 252)
    TEXT_MUTED = RGBColor(148, 163, 184)
    ACCENT_BLUE = RGBColor(56, 189, 248) # Cyan Blue #38BDF8
    ACCENT_GREEN = RGBColor(52, 211, 153)# Emerald #34D399
    ACCENT_ORANGE = RGBColor(251, 146, 60)

    def set_slide_background(slide, color=BG_DARK):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, tag, title):
        # Category Tag
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.4))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag.upper()
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.color.rgb = ACCENT_BLUE

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Accent decorative box
    dec = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.2), Inches(2.2), Inches(0.4))
    dec.fill.solid()
    dec.fill.fore_color.rgb = CARD_BG
    dec.line.color.rgb = ACCENT_BLUE
    p_dec = dec.text_frame.paragraphs[0]
    p_dec.text = "FINTECH AI HACKATHON"
    p_dec.alignment = PP_ALIGN.CENTER
    p_dec.font.size = Pt(11)
    p_dec.font.bold = True
    p_dec.font.color.rgb = ACCENT_BLUE

    # Title Box
    tbox = s1.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.5), Inches(2.2))
    tf1 = tbox.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "Apex AI: Customer Onboarding &\nDocument Verification Engine"
    p1.font.size = Pt(40)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_LIGHT

    # Subtitle
    stbox = s1.shapes.add_textbox(Inches(0.8), Inches(4.3), Inches(11.5), Inches(1.0))
    tf_st = stbox.text_frame
    tf_st.word_wrap = True
    p_st = tf_st.paragraphs[0]
    p_st.text = "Autonomous, fraud-resilient KYC processing with Multimodal Vision, Cross-Document Consistency, and Human-in-the-Loop Governance."
    p_st.font.size = Pt(18)
    p_st.font.color.rgb = TEXT_MUTED

    # Highlights row
    metrics = [
        ("3 Days → 5 Secs", "Processing Latency"),
        ("95%+", "Straight-Through Approval"),
        ("100% Audit Trail", "Regulatory Compliance"),
        ("FastAPI + Streamlit", "Decoupled Architecture")
    ]
    for idx, (m_val, m_lbl) in enumerate(metrics):
        card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 2.95), Inches(5.6), Inches(2.8), Inches(1.2))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BG
        tf_c = card.text_frame
        p_v = tf_c.paragraphs[0]
        p_v.text = m_val
        p_v.font.size = Pt(18)
        p_v.font.bold = True
        p_v.font.color.rgb = ACCENT_GREEN
        p_l = tf_c.add_paragraph()
        p_l.text = m_lbl
        p_l.font.size = Pt(12)
        p_l.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 2: Problem Statement
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Industry Pain Points", "The Crisis in Traditional Customer Onboarding")

    problems = [
        ("🐌 Extreme Processing Delays", "Traditional banking verification takes 48 to 72 hours per customer due to manual queue bottlenecks and manual data re-entry."),
        ("💸 High Operating Costs", "Banks spend upwards of $40 per onboarded user employing manual compliance teams to cross-reference identity scans."),
        ("🎭 Identity Fraud & Duplicates", "Sophisticated identity manipulation, blurry uploads, and repeated applications go undetected across fragmented branch silos."),
        ("⚖️ Regulatory & Audit Penalties", "Strict regulations (RBI, FINRA, SEC) mandate immutable decision trails. Manual notes fail compliance audits.")
    ]
    for i, (p_title, p_desc) in enumerate(problems):
        row = i // 2
        col = i % 2
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + col * 5.95), Inches(1.8 + row * 2.5), Inches(5.7), Inches(2.2))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BG
        tf = card.text_frame
        p_h = tf.paragraphs[0]
        p_h.text = p_title
        p_h.font.size = Pt(17)
        p_h.font.bold = True
        p_h.font.color.rgb = ACCENT_ORANGE
        p_d = tf.add_paragraph()
        p_d.text = "\n" + p_desc
        p_d.font.size = Pt(13)
        p_d.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 3: The Solution
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "The Innovation", "Apex AI: The Autonomous Intelligent Verification Engine")

    pillars = [
        ("1. Real-Time Pre-Screening", "OpenCV Laplacian variance immediately detects blurry or corrupted document scans before burning LLM tokens."),
        ("2. Multimodal LLM Extraction", "Google Gemini 1.5 Flash reads PAN, Aadhaar, and Bank Statements, mapped to strict Pydantic JSON schemas."),
        ("3. Cross-Document Crosscheck", "Algorithmic consistency checking verifies whether name, DOB, and ID numbers match between independent documents."),
        ("4. Human-in-the-Loop Governance", "Borderline cases (<90% confidence) are routed to a split-screen Reviewer Queue for human sign-off.")
    ]
    for i, (title, desc) in enumerate(pillars):
        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 2.95), Inches(2.0), Inches(2.8), Inches(4.7))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = ACCENT_BLUE if i == 1 else CARD_BG
        tf = card.text_frame
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(16)
        p_t.font.bold = True
        p_t.font.color.rgb = ACCENT_GREEN
        p_d = tf.add_paragraph()
        p_d.text = "\n\n" + desc
        p_d.font.size = Pt(13)
        p_d.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 4: Architecture & Tech Stack
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Engineering Design", "Two-Tier Decoupled Enterprise Stack")

    tech_cards = [
        ("🚀 Backend Core (FastAPI & Uvicorn)", [
            "Continuous REST API server running on port 8000",
            "SQLAlchemy ORM with relational schema & SQLite",
            "Interactive Swagger documentation at /docs",
            "Real-time request streaming and decision logging"
        ]),
        ("🧠 AI & Computer Vision Pipeline", [
            "OpenCV Laplacian filter for blur & resolution checks",
            "Google Gemini 1.5 Flash Vision multimodal extractor",
            "Pydantic v2 schemas enforcing strict JSON typing",
            "Zero-downtime offline regex fallback engine"
        ]),
        ("💻 Frontend Portal (Streamlit)", [
            "Customer upload wizard with instant validation feedback",
            "Compliance Reviewer Queue with side-by-side inspect",
            "Executive Plotly analytics dashboard",
            "Real-time immutable audit trail explorer"
        ])
    ]
    for i, (title, points) in enumerate(tech_cards):
        card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 3.95), Inches(2.0), Inches(3.8), Inches(4.7))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BG
        tf = card.text_frame
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(16)
        p_t.font.bold = True
        p_t.font.color.rgb = ACCENT_BLUE
        for pt in points:
            p_pt = tf.add_paragraph()
            p_pt.text = "• " + pt
            p_pt.font.size = Pt(13)
            p_pt.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 5: The 5-Stage Verification Pipeline
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Deep Dive", "The 5-Stage Automated Verification Pipeline")

    stages = [
        ("Stage 1: Pre-Processing", "OpenCV Laplacian Variance", "Computes edge sharpness score. Rejects blurry/obscured images immediately (< 100 threshold)."),
        ("Stage 2: Entity Extraction", "Gemini 1.5 Flash + Pydantic", "Extracts structured fields (Name, DOB, ID #) from images and multi-page PDFs."),
        ("Stage 3: Cross-Validation", "Deterministic Rule Engine", "Validates PAN pattern regex [A-Z]{5}[0-9]{4}[A-Z] & compares cross-document name alignment."),
        ("Stage 4: Fraud Detection", "MD5 Hash & Database Index", "Detects duplicate submissions and previously registered identity theft attempts."),
        ("Stage 5: Intelligent Routing", "Risk & Confidence Scorer", "Confidence ≥ 90% → Auto-Approved. Confidence < 90% → Human Reviewer Queue.")
    ]
    for i, (stg_name, tool, desc) in enumerate(stages):
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8 + i * 1.05), Inches(11.7), Inches(0.95))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BG
        tf = card.text_frame
        p = tf.paragraphs[0]
        p.text = f"{stg_name}  |  "
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = ACCENT_GREEN
        run_tool = p.add_run()
        run_tool.text = f"[{tool}]  —  "
        run_tool.font.color.rgb = ACCENT_BLUE
        run_tool.font.bold = True
        run_desc = p.add_run()
        run_desc.text = desc
        run_desc.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 6: 5 Benchmark Live Demo Scenarios
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Demonstration", "5 Real-World Scenarios Handled Flawlessly")

    scenarios = [
        ("Scenario 1: Happy Path", "Rahul Sharma", "Clear PAN & Aadhaar, matching names & valid regex.", "✅ Auto-Approved (95% Conf)", ACCENT_GREEN),
        ("Scenario 2: Unclear Scan", "Priya Nair", "Blurry, corrupted image upload.", "⚠️ Flagged: Low Quality / Blur", ACCENT_ORANGE),
        ("Scenario 3: Duplicate Fraud", "Amit Patel", "Submitted previously registered PAN card.", "🔴 Flagged: Duplicate Application", RGBColor(248, 113, 113)),
        ("Scenario 4: Name Inconsistency", "Sneha Reddy", "PAN reads 'Sneha Reddy', Aadhaar reads 'Sneha R K'.", "🟠 Flagged: Identity Discrepancy", ACCENT_ORANGE),
        ("Scenario 5: Missing Document", "Vikram Singh", "Submitted PAN but omitted mandatory Aadhaar card.", "🔴 Flagged: Incomplete Checklist", RGBColor(248, 113, 113)),
    ]
    for i, (scen, cust, desc, outcome, color) in enumerate(scenarios):
        card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8 + i * 1.05), Inches(11.7), Inches(0.95))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BG
        tf = card.text_frame
        p = tf.paragraphs[0]
        p.text = f"{scen} ({cust})\n"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = ACCENT_BLUE
        p2 = tf.add_paragraph()
        p2.text = f"{desc}  ➔  "
        p2.font.size = Pt(12)
        p2.font.color.rgb = TEXT_LIGHT
        run_out = p2.add_run()
        run_out.text = outcome
        run_out.font.bold = True
        run_out.font.color.rgb = color

    # ==========================================
    # SLIDE 7: Human-in-the-Loop & Compliance
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Governance & Trust", "Human-in-the-Loop & Regulatory Auditability")

    gov_cards = [
        ("Split-Screen Reviewer Queue", "Empowers compliance officers with side-by-side original scans and extracted metadata. Color-coded risk badges provide instant reason explanations for every flag."),
        ("Tri-Action Decisions", "Officers have 3 definitive actions: Approve, Reject, or Request More Info (triggering an automated customer resubmission notification)."),
        ("Immutable Audit Trail", "Every single automated check and human override is logged with timestamps, reviewer identity, and reason tags, guaranteeing 100% compliance with banking regulations."),
        ("Zero AI Hallucinations", "AI is never the sole judge. Probabilistic LLM extraction is always verified against deterministic regex patterns and rule engines.")
    ]
    for i, (g_title, g_desc) in enumerate(gov_cards):
        row = i // 2
        col = i % 2
        card = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + col * 5.95), Inches(1.8 + row * 2.5), Inches(5.7), Inches(2.2))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BG
        tf = card.text_frame
        p_h = tf.paragraphs[0]
        p_h.text = g_title
        p_h.font.size = Pt(17)
        p_h.font.bold = True
        p_h.font.color.rgb = ACCENT_GREEN
        p_d = tf.add_paragraph()
        p_d.text = "\n" + g_desc
        p_d.font.size = Pt(13)
        p_d.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 8: Business Impact & Future Scope
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Business ROI", "Transforming Banking Operations & Roadmap")

    impacts = [
        ("⚡ 98% Latency Cut", "Onboarding reduced from 72 hours down to 5 seconds for compliant users."),
        ("💰 75% Cost Reduction", "Minimizes manual review headcount while processing 10x higher volume."),
        ("🛡️ 0 Duplicate Fraud", "Identifies synthetic identities and duplicate claims at the gate."),
        ("🌐 Cloud-Ready Roadmap", "One-line swap from SQLite to PostgreSQL, Redis queues, and Docker containers.")
    ]
    for i, (title, desc) in enumerate(impacts):
        card = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 2.95), Inches(2.0), Inches(2.8), Inches(4.7))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BG
        tf = card.text_frame
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(16)
        p_t.font.bold = True
        p_t.font.color.rgb = ACCENT_BLUE
        p_d = tf.add_paragraph()
        p_d.text = "\n\n" + desc
        p_d.font.size = Pt(13)
        p_d.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 9: Conclusion & Live Demo
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)

    cbox = s9.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.5))
    tfc = cbox.text_frame
    tfc.word_wrap = True
    pc = tfc.paragraphs[0]
    pc.text = "Thank You!"
    pc.font.size = Pt(44)
    pc.font.bold = True
    pc.font.color.rgb = TEXT_LIGHT

    pc_sub = tfc.add_paragraph()
    pc_sub.text = "\nApex AI: Autonomous Customer Onboarding & Verification Engine"
    pc_sub.font.size = Pt(22)
    pc_sub.font.color.rgb = ACCENT_BLUE

    pc_demo = tfc.add_paragraph()
    pc_demo.text = "\n\n🚀 Live System Demo Links:"
    pc_demo.font.size = Pt(16)
    pc_demo.font.bold = True
    pc_demo.font.color.rgb = ACCENT_GREEN

    pc_links = tfc.add_paragraph()
    pc_links.text = "• Frontend Portal: http://localhost:8501\n• Backend REST API & Swagger: http://localhost:8000/docs\n• GitHub: https://github.com/harikakolusu/AI-Powered-Customer-Onboarding-Document-Verification-System"
    pc_links.font.size = Pt(15)
    pc_links.font.color.rgb = TEXT_MUTED

    output_path = r"C:\Users\Viswateja\OneDrive\Desktop\projects\Apex_AI_Hackathon_Pitch.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    create_deck()
