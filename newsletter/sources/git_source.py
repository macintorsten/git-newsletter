"""
Git data source.

Thin adapter that calls the git_skills helper functions and returns a plain
dict.  The result is used directly by the CLI orchestrator.

For agent workflows, agents call the skill functions in
.github/skills/git-research/git_skills.py and persist results to
session_store via SQL — no Python session database is involved.
"""

from __future__ import annotations

from typing import Any

from newsletter.skills import git_skills


def fetch(
    repo_path: str,
    branch: str = "main",
    period_days: int = 7,
    stale_after_days: int = 30,
) -> dict[str, Any]:
    """
    Fetch all git data for *repo_path* and return it as a plain dict.

    Supports both local filesystem paths and remote URLs — see
    ``.github/skills/git-research/SKILL.md`` for details.
    """
    return {
        "repo": repo_path,
        "default_branch": branch,
        "period_days": period_days,
        "stale_after_days": stale_after_days,
        "commits": git_skills.get_recent_commits(repo_path, branch, period_days),
        "branch_activity": git_skills.get_branch_activity(repo_path, period_days),
        "stale_branches": git_skills.get_stale_branches(repo_path, stale_after_days),
        "merged_branches": git_skills.get_merged_branches(repo_path, branch, period_days),
    }
