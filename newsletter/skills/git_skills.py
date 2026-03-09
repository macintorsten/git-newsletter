"""
Git skill implementations.

These functions are the low-level building blocks used by the GitSource adapter
and can also be called directly by VS Code Copilot agents that follow the
git-research SKILL.md instructions.

All functions return plain JSON-serialisable dicts / lists so they can be
written directly into the session database.

Dependencies: gitpython (git)
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


def _open_repo(repo_path: str):
    """
    Return a ``git.Repo`` object for *repo_path*.

    If *repo_path* looks like an HTTP/SSH URL the repo is cloned into a
    temporary directory first.  The caller is responsible for cleaning up
    the temp directory if needed (it is created with ``tempfile.mkdtemp``).
    """
    try:
        import git as gitpython
    except ImportError as exc:
        raise ImportError(
            "gitpython is required for git skills. "
            "Install it with: pip install gitpython"
        ) from exc

    if repo_path.startswith(("http://", "https://", "git@", "ssh://")):
        tmp = tempfile.mkdtemp(prefix="git-newsletter-")
        gitpython.Repo.clone_from(repo_path, tmp, depth=200)
        return gitpython.Repo(tmp)

    return gitpython.Repo(repo_path, search_parent_directories=True)


def _commit_to_dict(commit: Any) -> dict[str, Any]:
    """Convert a gitpython ``Commit`` object to a plain dict."""
    try:
        stats = commit.stats.total
        diff_summary = (
            f"+{stats['insertions']} -{stats['deletions']} "
            f"in {stats['files']} file(s)"
        )
    except Exception:
        diff_summary = "stats unavailable"

    try:
        diff_patch = commit.repo.git.show(commit.hexsha, "--unified=3")
    except Exception:
        diff_patch = ""

    return {
        "sha": commit.hexsha,
        "short_sha": commit.hexsha[:7],
        "author_name": commit.author.name,
        "author_email": commit.author.email,
        "committer_name": commit.committer.name,
        "committer_email": commit.committer.email,
        "timestamp": datetime.fromtimestamp(
            commit.committed_date, tz=timezone.utc
        ).isoformat(),
        "message": commit.message.strip(),
        "diff_summary": diff_summary,
        "diff_patch": diff_patch,
    }


def get_recent_commits(
    repo_path: str,
    branch: str = "main",
    period_days: int = 7,
) -> list[dict[str, Any]]:
    """
    Return all commits on *branch* made within the last *period_days* days.

    Each entry is a plain dict matching the ``CommitRecord`` schema.
    """
    repo = _open_repo(repo_path)
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=period_days)

    try:
        commits_iter = repo.iter_commits(branch, max_count=500)
    except Exception:
        # Try with origin/ prefix for remote branches
        commits_iter = repo.iter_commits(f"origin/{branch}", max_count=500)

    results: list[dict[str, Any]] = []
    for commit in commits_iter:
        committed_dt = datetime.fromtimestamp(
            commit.committed_date, tz=timezone.utc
        )
        if committed_dt < cutoff:
            break
        results.append(_commit_to_dict(commit))

    return results


def get_branch_activity(
    repo_path: str,
    period_days: int = 7,
) -> list[dict[str, Any]]:
    """
    Return a summary of activity for every branch (local + remote/origin/*).
    """
    repo = _open_repo(repo_path)
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=period_days)

    seen: set[str] = set()
    results: list[dict[str, Any]] = []

    branches: list[Any] = list(repo.heads)  # local
    try:
        branches += list(repo.remotes.origin.refs)  # remote
    except Exception:
        pass

    for ref in branches:
        name = ref.name.removeprefix("origin/")
        if name in seen:
            continue
        seen.add(name)

        try:
            last_commit = ref.commit
            last_dt = datetime.fromtimestamp(
                last_commit.committed_date, tz=timezone.utc
            )
            count = sum(
                1
                for c in repo.iter_commits(ref, max_count=500)
                if datetime.fromtimestamp(c.committed_date, tz=timezone.utc)
                >= cutoff
            )
            results.append(
                {
                    "name": name,
                    "last_commit_sha": last_commit.hexsha[:7],
                    "last_commit_timestamp": last_dt.isoformat(),
                    "last_author": last_commit.author.name,
                    "commits_in_period": count,
                }
            )
        except Exception:
            continue

    return results


def get_stale_branches(
    repo_path: str,
    stale_after_days: int = 30,
) -> list[dict[str, Any]]:
    """
    Return branches whose last commit is older than *stale_after_days* days.
    """
    repo = _open_repo(repo_path)
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=stale_after_days)

    seen: set[str] = set()
    results: list[dict[str, Any]] = []

    branches: list[Any] = list(repo.heads)
    try:
        branches += list(repo.remotes.origin.refs)
    except Exception:
        pass

    for ref in branches:
        name = ref.name.removeprefix("origin/")
        if name in seen:
            continue
        seen.add(name)

        try:
            last_commit = ref.commit
            last_dt = datetime.fromtimestamp(
                last_commit.committed_date, tz=timezone.utc
            )
            if last_dt < cutoff:
                age_days = (datetime.now(tz=timezone.utc) - last_dt).days
                results.append(
                    {
                        "name": name,
                        "last_commit_sha": last_commit.hexsha[:7],
                        "last_commit_timestamp": last_dt.isoformat(),
                        "last_author": last_commit.author.name,
                        "age_days": age_days,
                    }
                )
        except Exception:
            continue

    return results


def get_merged_branches(
    repo_path: str,
    target_branch: str = "main",
    period_days: int = 7,
) -> list[str]:
    """
    Return names of branches that were merged into *target_branch* within
    the last *period_days* days.
    """
    repo = _open_repo(repo_path)
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=period_days)

    try:
        merged_output = repo.git.branch("--merged", target_branch, "-r")
        candidates = [
            line.strip().removeprefix("origin/")
            for line in merged_output.splitlines()
            if line.strip() and "HEAD" not in line
        ]
    except Exception:
        return []

    results: list[str] = []
    for name in candidates:
        if name == target_branch:
            continue
        try:
            ref = repo.heads[name]
        except (IndexError, Exception):
            try:
                ref = repo.remotes.origin.refs[name]
            except Exception:
                continue

        try:
            last_dt = datetime.fromtimestamp(
                ref.commit.committed_date, tz=timezone.utc
            )
            if last_dt >= cutoff:
                results.append(name)
        except Exception:
            continue

    return results


def get_commit_diff(repo_path: str, sha: str) -> str:
    """Return the full unified diff for a single commit identified by *sha*."""
    repo = _open_repo(repo_path)
    try:
        return repo.git.show(sha, "--unified=3")
    except Exception as exc:
        return f"Could not retrieve diff for {sha}: {exc}"
