#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "gitpython>=3.1.40",
# ]
# ///
"""
Git skill implementations.

These functions are the low-level building blocks used by the GitSource adapter
and can also be called directly by VS Code Copilot agents that follow the
commit-analysis SKILL.md instructions.

## Library usage

Import and call any public function directly from Python:

    from git_skills import get_recent_commits, get_branch_activity, ...

## CLI usage

Run ``python git_skills.py --action <action> [options]`` (or ``uv run git_skills.py …``)
to execute a single skill function and receive JSON output on stdout:

    python git_skills.py --action recent-commits  --repo <path> [--branch main] [--days 7]
    python git_skills.py --action branch-activity --repo <path> [--days 7]
    python git_skills.py --action stale-branches  --repo <path> [--stale-after 30]
    python git_skills.py --action merged-branches --repo <path> [--target-branch main] [--days 7]
    python git_skills.py --action commit-diff     --repo <path> --sha <sha>
    python git_skills.py --action git-cmd         --repo <path> --git-args "log --oneline -5"

The ``git-cmd`` action runs an arbitrary git subcommand and returns its output
wrapped in a JSON object (``{"output": "<raw text>"}``).  It exists for
operations not covered by the named actions above, and has two concrete
advantages over calling the ``git`` binary directly:

1. **JSON output** — the result fits the same structured JSON contract as every
   other action, so parsers never need special-casing.
2. **Remote-URL auto-clone** — if ``--repo`` is a URL, the repository is cloned
   automatically into a temp directory (identical behaviour to the named
   actions), so you do not need to clone it yourself first.

``--git-args`` accepts a space-separated git subcommand and its flags
(e.g. ``"shortlog -sn HEAD"``).

All functions return plain JSON-serialisable dicts / lists so they can be
written directly into the session database.

Both **local paths** and **remote URLs** are supported identically:
  - Local path: ``/path/to/repo`` or ``.``
  - Remote URL:  ``https://github.com/org/repo.git``  or
                 ``git@github.com:org/repo.git``

For remote URLs the repository is cloned once into a **persistent on-disk
cache** and reused across process invocations.  On every reuse the clone is
updated with ``git fetch --all --prune`` so callers always see current data
without paying the full clone cost.  The cache directory is resolved in order:

1. ``$GIT_NEWSLETTER_CACHE_DIR`` — used directly as the repos root (no
   extra subdirectories added); useful for CI or isolated testing
2. ``$XDG_CACHE_HOME/git-newsletter/repos``
3. ``~/.cache/git-newsletter/repos``

Each remote URL maps to a sub-directory whose name is a short SHA-256 hash of
the URL.  Pass ``--no-cache`` (CLI) or ``force_reclone=True`` (Python) to
delete the cached clone and start fresh.

Dependencies: gitpython (git)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Iterator

# Module-level repo cache: original_path → Repo
_repo_cache: dict[str, Any] = {}


def _remote_clone_dir(url: str) -> Path:
    """
    Return the persistent on-disk cache directory for a remote URL clone.

    The directory is deterministic — it is derived from a short SHA-256 hash of
    the URL — so multiple processes targeting the same URL always land in the
    same place.  Directory resolution order:

    1. ``$GIT_NEWSLETTER_CACHE_DIR`` — used directly as the repos root (useful
       for CI or testing; no extra subdirectories are appended)
    2. ``$XDG_CACHE_HOME/git-newsletter/repos``
    3. ``~/.cache/git-newsletter/repos``
    """
    if override := os.environ.get("GIT_NEWSLETTER_CACHE_DIR"):
        cache_root = Path(override)
    else:
        xdg = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
        cache_root = Path(xdg) / "git-newsletter" / "repos"
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
    return cache_root / url_hash


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _open_repo(repo_path: str, *, force_reclone: bool = False) -> Any:
    """
    Return a ``git.Repo`` object for *repo_path*, using a module-level cache.

    **Local paths** are opened with ``search_parent_directories=True`` so that
    calling with a subdirectory of a repo works correctly.

    **Remote URLs** use a persistent on-disk cache so that multiple process
    invocations (e.g. different agents both running git_skills.py) reuse the
    same clone instead of each paying the full clone cost:

    - On the first call the repo is cloned with ``--no-single-branch`` so that
      all remote tracking refs are available.
    - On subsequent calls the existing clone is opened and updated with
      ``git fetch --all --prune``.  If the fetch fails (e.g. network issue) a
      warning is printed to stderr and the stale clone is used as-is.
    - Set *force_reclone* to ``True`` (or pass ``--no-cache`` on the CLI) to
      discard the cached clone and start fresh.
    """
    if not force_reclone and repo_path in _repo_cache:
        return _repo_cache[repo_path]

    try:
        import git
    except ImportError as exc:
        raise ImportError(
            "gitpython is required for git skills. "
            "Install it with: pip install gitpython"
        ) from exc

    if repo_path.startswith(("http://", "https://", "git@", "ssh://")):
        clone_dir = _remote_clone_dir(repo_path)

        if force_reclone and clone_dir.exists():
            shutil.rmtree(clone_dir)

        needs_clone = not clone_dir.exists()

        if not needs_clone:
            try:
                repo = git.Repo(clone_dir)
            except (git.InvalidGitRepositoryError, git.NoSuchPathError):
                # Corrupted cache — wipe and fall through to a fresh clone
                shutil.rmtree(clone_dir, ignore_errors=True)
                needs_clone = True
            else:
                # Update the cached clone so callers see current data
                try:
                    for remote in repo.remotes:
                        remote.fetch(prune=True)
                except Exception as fetch_err:
                    print(
                        f"[git-newsletter] Warning: fetch failed for {repo_path!r}: "
                        f"{fetch_err}. Using cached data.",
                        file=sys.stderr,
                    )

        if needs_clone:
            # Handles both: directory never existed, and recovery from a
            # corrupted cache that was wiped above.
            clone_dir.mkdir(parents=True, exist_ok=True)
            repo = git.Repo.clone_from(repo_path, clone_dir, no_single_branch=True)

        _repo_cache[repo_path] = repo
    else:
        repo = git.Repo(repo_path, search_parent_directories=True)
        _repo_cache[repo_path] = repo

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


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

_ACTIONS = ("recent-commits", "branch-activity", "stale-branches", "merged-branches", "commit-diff", "git-cmd")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a single git skill function and print JSON to stdout.\n\n"
            "Actions:\n"
            "  recent-commits   Commits on a branch within the last N days.\n"
            "  branch-activity  Activity summary for all branches.\n"
            "  stale-branches   Branches with no commits in the last N days.\n"
            "  merged-branches  Branches merged into target within the last N days.\n"
            "  commit-diff      Full unified diff for a single commit SHA.\n"
            "  git-cmd          Run an arbitrary git subcommand and return its output\n"
            "                   as JSON ({\"output\": \"...\"}).  Two benefits over a raw\n"
            "                   git call: (1) output is JSON like every other action, and\n"
            "                   (2) if --repo is a URL the repository is auto-cloned.\n"
            "                   Provide the subcommand + args via --git-args.\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=_ACTIONS,
        metavar="ACTION",
        help="Skill to run: " + ", ".join(_ACTIONS),
    )
    parser.add_argument("--repo", required=True, help="Local path or remote URL of the repository")
    parser.add_argument("--branch", default="main", help="Branch name (default: main)")
    parser.add_argument("--target-branch", default="main", help="Target branch for merged-branches (default: main)")
    parser.add_argument("--days", type=int, default=7, help="Look-back window in days (default: 7)")
    parser.add_argument("--stale-after", type=int, default=30, help="Days before a branch is considered stale (default: 30)")
    parser.add_argument("--sha", default=None, help="Commit SHA for commit-diff action")
    parser.add_argument(
        "--git-args",
        default=None,
        help=(
            "Git subcommand and arguments for the git-cmd action, parsed with "
            "shell-like quoting rules (e.g. 'log --oneline -5' or "
            "'log --grep=\"fix bug\"'). "
            "Wrap the whole value in quotes when calling from the shell."
        ),
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        default=False,
        help=(
            "Discard any existing cached clone for --repo and re-clone from "
            "scratch.  Only meaningful for remote URLs; ignored for local paths."
        ),
    )
    return parser


def _main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        # Pre-open the repo so --no-cache is honoured before any skill function
        # calls _open_repo internally (they all use the module-level cache, so
        # the force_reclone only needs to happen once here).
        _open_repo(args.repo, force_reclone=args.no_cache)

        if args.action == "recent-commits":
            result: Any = get_recent_commits(args.repo, args.branch, args.days)
        elif args.action == "branch-activity":
            result = get_branch_activity(args.repo, args.days)
        elif args.action == "stale-branches":
            result = get_stale_branches(args.repo, args.stale_after)
        elif args.action == "merged-branches":
            result = get_merged_branches(args.repo, args.target_branch, args.days)
        elif args.action == "commit-diff":
            if not args.sha:
                parser.error("--sha is required for the commit-diff action")
            result = get_commit_diff(args.repo, args.sha)
        else:  # git-cmd
            if not args.git_args:
                parser.error("--git-args is required for the git-cmd action")
            repo = _open_repo(args.repo)
            git_argv = shlex.split(args.git_args)
            output = repo.git.execute(["git"] + git_argv)
            result = {"output": output}
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _main()
