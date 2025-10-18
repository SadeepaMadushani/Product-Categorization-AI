import subprocess
import sys
import time
import webbrowser

def run_backend():
    print("🚀 Starting FastAPI backend...")
    backend = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "backend.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"
    ])
    return backend

def run_frontend():
    print("🎨 Starting Streamlit frontend...")
    frontend = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "app.py"
    ], cwd="frontend")
    return frontend

if __name__ == "__main__":
    backend = run_backend()
    time.sleep(3)  # give backend time to start

    frontend = run_frontend()
    time.sleep(5)  # give streamlit time to load

    streamlit_url = "http://localhost:8501"
    print(f"✅ Backend running on http://127.0.0.1:8000 | Frontend running on {streamlit_url}")

  

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        backend.terminate()
        frontend.terminate()
