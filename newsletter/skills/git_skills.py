"""
Thin re-export shim for git skill functions.

The canonical implementation lives co-located with its SKILL.md definition at:
  .github/skills/git-research/git_skills.py

This module exists purely for Python package compatibility so that the CLI
orchestrator can continue to import `newsletter.skills.git_skills` unchanged.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_impl = (
    Path(__file__).resolve().parents[2]
    / ".github" / "skills" / "git-research" / "git_skills.py"
)
if not _impl.exists():
    raise FileNotFoundError(
        f"Co-located skill script not found: {_impl}\n"
        "Ensure .github/skills/git-research/git_skills.py exists in the repository root."
    )

_spec = importlib.util.spec_from_file_location("_git_skills_impl", _impl)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

get_recent_commits = _mod.get_recent_commits
get_branch_activity = _mod.get_branch_activity
get_stale_branches = _mod.get_stale_branches
get_merged_branches = _mod.get_merged_branches
get_commit_diff = _mod.get_commit_diff
