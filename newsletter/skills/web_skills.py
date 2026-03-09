"""
Thin re-export shim for web research skill functions.

The canonical implementation lives co-located with its SKILL.md definition at:
  .github/skills/web-research/web_skills.py

This module exists purely for Python package compatibility so that the CLI
orchestrator can continue to import `newsletter.skills.web_skills` unchanged.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_impl = (
    Path(__file__).resolve().parents[2]
    / ".github" / "skills" / "web-research" / "web_skills.py"
)
if not _impl.exists():
    raise FileNotFoundError(
        f"Co-located skill script not found: {_impl}\n"
        "Ensure .github/skills/web-research/web_skills.py exists in the repository root."
    )

_spec = importlib.util.spec_from_file_location("_web_skills_impl", _impl)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

search_web = _mod.search_web
fetch_page = _mod.fetch_page
