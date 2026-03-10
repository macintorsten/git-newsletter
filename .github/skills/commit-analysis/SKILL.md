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

#### Step 1 — read session parameters

```sql
-- database: session_store
SELECT repo, branch, period_days, stale_after_days
FROM   nl_sessions WHERE session_id = '<session_id>';
```

#### Step 2 — run the git helpers

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
helpers, etc.).

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
