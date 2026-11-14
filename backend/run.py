"""
Backend Server Runner — Launches the FastAPI & Uvicorn continuous backend server.

Usage:
    python backend/run.py              → Run live backend server on http://localhost:8000
    python backend/run.py --port 8001  → Run on custom port
    python backend/run.py --test       → Run pytest test suite
"""
import sys
import subprocess
from pathlib import Path

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def run_tests():
    """Run all backend pytest tests."""
    print("\n[Testing] Running pytest suite...")
    print("-" * 60)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "backend/tests/test_scenarios.py", "-v"],
        cwd=str(BASE_DIR)
    )
    return result.returncode


def main():
    if "--test" in sys.argv:
        code = run_tests()
        sys.exit(code)

    port = 8000
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])

    print("=" * 65)
    print("  Apex AI Customer Onboarding — Backend Server (FastAPI)")
    print("=" * 65)
    print(f"\n  ✓ Live API Server:    http://127.0.0.1:{port}")
    print(f"  ✓ Interactive Docs:   http://127.0.0.1:{port}/docs")
    print(f"  ✓ Health Check:       http://127.0.0.1:{port}/health")
    print("\n  Live request & processing logs will display below.")
    print("  Press Ctrl+C to stop the backend server.\n" + "-" * 65)

    import uvicorn
    uvicorn.run(
        "backend.server:app",
        host="127.0.0.1",
        port=port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
