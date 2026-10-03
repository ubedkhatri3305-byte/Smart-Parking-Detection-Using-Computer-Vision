"""
Application Entry Point for Local Development and Cloud Hosting (Render / Railway / Heroku)
Exposes `app` for ASGI servers (uvicorn, gunicorn) and handles direct `python main.py` execution.
Automatically binds to $PORT (assigned by Render, defaulting to 10000 or 8000).
"""

import os
import uvicorn
from backend.main import app

if __name__ == "__main__":
    port_env = os.environ.get("PORT")
    port = int(port_env) if port_env else 8000
    print(f"[*] Starting Smart Parking Detection server on 0.0.0.0:{port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
