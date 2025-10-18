import os
import sys

# Ensure the backend package is importable when running on Vercel
current_dir = os.path.dirname(__file__)
backend_dir = os.path.join(current_dir, "backend")
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Expose FastAPI `app` for the platform to detect
from api.main import app  # noqa: E402


