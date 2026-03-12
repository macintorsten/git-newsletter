---
name: commit-analysis
description: >
  Fetch recent git data and transform it into clear, human-readable newsletter
  articles in a single pass. Use this skill when the newsletter-editor hands
  off to the commit-analyst agent after initialising the session.
---

## Commit Analysis Skill

You are the **Commit Analyst**. In a single pass you collect raw git data
from the repository **and** turn it into short, engaging newsletter articles.

Authority and scope:

- This skill is the authoritative source for the `commit-analyst` execution
  workflow.
- Keep the matching agent file focused on role, handoff contract, and done
  criteria.
- Keep detailed SQL, tool usage, heuristics, and persistence rules here.

Idempotency contract:

- A rerun with the same `session_id` must be safe.
- Persist commits, branches, and articles with conflict-safe writes so logical
  rows are updated in place instead of duplicated.
- Mark `commit_analysis` as `done` only after every required write succeeds.
- If a required write fails, do not mark the stage `done`; set it to `failed`
  and return control to the editor.

### Phase 1 — collect git data with git_skills.py

`git_skills.py` lives in this same skill directory,
`.github/skills/commit-analysis/`. Use it to collect data, then persist the results to
`session_store`.

`git_skills.py` carries PEP 723 inline metadata which documents its
dependencies.  Run it with an activated venv (`python git_skills.py …`) or
with `uv run` (`uv run git_skills.py …`) — both work equally well.

#### Step 1 — read session parameters

```sql
-- database: session_store
SELECT repo, branch, period_days, stale_after_days
FROM   nl_sessions WHERE session_id = '<session_id>';
```

#### Step 2 — run the git helpers

Run each command and parse the JSON output.

With an activated venv or system Python:

```bash
python .github/skills/commit-analysis/git_skills.py \
    --action recent-commits --repo <repo_path> --branch <branch> --days <period_days>

python .github/skills/commit-analysis/git_skills.py \
    --action branch-activity --repo <repo_path> --days <period_days>

python .github/skills/commit-analysis/git_skills.py \
    --action stale-branches --repo <repo_path> --stale-after <stale_after_days>

python .github/skills/commit-analysis/git_skills.py \
    --action merged-branches --repo <repo_path> --target-branch <branch> --days <period_days>
```

Alternatively, using `uv run` (installs `gitpython` automatically, no venv needed):

```bash
uv run .github/skills/commit-analysis/git_skills.py \
    --action recent-commits --repo <repo_path> --branch <branch> --days <period_days>

uv run .github/skills/commit-analysis/git_skills.py \
    --action branch-activity --repo <repo_path> --days <period_days>

uv run .github/skills/commit-analysis/git_skills.py \
    --action stale-branches --repo <repo_path> --stale-after <stale_after_days>

uv run .github/skills/commit-analysis/git_skills.py \
    --action merged-branches --repo <repo_path> --target-branch <branch> --days <period_days>
```

Each command prints a JSON array to stdout. Parse and store the result.

If you need a git operation that is not covered by the actions above, use the
**`git-cmd` escape hatch** — it accepts any git subcommand and its flags via
`--git-args` and returns the raw text output wrapped in a JSON object
(`{"output": "…"}`).  Authentication works identically to the named actions
because `git-cmd` uses the same underlying repo handle, which in turn calls the
real `git` binary.  This means SSH keys, credential helpers, `GIT_ASKPASS`,
`GITHUB_TOKEN`, and any other mechanism that works with the `git` CLI also works
here.

```bash
# Arbitrary git operation — escape hatch for anything not covered above:
python .github/skills/commit-analysis/git_skills.py \
    --action git-cmd --repo <repo_path> --git-args "shortlog -sn HEAD"

python .github/skills/commit-analysis/git_skills.py \
    --action git-cmd --repo <repo_path> --git-args "log --oneline --graph -10"
```

> **Authentication note:** GitPython delegates all network operations to the
> real `git` binary, so authentication behaves identically to running `git`
> directly on the command line.  SSH keys, `~/.netrc`, credential helpers,
> `GIT_ASKPASS`, and `GITHUB_TOKEN`-backed credential stores all work as
> expected.  There is no separate auth configuration required.

Alternatively, when already running inside a Python process that has
`gitpython` installed, import the functions directly:

```python
from git_skills import (
    get_recent_commits,
    get_branch_activity,
    get_stale_branches,
    get_merged_branches,
)

commits         = get_recent_commits(repo_path, branch, period_days)
branch_activity = get_branch_activity(repo_path, period_days)
stale_branches  = get_stale_branches(repo_path, stale_days)
merged_branches = get_merged_branches(repo_path, branch, period_days)
```

Supports both local filesystem paths and remote URLs. Remote URLs are cloned
once and cached; authentication uses the environment (SSH keys, credential
helpers, `GITHUB_TOKEN`, etc.) — identical to the `git` CLI.

#### Step 3 — persist commits

```sql
-- database: session_store
INSERT INTO nl_commits
    (session_id, sha, short_sha, author, email,
     committed_at, message, diff_summary, diff_patch)
VALUES
    ('<session_id>', '<sha>', '<short_sha>', '<author_name>', '<author_email>',
   '<iso8601_timestamp>', '<commit_message>', '<diff_summary>', '<diff_patch>')
ON CONFLICT(session_id, sha) DO UPDATE SET
  short_sha = excluded.short_sha,
  author = excluded.author,
  email = excluded.email,
  committed_at = excluded.committed_at,
  message = excluded.message,
  diff_summary = excluded.diff_summary,
  diff_patch = excluded.diff_patch;
-- Repeat for every commit returned by get_recent_commits()
```

#### Step 4 — persist branches

```sql
-- database: session_store
INSERT INTO nl_branches
    (session_id, name, last_sha, last_author, last_commit_at,
     commits_in_period, is_stale, age_days, was_merged)
VALUES
    ('<session_id>', '<branch_name>', '<last_sha>', '<last_author>',
   '<last_commit_iso>', <commits_in_period>, <0_or_1>, <age_days>, <0_or_1>)
ON CONFLICT(session_id, name) DO UPDATE SET
  last_sha = excluded.last_sha,
  last_author = excluded.last_author,
  last_commit_at = excluded.last_commit_at,
  commits_in_period = excluded.commits_in_period,
  is_stale = excluded.is_stale,
  age_days = excluded.age_days,
  was_merged = excluded.was_merged;
-- Repeat for every branch from get_branch_activity(), get_stale_branches(),
-- and get_merged_branches()
```

#### Error handling

If a branch is not found or a git operation fails, write a fallback branch row
with `is_stale = 0` and `commits_in_period = 0`, and leave unavailable branch
fields empty. Keep the collection pass moving when the git helper fails for a
single branch, but treat database write failures as terminal for the stage.

---

### Phase 2 — write articles

#### Step 5 — group related commits

Decide which commits belong together (same feature, same fix, same author
working on a coherent change). You decide the grouping. Good heuristics:

- Same feature branch of origin → one article
- Multiple small tidy-up commits from one author → one "Housekeeping 🧹" entry
- A single large, impactful commit → its own article
- Dependency bumps → one "📦 Dependency updates" entry (brief)

#### Step 6 — write an article for each group

For each group, produce a short article (150–300 words) covering:
- **What changed** — plain English description
- **Why it matters** — motivation from the commit message and diff
- **Technical details** — files, functions, systems involved; explain any
  non-obvious term a general developer might not know
- **Who did it** — credit author(s) by name

Use emojis 🎉 to lighten the tone. Tone: friendly, educational, encouraging.

#### Step 7 — flag deep-dive candidates

If a commit looks particularly significant (new feature, major refactor,
performance win, security fix), set `deep_dive = 1` and provide a clear
`deep_dive_q` question that the Web Researcher can answer.

#### Step 8 — write articles to session_store

Generate a unique `article_id` for each group (e.g. `art-001`, `art-002`).

```sql
-- database: session_store
INSERT INTO nl_articles
    (session_id, article_id, commit_shas, title,
     body_markdown, authors, deep_dive, deep_dive_q)
VALUES
    ('<session_id>', '<article_id>', '<sha1,sha2,...>', '<Friendly Title>',
     '<full article in Markdown>', '<Author One, Author Two>',
   <0_or_1>, '<deep dive question or NULL>')
ON CONFLICT(session_id, article_id) DO UPDATE SET
  commit_shas = excluded.commit_shas,
  title = excluded.title,
  body_markdown = excluded.body_markdown,
  authors = excluded.authors,
  deep_dive = excluded.deep_dive,
  deep_dive_q = excluded.deep_dive_q;
-- Repeat for every article group.
```

#### Step 9 — mark stage done

Only run this update after every required commit, branch, and article write has
succeeded for the current `session_id`.

```sql
-- database: session_store
UPDATE nl_status
SET    status = 'done', updated_at = CURRENT_TIMESTAMP
WHERE  session_id = '<session_id>' AND stage = 'commit_analysis';
```

### Handoff

Use the **↩️ Return to editor — commit analysis done** handoff button (or
notify the **Newsletter Editor** directly) that `stage = 'commit_analysis'`
is now `'done'`. The editor will query `nl_articles`, make editorial
selections, and optionally queue deep-dive research tasks.
