# 🏦 AI-Powered Customer Onboarding & KYC Document Verification System

An intelligent, enterprise-grade banking customer onboarding system that automates document processing, quality pre-screening, AI-driven entity extraction, duplicate fraud prevention, and cross-document discrepancy detection while keeping **Human-in-the-Loop** approval workflows for compliance.

---

## 🏛️ Architecture & Separation of Concerns

The project strictly decouples presentation from core backend intelligence:

```text
projects/
├── backend/                  # Core Business Logic & AI Engines
│   ├── app/
│   │   ├── config.py         # Configs, LLM flags, thresholds
│   │   ├── database.py       # SQLAlchemy engine & session manager
│   │   ├── models/           # ORM Models (Customer, Application, Document, Verification, Audit)
│   │   ├── schemas/          # Pydantic Schemas (PAN, Aadhaar, Bank Statement, Consistency)
│   │   ├── services/         # Quality check, LLM engine, Duplicate check, Router, Audit logger
│   │   └── utils/            # Synthetic data & benchmark KYC document generator
│   ├── tests/
│   │   └── test_scenarios.py # Automated Pytest suite covering all 5 business scenarios
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # Interactive Streamlit Multi-page App
│   ├── app.py                # System landing page & 1-click scenario test bench
│   ├── pages/
│   │   ├── 1_📤_Customer_Upload.py   # Document upload portal (Custom & Scenario runs)
│   │   ├── 2_📋_Reviewer_Queue.py     # Split-screen reviewer inspection & human decision form
│   │   ├── 3_📊_Manager_Dashboard.py # Real-time Plotly charts, throughput, SLA & STP %
│   │   └── 4_📜_Audit_Log.py          # Regulatory chronological audit trail explorer
│   ├── components/           # Reusable UI widgets & badges (ui_helpers.py)
│   └── assets/               # CSS styles & banking theme (style.css)
│
├── storage/                  # SQLite DB (`onboarding.db`) & synthetic benchmark documents
├── run_app.py                # Unified one-command launch script
├── .env.example              # Environment variables template
└── README.md                 # Project documentation & runbook
```

---

## 📋 Expected Solution vs. Implementation Mapping

| Module | Requirement | Implementation in System |
| :--- | :--- | :--- |
| **Document Upload** | Accept PDF and image documents (PNG, JPG, PDF) | `1_📤_Customer_Upload.py` supports multi-format file uploads and batch KYC bundles. |
| **Data Extraction** | Extract name, ID number, address, DOB | `llm_service.py` extracts strictly-typed JSON using Pydantic schemas (`PanCardExtraction`, `AadhaarCardExtraction`, `BankStatementExtraction`). |
| **Document Validation** | Identify missing or invalid information | `validation_service.py` enforces regex rules (PAN format, Aadhaar 12-digit, IFSC) and mandatory document checklist. |
| **Duplicate Detection** | Detect repeated customer applications | `duplicate_service.py` checks exact PAN/Aadhaar and demographic matches against existing records in SQLite. |
| **AI Analysis** | Identify inconsistencies between submitted documents | `consistency_service.py` runs semantic cross-matching (comparing names, DOB, address across documents) with discrepancy severity scoring. |
| **Exception Handling** | Route problematic applications to human reviewers | `routing_service.py` computes risk scores (0–100) and automatically routes blurry, mismatched, or duplicate applications to exceptions. |
| **Approval Workflow** | Authorized employees can approve or reject | `2_📋_Reviewer_Queue.py` provides split-screen document comparison and decision actions (`APPROVE`, `REJECT`, `REQUEST_REUPLOAD`). |
| **Dashboard** | Display application status & processing metrics | `3_📊_Manager_Dashboard.py` renders interactive Plotly charts (SLA, STP %, status breakdown, risk distribution). |
| **Audit Trail** | Maintain history of every important action | `audit_service.py` writes append-only records to `audit_logs` table, fully searchable in `4_📜_Audit_Log.py`. |

---

## 🤖 LLM Technology Integration

1. **Multimodal Structured Extraction**:
   - Direct document analysis using **Google Gemini Vision** (`gemini-1.5-flash`).
   - Guarantees strict type safety via **Pydantic schemas** (`PanCardExtraction`, `AadhaarCardExtraction`, `BankStatementExtraction`).
   - Extracts: Full Name, Father's Name, Date of Birth, ID Numbers, Gender, Address, Confidence score, and Visual Anomalies.

2. **AI Cross-Document Inconsistency Analyzer**:
   - Compares identities across disparate documents (PAN vs. Aadhaar vs. Bank Statement).
   - Identifies whether naming variations are acceptable abbreviations/initials (e.g. `K. Viswateja` vs `Viswateja Kumar`) or true fraudulent identity mismatches.
   - Outputs an audit-ready narrative and severity rating (`LOW`, `MEDIUM`, `HIGH`).

3. **Hybrid Offline/Online Fallback**:
   - The engine automatically uses the live Gemini API when `GEMINI_API_KEY` is present.
   - When offline or during automated testing, an intelligent local fallback ensures 100% demo fidelity without external network latency or failure.

---

## 🎯 5 Core Business Scenarios

| Scenario | Trigger & Document Profile | System Behavior | Final State |
| :--- | :--- | :--- | :--- |
| **Scenario 1** | Customer uploads valid PAN + Aadhaar + Statement. Clean scan, matching details. | Extraction $>90\%$ confidence; format validated; moves to Human Review Queue. | `READY_FOR_REVIEW` $\rightarrow$ `APPROVED` |
| **Scenario 2** | Blurry / degraded PAN card uploaded. | Laplacian variance $< 100.0$; flags blur; routes to manual exception queue. | `FLAGGED_UNCLEAR` |
| **Scenario 3** | Customer submits an application with an already registered PAN. | Database lookup catches identical PAN; flags duplicate fraud risk. | `FLAGGED_DUPLICATE` |
| **Scenario 4** | PAN has *Ananya Deshmukh*, Aadhaar has *Pooja Sharma*. | AI cross-matching engine flags identity discrepancy with explanatory diff. | `FLAGGED_INCONSISTENCY` |
| **Scenario 5** | Customer uploads PAN but forgets Address Proof. | Completeness validation fails mandatory checklist; halts application. | `MISSING_DOCUMENTS` |

---

## ⚡ Quick Start Guide

### 1. Installation

Install the required dependencies:

```bash
pip install -r backend/requirements.txt
```

### 2. Configure Environment (Optional for Live Gemini API)

Copy `.env.example` to `.env`:

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**Windows (CMD):**

```cmd
copy .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

Add your `GEMINI_API_KEY` in `.env` to enable live multimodal extraction. If left blank, the built-in intelligent fallback seamlessly handles all 5 test scenarios.

### 3. Run Automated Tests (Pytest)

Run the test suite verifying all 5 business scenarios:

```bash
python -m pytest backend/tests/test_scenarios.py -v
```

### 4. Launch the Application

Run the one-click startup runner (auto-initializes DB, generates sample data, and starts the frontend):

```bash
python run_app.py
```

Or directly via Streamlit:

```bash
streamlit run frontend/app.py
```

---

## 🧭 Interactive Demo Walkthrough

Once the Streamlit app opens in your browser (`http://localhost:8501`):

1. **Home Page (`app.py`)**: Click **"⚡ Seed All 5 Demo Scenarios into Database"** to instantly populate the database with realistic sample cases.
2. **Reviewer Queue (`2_📋_Reviewer_Queue.py`)**:
   - Inspect applications by status (`READY_FOR_REVIEW`, `FLAGGED_UNCLEAR`, `FLAGGED_INCONSISTENCY`, etc.).
   - View the side-by-side original scans and AI-extracted entity data.
   - Record an official review decision (`APPROVE`, `REJECT`, `REQUEST_REUPLOAD`) with audit comments.
3. **Manager Dashboard (`3_📊_Manager_Dashboard.py`)**:
   - Inspect throughput, Straight-Through-Processing (STP) rate, risk level distributions, and document sharpness charts.
   - Export the master application log as a CSV.
4. **Audit Log (`4_📜_Audit_Log.py`)**:
   - Filter and review chronological audit trails for full regulatory traceability.

---

## 🛡️ Regulatory Compliance & Audit Trail

Every state transition (submission, quality screening, duplicate detection, AI cross-match, reviewer approval/rejection) is recorded to the append-only `audit_logs` table with:

- **Timestamp (UTC)**
- **Actor** (`CUSTOMER`, `SYSTEM_AI`, `SYSTEM_RULE`, `REVIEWER_<NAME>`)
- **State Transition** (`previous_state` $\rightarrow$ `new_state`)
- **Reason & Decision Comments**
- **JSON Metadata Payload**
