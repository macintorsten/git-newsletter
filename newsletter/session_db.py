"""
Session database manager.

Provides helpers to load, save, and update the shared SessionDatabase JSON
file that all agents read from and write to during a pipeline run.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from newsletter.models import SessionDatabase


_DEFAULT_DB_PATH = Path("newsletter_session.json")


def load(path: str | Path | None = None) -> SessionDatabase:
    """Load the session database from *path* (or the default path)."""
    db_path = Path(path) if path else _DEFAULT_DB_PATH
    if db_path.exists():
        with db_path.open("r", encoding="utf-8") as fh:
            return SessionDatabase.from_dict(json.load(fh))
    return SessionDatabase()


def save(db: SessionDatabase, path: str | Path | None = None) -> Path:
    """Persist *db* to *path* (or the default path) and return the path used."""
    db_path = Path(path) if path else _DEFAULT_DB_PATH
    with db_path.open("w", encoding="utf-8") as fh:
        fh.write(db.to_json())
    return db_path


def log(db: SessionDatabase, message: str) -> None:
    """Append a timestamped log entry to the database."""
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    db.logs.append(f"[{ts}] {message}")
