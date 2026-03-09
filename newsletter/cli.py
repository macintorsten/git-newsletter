"""
CLI entry point for the newsletter editor.

Usage:
    python -m newsletter [OPTIONS]

Examples:
    # Generate a newsletter for the last 7 days on 'main'
    python -m newsletter --repo /path/to/your/repo

    # Specify branch, look-back window, and output file
    python -m newsletter \\
        --repo /path/to/your/repo \\
        --branch develop \\
        --days 14 \\
        --output my_newsletter.md

    # Use a remote repository URL
    python -m newsletter --repo https://github.com/org/repo.git --branch main

    # Custom stale-branch threshold
    python -m newsletter --repo . --stale-days 60
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m newsletter",
        description=(
            "git-newsletter editor — generate a Markdown newsletter from "
            "recent git activity."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--repo",
        required=True,
        metavar="PATH_OR_URL",
        help="Local path or remote URL of the git repository.",
    )
    parser.add_argument(
        "--branch",
        default="main",
        metavar="BRANCH",
        help="Branch to report on (default: main).",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        metavar="N",
        help="Number of days to look back for commits (default: 7).",
    )
    parser.add_argument(
        "--stale-days",
        type=int,
        default=30,
        dest="stale_days",
        metavar="N",
        help="Days of inactivity before a branch is considered stale (default: 30).",
    )
    parser.add_argument(
        "--output",
        default="newsletter_output.md",
        metavar="FILE",
        help="Path for the generated Markdown newsletter (default: newsletter_output.md).",
    )
    parser.add_argument(
        "--db",
        default=None,
        metavar="FILE",
        dest="db_path",
        help=(
            "Path for the session database JSON file "
            "(default: newsletter_session.json)."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        from newsletter.orchestrator import run
    except ImportError as exc:
        print(f"Error: could not import newsletter package: {exc}", file=sys.stderr)
        return 1

    print(
        f"📰 git-newsletter editor starting...\n"
        f"   repo   : {args.repo}\n"
        f"   branch : {args.branch}\n"
        f"   period : last {args.days} day(s)\n"
        f"   stale  : >{args.stale_days} days\n"
        f"   output : {args.output}\n"
    )

    try:
        db = run(
            repo_path=args.repo,
            branch=args.branch,
            period_days=args.days,
            stale_after_days=args.stale_days,
            output_path=args.output,
            db_path=args.db_path,
        )
    except Exception as exc:
        print(f"❌ Pipeline failed: {exc}", file=sys.stderr)
        return 1

    out_path = Path(db.output.output_path)
    if out_path.exists():
        print(f"✅ Newsletter written to: {out_path.resolve()}")
    else:
        print("⚠️  Pipeline completed but output file was not found.", file=sys.stderr)

    if db.logs:
        print("\n📋 Pipeline log:")
        for entry in db.logs:
            print(f"   {entry}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
