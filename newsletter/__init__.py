"""
newsletter – git-newsletter editor package.

The package contains:
  - sources/       : Pluggable data-source adapters (git, future: GitLab, Jira…)
  - skills/        : Thin shims re-exporting from .github/skills/*/
  - agents/        : Agent system-prompt templates (with session_store SQL schema)
  - orchestrator.py: CLI pipeline – collects git data, renders newsletter template
  - cli.py         : `python -m newsletter` entry point

Agent state (for Copilot agent workflows) is persisted to Copilot's native
`session_store` via SQL — see .github/copilot/agents/ and .github/skills/.
"""
