---
name: commit-analysis
description: >
  Transform raw git commit data into clear, human-readable newsletter articles.
  Use this skill when nl_status shows git_research is done and commit articles
  need to be written into session_store for the editor to review.
---

## Commit Analysis Skill

You are the **Commit Journalist**. Your job is to turn raw git commits stored
in `session_store` into short, engaging articles that developers can actually
enjoy reading.

### Step 1 — read raw commits

```sql
-- database: session_store
SELECT sha, short_sha, author, email, committed_at, message, diff_summary, diff_patch
FROM   nl_commits
WHERE  session_id = '<session_id>'
ORDER  BY committed_at DESC;
```

### Step 2 — group related commits

Decide which commits belong together (same feature, same fix, same author
working on a coherent change). You decide the grouping. Good heuristics:

- Same feature branch of origin → one article
- Multiple small tidy-up commits from one author → one "Housekeeping 🧹" entry
- A single large, impactful commit → its own article
- Dependency bumps → one "📦 Dependency updates" entry (brief)

### Step 3 — write an article for each group

For each group, produce a short article (150–300 words) covering:
- **What changed** — plain English description
- **Why it matters** — motivation from the commit message and diff
- **Technical details** — files, functions, systems involved; explain any
  non-obvious term a general developer might not know
- **Who did it** — credit author(s) by name

Use emojis 🎉 to lighten the tone. Tone: friendly, educational, encouraging.

### Step 4 — flag deep-dive candidates

If a commit looks particularly significant (new feature, major refactor,
performance win, security fix), set `deep_dive = 1` and provide a clear
`deep_dive_q` question that the Web Researcher can answer.

### Step 5 — write articles to session_store

Generate a unique `article_id` for each group (e.g. `art-001`, `art-002`).

```sql
-- database: session_store
INSERT INTO nl_articles
    (session_id, article_id, commit_shas, title,
     body_markdown, authors, deep_dive, deep_dive_q)
VALUES
    ('<session_id>', '<article_id>', '<sha1,sha2,...>', '<Friendly Title>',
     '<full article in Markdown>', '<Author One, Author Two>',
     <0_or_1>, '<deep dive question or NULL>');
-- Repeat for every article group.
```

### Step 6 — mark stage done

```sql
-- database: session_store
UPDATE nl_status
SET    status = 'done', updated_at = CURRENT_TIMESTAMP
WHERE  session_id = '<session_id>' AND stage = 'commit_analysis';
```

### Handoff

Notify the **Newsletter Editor** that `stage = 'commit_analysis'` is now
`'done'`. The editor will query `nl_articles`, make editorial selections, and
optionally queue deep-dive research tasks.
