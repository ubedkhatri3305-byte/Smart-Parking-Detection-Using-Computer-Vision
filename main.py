"""
Application Entry Point for Local Development and Cloud Hosting (Render / Railway)
Reads $PORT environment variable automatically assigned by cloud platforms.
"""

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"[*] Starting Smart Parking Detection server on port {port}...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)
