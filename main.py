import sys
import os

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from apps.control_plane.main import app

# This entry point is used by Vercel's Python runtime
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
