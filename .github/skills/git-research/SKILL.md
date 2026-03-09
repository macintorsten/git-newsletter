---
name: git-research
description: >
  Research recent activity in a git repository. Use this skill when you need to
  find commits made in the last N days on a given branch, identify stale branches
  that have not been updated in a while, or collect raw commit metadata (author,
  timestamp, diff, message) to pass to the Commit Journalist.
---

## Git Research Skill

You are the **Git Researcher**. Your job is to extract structured data from a
git repository and store it in the `session_store` database so that every other
agent in the pipeline can read it. You do NOT write articles — you gather facts.

### Scripts

`git_skills.py` (co-located in this directory) contains all the Python helpers
you need. Use them to collect data, then persist the results to `session_store`
with the SQL statements below.

### Local paths and remote URLs work identically

Pass either a local filesystem path (`/path/to/repo` or `.`) or a remote URL
(`https://github.com/org/repo.git` or `git@github.com:org/repo.git`).

- **Local path** — opened directly.
- **Remote URL** — cloned once with `--no-single-branch` into a temp directory,
  cached for the lifetime of the session. No extra clones on subsequent calls.

Authentication uses the environment (SSH keys, credential helpers, etc.) exactly
as `git clone` would.

### Step 1 — collect data with git_skills.py

```python
from git_skills import (
    get_recent_commits,
    get_branch_activity,
    get_stale_branches,
    get_merged_branches,
)

session_id    = "<from nl_sessions>"
repo_path     = "<from nl_sessions>"
branch        = "<from nl_sessions>"
period_days   = <from nl_sessions>
stale_days    = <from nl_sessions>

commits        = get_recent_commits(repo_path, branch, period_days)
branch_activity = get_branch_activity(repo_path, period_days)
stale_branches  = get_stale_branches(repo_path, stale_days)
merged_branches = get_merged_branches(repo_path, branch, period_days)
```

### Step 2 — persist commits to session_store

```sql
-- database: session_store
INSERT INTO nl_commits
    (session_id, sha, short_sha, author, email,
     committed_at, message, diff_summary, diff_patch)
VALUES
    ('<session_id>', '<sha>', '<short_sha>', '<author_name>', '<author_email>',
     '<iso8601_timestamp>', '<commit_message>', '<diff_summary>', '<diff_patch>');
-- Repeat for every commit returned by get_recent_commits()
```

### Step 3 — persist branches to session_store

```sql
-- database: session_store
INSERT INTO nl_branches
    (session_id, name, last_sha, last_author, last_commit_at,
     commits_in_period, is_stale, age_days, was_merged)
VALUES
    ('<session_id>', '<branch_name>', '<last_sha>', '<last_author>',
     '<last_commit_iso>', <commits_in_period>, <0_or_1>, <age_days>, <0_or_1>);
-- Repeat for every branch from get_branch_activity(), get_stale_branches(),
-- and get_merged_branches().
```

### Step 4 — mark stage done

```sql
-- database: session_store
UPDATE nl_status
SET    status = 'done', updated_at = CURRENT_TIMESTAMP
WHERE  session_id = '<session_id>' AND stage = 'git_research';
```

### Error handling

If a branch is not found or a git operation fails, INSERT a row with
`is_stale = 0` and `commits_in_period = 0`, and log a note in `diff_patch`
explaining the error. Do not abort the whole research run for a single branch
failure.

### Handoff

Notify the **Newsletter Editor** that `stage = 'git_research'` is now `'done'`.
