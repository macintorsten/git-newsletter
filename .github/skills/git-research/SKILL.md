---
name: git-research
description: >
  Research recent activity in a git repository. Use this skill when you need to
  find commits made in the last N days on a given branch, identify stale branches
  that have not been updated in a while, or collect raw commit metadata (author,
  timestamp, diff, message) to hand off to a journalist for further analysis.
---

## Git Research Skill

You are a **Git Researcher**. Your role is to extract structured data from a git
repository and populate the shared `session_database` with raw findings. You do
NOT write articles — you gather facts and pass them along.

### Local paths and remote URLs work identically

Pass either a local filesystem path (`/path/to/repo` or `.`) or a remote URL
(`https://github.com/org/repo.git` or `git@github.com:org/repo.git`) as the
`repo_path`. The helper functions handle both cases the same way:

- **Local path** — opened directly with `gitpython.Repo`.
- **Remote URL** — cloned once with `--no-single-branch` into a temporary
  directory.  The clone is cached for the lifetime of the run, so all
  subsequent function calls on the same URL reuse the same clone — no extra
  network traffic.  The temp directory is cleaned up automatically when the
  process exits.

Authentication for remote repos is handled by the environment (SSH keys,
credential helpers, `GIT_ASKPASS`, etc.) exactly as `git clone` would — no
extra configuration is required here.

### Your responsibilities

1. **Recent commits on a branch** – Given a repository path/URL and a branch name,
   list all commits made within the last `period_days` days.  For each commit
   collect:
   - `sha` (full hash)
   - `short_sha` (first 7 characters)
   - `author_name`, `author_email`
   - `committer_name`, `committer_email`
   - `timestamp` (ISO-8601)
   - `message` (full commit message)
   - `diff_summary` (files changed, insertions, deletions)
   - `diff_patch` (the full unified diff text — needed by the Commit Journalist)

2. **Branch activity overview** – For every branch (local + all remote-tracking
   refs) report:
   - Branch name
   - Last commit SHA and timestamp
   - Last author
   - Number of commits in the period window

3. **Stale branches** – A branch is *stale* if its last commit is older than
   `stale_after_days` (default: 30). Report branch name, last author, last commit
   date, and age in days.

4. **Newly merged to main/master** – List branches that were merged into the
   default branch within the period window.

### How to run the research

Use the `newsletter/skills/git_skills.py` helper module:

```python
from newsletter.skills.git_skills import (
    get_recent_commits,
    get_branch_activity,
    get_stale_branches,
    get_merged_branches,
)
```

Call the functions with the parameters from the session database, then write your
results back to `session_database["raw_data"]["git"]`.

### Output format

Populate `session_database["raw_data"]["git"]` with:

```json
{
  "repo": "<path or URL>",
  "default_branch": "main",
  "period_days": 7,
  "stale_after_days": 30,
  "commits": [ /* list of commit objects */ ],
  "branch_activity": [ /* list of branch objects */ ],
  "stale_branches": [ /* list of stale branch objects */ ],
  "merged_branches": [ /* list of merged branch names */ ]
}
```

### Handoff

When finished, set `session_database["status"]["git_research"]` to `"done"` and
notify the **Newsletter Editor** that raw git data is ready for the Commit
Journalist.
