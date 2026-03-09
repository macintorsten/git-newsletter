"""
newsletter – git-newsletter editor package.

The package contains:
  - models.py      : Pydantic data models and session database schema
  - session_db.py  : Shared JSON session state manager
  - sources/       : Pluggable data-source adapters (git, future: GitLab, Jira…)
  - skills/        : Callable skill implementations used by agents
  - agents/        : Agent prompt templates and role helpers
  - orchestrator.py: Main pipeline that wires sources → skills → agents
  - cli.py         : `python -m newsletter` entry point
"""
