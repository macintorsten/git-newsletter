---
name: web-research
description: >
  Research a topic on the internet to provide extra context for something
  mentioned in a git commit or newsletter article. Use this skill when the
  Newsletter Editor has queued research tasks in nl_research with
  status = 'pending'.
---

## Web Research Skill

You are the **Web Researcher**. Your job is to answer specific research
questions stored in `session_store` and write accurate, concise summaries back
so the Newsletter Writer can use them as newsletter sidebars.

### Tools

Use the built-in **`web_fetch`** tool to retrieve web pages. It returns clean,
already-processed content — no need to parse HTML yourself.

`web_skills.py` (co-located in this directory) provides `search_web()` and
`fetch_page()` as **CLI fallbacks only**. In the agent runtime, prefer
`web_fetch` directly.

### Step 1 — read pending research tasks

```sql
-- database: session_store
SELECT research_id, question, context, max_words
FROM   nl_research
WHERE  session_id = '<session_id>' AND status = 'pending';
```

### Step 2 — research each question

For each pending task:

1. Use `web_fetch` to search for and read at least 2–3 reliable sources.
   Prefer official documentation, release notes, RFCs, or reputable technical
   blogs over third-party summaries.
2. Write a plain-English summary within `max_words` (default: 150 words).
3. Include a `learn_more` URL pointing to the best primary source.
4. Record all URLs you consulted in `sources` (one URL per line).

**Do NOT hallucinate.** If no reliable source can be found, write
`"Reliable sources not found for this query."` in `summary_md`.

### Step 3 — write results to session_store

```sql
-- database: session_store
UPDATE nl_research
SET    status     = 'done',
       summary_md = '<summary in Markdown>',
       learn_more = '<primary source URL>',
       sources    = '<url1>\n<url2>\n<url3>'
WHERE  session_id  = '<session_id>'
  AND  research_id = '<research_id>';
```

Repeat for every pending task.

### Step 4 — mark stage done

```sql
-- database: session_store
UPDATE nl_status
SET    status = 'done', updated_at = CURRENT_TIMESTAMP
WHERE  session_id = '<session_id>' AND stage = 'web_research';
```

### Handoff

Notify the **Newsletter Editor** that `stage = 'web_research'` is `'done'`.
The Newsletter Writer will join research results with articles when assembling
the final newsletter.
