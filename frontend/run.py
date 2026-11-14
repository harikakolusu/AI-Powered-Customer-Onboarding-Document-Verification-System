"""
Frontend Runner — Launches the Streamlit app.

Usage:
    python frontend/run.py              → Start on default port 8501
    python frontend/run.py --port 8502  → Start on custom port
"""
import subprocess
import sys
from pathlib import Path

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def main():
    print("=" * 55)
    print("  Frontend — Streamlit App")
    print("=" * 55)

    # Parse optional port argument
    port = "8501"
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = sys.argv[idx + 1]

    frontend_app = Path(__file__).resolve().parent / "app.py"

    print(f"\n  Starting Streamlit on port {port}...")
    print(f"  Open: http://localhost:{port}")
    print(f"  Press Ctrl+C to stop\n")

    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(frontend_app),
        "--server.port", port,
    ]
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
