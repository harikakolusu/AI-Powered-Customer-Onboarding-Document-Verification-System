"""
Combined Runner — Initializes backend + launches frontend together.

For separate execution, use:
    python backend/run.py      → Backend only (DB + sample data)
    python frontend/run.py     → Frontend only (Streamlit UI)
"""
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def main():
    print("=" * 65)
    print("Apex AI-Powered Customer Onboarding & Verification System")
    print("=" * 65)

    # 1. Initialize backend
    from backend.app.database import init_db
    from backend.app.utils.synthetic_data import generate_all_scenario_documents

    print("[1/3] Initializing SQLite database...")
    init_db()

    print("[2/3] Generating synthetic benchmark test documents (Scenarios 1-5)...")
    generate_all_scenario_documents()

    # 2. Launch frontend
    print("[3/3] Launching Streamlit Frontend Portal...")
    frontend_app = BASE_DIR / "frontend" / "app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(frontend_app)]
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
