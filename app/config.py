"""Settings come from environment variables, or from a .env file in the project root.

Real environment variables win over the .env file. Copy .env.example to .env to start.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_env(path):
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env(ROOT / ".env")


def data_dir():
    """Where images, the database and the prepared cache live (default: ./data)."""
    p = Path(os.environ.get("DATA_DIR", "data"))
    return p if p.is_absolute() else ROOT / p
