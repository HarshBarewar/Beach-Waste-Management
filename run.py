#!/usr/bin/env python
"""
BeachWaste AI - Single-Command Development Runner.

Launches both FastAPI Backend (port 8000) and React Vite Frontend (port 5173)
concurrently, ensures dependencies and ports are free, waits for readiness,
and automatically opens the application in your default browser.

Usage:
    python run.py
"""
import sys
import os
import time
import subprocess
import signal
import webbrowser
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"

def free_port(port: int):
    """Kills any stale process currently holding the target port."""
    try:
        if sys.platform == "win32":
            res = subprocess.run(
                f"netstat -ano | findstr :{port}",
                shell=True,
                capture_output=True,
                text=True
            )
            for line in res.stdout.splitlines():
                parts = line.strip().split()
                if len(parts) >= 5 and "LISTENING" in parts:
                    pid = parts[-1]
                    try:
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
                        print(f"  [cleanup] Cleared lingering process (PID {pid}) on port {port}")
                    except Exception:
                        pass
        else:
            subprocess.run(f"lsof -ti :{port} | xargs kill -9", shell=True, capture_output=True)
    except Exception:
        pass

def get_python_exe() -> str:
    """Finds best Python executable (active venv or sys.executable)."""
    if sys.platform == "win32":
        venv_py = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
    else:
        venv_py = ROOT_DIR / ".venv" / "bin" / "python"
    
    if venv_py.exists():
        return str(venv_py)
    return sys.executable

def check_frontend_deps():
    """Installs frontend dependencies if node_modules is missing."""
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("  [setup] Installing frontend node_modules (first-time setup)...")
        subprocess.run("npm install", cwd=str(FRONTEND_DIR), shell=True, check=True)
        print("  [setup] Frontend packages installed successfully.")

def wait_for_url(url: str, timeout: int = 20) -> bool:
    """Polls a URL until it responds with HTTP 200 or timeout expires."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "BeachWaste-Runner"})
            with urllib.request.urlopen(req, timeout=1.5) as response:
                if response.status in (200, 304):
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

def main():
    print("=" * 68)
    print("   BeachWaste AI - Deep Learning Global Waste Platform")
    print("=" * 68)

    # 1. Clear ports if needed
    free_port(8000)
    free_port(5173)

    # 2. Check frontend dependencies
    check_frontend_deps()

    py_exe = get_python_exe()
    backend_env = os.environ.copy()
    backend_env["PYTHONPATH"] = str(ROOT_DIR)

    # 3. Launch Backend Process
    print("\n  [*] Starting Backend (FastAPI on http://127.0.0.1:8000)...")
    backend_proc = subprocess.Popen(
        [py_exe, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(ROOT_DIR),
        env=backend_env
    )

    # 4. Launch Frontend Process
    print("  [*] Starting Frontend (React Vite on http://localhost:5173)...")
    frontend_proc = subprocess.Popen(
        "npm run dev",
        cwd=str(FRONTEND_DIR),
        shell=True
    )

    def shutdown(signum=None, frame=None):
        print("\n\n  [*] Shutting down BeachWaste AI servers cleanly...")
        try:
            backend_proc.terminate()
            backend_proc.wait(timeout=3)
        except Exception:
            try:
                backend_proc.kill()
            except Exception:
                pass

        try:
            if sys.platform == "win32":
                subprocess.run(f"taskkill /F /T /PID {frontend_proc.pid}", shell=True, capture_output=True)
            else:
                frontend_proc.terminate()
        except Exception:
            pass

        free_port(8000)
        free_port(5173)
        print("  [OK] All servers stopped. Have a great day!\n")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)

    # 5. Wait for readiness
    backend_ready = wait_for_url("http://127.0.0.1:8000/api/health", timeout=15)
    frontend_ready = wait_for_url("http://localhost:5173", timeout=15)

    print("\n" + "=" * 68)
    if backend_ready and frontend_ready:
        print("  [SUCCESS] BEACHWASTE AI IS RUNNING & READY!")
    else:
        print("  [!] Servers starting up...")
    print("=" * 68)
    print("  Web Application:    http://localhost:5173")
    print("  Backend API Docs:   http://127.0.0.1:8000/docs")
    print("  API Health Check:   http://127.0.0.1:8000/api/health")
    print("=" * 68)
    print("  Tip: Press Ctrl+C at any time in this window to stop both servers.")
    print("=" * 68 + "\n")

    # Automatically open browser
    try:
        webbrowser.open("http://localhost:5173")
    except Exception:
        pass

    # Monitor loop
    try:
        while True:
            # If any process unexpectedly died, report and exit
            if backend_proc.poll() is not None:
                print(f"\n[Warning] Backend process exited unexpectedly with code {backend_proc.returncode}")
                break
            if frontend_proc.poll() is not None:
                print(f"\n[Warning] Frontend process exited unexpectedly with code {frontend_proc.returncode}")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        shutdown()

if __name__ == "__main__":
    main()
