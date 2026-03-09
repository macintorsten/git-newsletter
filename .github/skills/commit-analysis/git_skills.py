"""
Git skill implementations.

These functions are the low-level building blocks used by the GitSource adapter
and can also be called directly by VS Code Copilot agents that follow the
commit-analysis SKILL.md instructions.

All functions return plain JSON-serialisable dicts / lists so they can be
written directly into the session database.

Both **local paths** and **remote URLs** are supported identically:
  - Local path: ``/path/to/repo`` or ``.``
  - Remote URL:  ``https://github.com/org/repo.git``  or
                 ``git@github.com:org/repo.git``

For remote URLs the repository is cloned once into a temporary directory the
first time any skill function is called.  Subsequent calls within the same
process reuse the cached ``git.Repo`` object — no extra cloning takes place.
The temporary directory is deleted automatically when the process exits.

Dependencies: gitpython (git)
"""

from __future__ import annotations

import atexit
import shutil
import tempfile
from datetime import datetime, timezone, timedelta
from typing import Any, Iterator

# Module-level repo cache: original_path → (Repo, temp_dir_or_None)
_repo_cache: dict[str, tuple[Any, str | None]] = {}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _open_repo(repo_path: str) -> Any:
    """
    Return a ``git.Repo`` object for *repo_path*, using a module-level cache.

    Remote URLs are cloned once with ``--no-single-branch`` so that all remote
    tracking refs (and therefore all branches) are available.  The temp
    directory is registered with ``atexit`` for automatic cleanup.

    Local paths use ``search_parent_directories=True`` so that calling with a
    subdirectory of a repo works correctly.
    """
    if repo_path in _repo_cache:
        return _repo_cache[repo_path][0]

    try:
        import git
    except ImportError as exc:
        raise ImportError(
            "gitpython is required for git skills. "
            "Install it with: pip install gitpython"
        ) from exc

    if repo_path.startswith(("http://", "https://", "git@", "ssh://")):
        tmp = tempfile.mkdtemp(prefix="git-newsletter-")
        atexit.register(shutil.rmtree, tmp, ignore_errors=True)
        repo = git.Repo.clone_from(repo_path, tmp, no_single_branch=True)
        _repo_cache[repo_path] = (repo, tmp)
    else:
        repo = git.Repo(repo_path, search_parent_directories=True)
        _repo_cache[repo_path] = (repo, None)

    return repo


def _iter_branches(repo: Any) -> Iterator[tuple[str, Any]]:
    """
    Yield ``(normalised_name, ref)`` for every unique branch in *repo*.

    Local heads are preferred when they exist; remote-tracking refs fill in
    everything that has not been checked out locally.  ``HEAD`` pseudo-refs
    are skipped.
    """
    seen: set[str] = set()

    # Local branches first (present in local clones and working copies)
    for ref in repo.heads:
        if ref.name not in seen:
            seen.add(ref.name)
            yield ref.name, ref

    # Remote tracking refs — essential when the repo was freshly cloned,
    # because only the default branch is checked out locally in that case.
    for remote in repo.remotes:
        for ref in remote.refs:
            # RemoteReference.remote_head gives the branch name without the
            # "origin/" prefix (e.g. "feature/my-thing" not "origin/feature/…")
            name: str = getattr(ref, "remote_head", None) or ref.name
            if name in ("HEAD", "") or name in seen:
                continue
            seen.add(name)
            yield name, ref


def _find_ref(repo: Any, branch_name: str) -> Any | None:
    """
    Return the ref object for *branch_name*, checking local heads first and
    remote-tracking refs as a fallback.  Returns ``None`` if not found.
    """
    # Local head
    try:
        return repo.heads[branch_name]
    except (IndexError, Exception):
        pass

    # Remote tracking ref (works for freshly cloned repos)
    for remote in repo.remotes:
        for ref in remote.refs:
            name = getattr(ref, "remote_head", None) or ref.name
            if name == branch_name:
                return ref

    return None


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


# ---------------------------------------------------------------------------
# Public skill functions
# ---------------------------------------------------------------------------

def get_recent_commits(
    repo_path: str,
    branch: str = "main",
    period_days: int = 7,
) -> list[dict[str, Any]]:
    """
    Return all commits on *branch* made within the last *period_days* days.

    Works identically for local paths and remote URLs.  For remote repos the
    repository is cloned once and cached for the lifetime of the process.

    Each entry is a plain dict matching the ``CommitRecord`` schema.
    """
    repo = _open_repo(repo_path)
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=period_days)

    # Find the ref — prefer local head, fall back to remote tracking ref
    ref = _find_ref(repo, branch)
    if ref is None:
        raise ValueError(
            f"Branch {branch!r} not found in {repo_path!r}. "
            "Check the branch name and ensure the repo has been fetched."
        )

    results: list[dict[str, Any]] = []
    for commit in repo.iter_commits(ref, max_count=500):
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
    Return a summary of activity for every branch (local + remote tracking).

    Works identically for local paths and remote URLs.
    """
    repo = _open_repo(repo_path)
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=period_days)

    results: list[dict[str, Any]] = []
    for name, ref in _iter_branches(repo):
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

    Works identically for local paths and remote URLs.
    """
    repo = _open_repo(repo_path)
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=stale_after_days)

    results: list[dict[str, Any]] = []
    for name, ref in _iter_branches(repo):
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
    Return names of branches merged into *target_branch* within the last
    *period_days* days.

    Works identically for local paths and remote URLs.
    """
    repo = _open_repo(repo_path)
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=period_days)

    # Build the set of remote-merged branch names reported by git
    try:
        merged_output = repo.git.branch("--merged", target_branch, "-r")
        # Lines look like "  origin/feature/foo" — normalise to "feature/foo"
        merged_set: set[str] = set()
        for line in merged_output.splitlines():
            stripped = line.strip()
            if not stripped or "HEAD" in stripped:
                continue
            # Strip the leading "origin/" (or any remote name)
            if "/" in stripped:
                merged_set.add(stripped.split("/", 1)[1])
            else:
                merged_set.add(stripped)
    except Exception:
        return []

    results: list[str] = []
    for name, ref in _iter_branches(repo):
        if name == target_branch or name not in merged_set:
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
