"""
Git data source.

Wraps the low-level git_skills helper functions and writes the results into
the shared session database under ``db.raw_data.git``.
"""

from __future__ import annotations

from typing import Any

from newsletter.sources.base import BaseSource
from newsletter.models import SessionDatabase
import newsletter.session_db as session_db
from newsletter.skills import git_skills


class GitSource(BaseSource):
    """
    Fetches commit history, branch activity, stale branches, and merge
    information from a git repository.

    Config keys (all optional – fall back to session metadata when absent):
      repo_path      str   Local path or remote URL of the repository.
      branch         str   Branch to inspect (default: "main").
      period_days    int   Look-back window in days (default: 7).
      stale_after_days int Threshold for stale branch detection (default: 30).
    """

    source_id = "git"

    def fetch(self, db: SessionDatabase) -> None:
        repo = self.config.get("repo_path") or db.metadata.repo
        branch = self.config.get("branch") or db.metadata.branch
        period_days = int(
            self.config.get("period_days") or db.metadata.period_days
        )
        stale_after_days = int(
            self.config.get("stale_after_days") or db.metadata.stale_after_days
        )

        session_db.log(
            db,
            f"GitSource: fetching {repo!r} branch={branch!r} "
            f"period={period_days}d stale={stale_after_days}d",
        )

        commits = git_skills.get_recent_commits(repo, branch, period_days)
        branch_activity = git_skills.get_branch_activity(repo, period_days)
        stale_branches = git_skills.get_stale_branches(repo, stale_after_days)
        merged_branches = git_skills.get_merged_branches(
            repo, branch, period_days
        )

        db.raw_data.git = {
            "repo": repo,
            "default_branch": branch,
            "period_days": period_days,
            "stale_after_days": stale_after_days,
            "commits": commits,
            "branch_activity": branch_activity,
            "stale_branches": stale_branches,
            "merged_branches": merged_branches,
        }

        db.status.git_research = "done"
        session_db.log(
            db,
            f"GitSource: done – {len(commits)} commits, "
            f"{len(stale_branches)} stale branches.",
        )
