"""Start IDRF Reader.

    python run.py

Settings are read from .env (copy .env.example to .env first).
"""
import os

from app import config  # noqa: F401  (loads .env)

if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8080"))
    shown = "localhost" if host in ("127.0.0.1", "0.0.0.0") else host
    print(f"\n  IDRF Reader is starting: open http://{shown}:{port} in a browser.\n  Press Ctrl+C to stop.\n")
    uvicorn.run("app.main:app", host=host, port=port, workers=1, proxy_headers=True)
