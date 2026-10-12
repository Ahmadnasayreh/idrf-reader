"""Safe copy of the scoring database while the app is running.

    python tools/backup.py

Writes data/backups/idrf-YYYY-MM-DD_HHMM.db and keeps the 30 most recent copies.
"""
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config  # noqa: E402

data = config.data_dir()
out_dir = data / "backups"
out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / f'idrf-{datetime.now().strftime("%Y-%m-%d_%H%M")}.db'
src = sqlite3.connect(data / "idrf.db")
dst = sqlite3.connect(out)
with dst:
    src.backup(dst)
src.close()
dst.close()
for old in sorted(out_dir.glob("idrf-*.db"))[:-30]:
    old.unlink()
print("Backup written to", out)
