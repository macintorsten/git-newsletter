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

Authority and scope:

- This skill is the authoritative source for the `web-researcher` execution
  workflow.
- Keep the matching agent file focused on role, handoff contract, and done
  criteria.
- Keep detailed source rules, SQL updates, and persistence behavior here.

Execution input contract:

- The editor must pass an explicit `research_id` set for the assigned shard,
  plus a shard token for traceability.
- Process only the assigned `research_id` values for the current `session_id`.
- If the handoff does not include an explicit `research_id` set, stop and
  return a concise error instead of claiming the whole queue.

Idempotency contract:

- A rerun with the same `session_id` must update the assigned research rows in
  place.
- Do not insert new research rows in this skill; only update the rows selected
  in Step 1.
- Mark `web_research` as `done` only after every required row update succeeds.
- If a required row update fails, do not mark the stage `done`; set it to
  `failed` and return control to the editor.

### Tools

Use the built-in **`web_fetch`** tool to retrieve web pages. It returns clean,
already-processed content — no need to parse HTML yourself.

### Step 1 — read the assigned research shard

```sql
-- database: session_store
SELECT research_id, question, context, max_words
FROM   nl_research
WHERE  session_id = '<session_id>'
  AND  status = 'pending'
  AND  research_id IN ('<id1>', '<id2>');
```

The `IN (...)` list must match the explicit `research_id` values passed by the
editor for this shard.

### Step 2 — research each question

For each assigned task:

1. Use `web_fetch` to search for and read at least 2–3 reliable sources.
   Prefer official documentation, release notes, RFCs, or reputable technical
   blogs over third-party summaries.
2. Write a plain-English summary within `max_words` (default: 150 words).
3. Include a `learn_more` URL pointing to the best primary source.
4. Record all URLs you consulted in `sources` (one URL per line).

**Do NOT hallucinate.** If no reliable source can be found, write
`"Reliable sources not found for this query."` in `summary_md`.

### Step 3 — write results to session_store

Update each pre-existing research row by `research_id`. This keeps reruns safe
with the same `session_id` and prevents duplicate research records.

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

Repeat for every assigned task.

### Step 4 — mark stage done

Only run the stage-completion update after every assigned research row from
Step 1 has been updated successfully for the current `session_id` and there are
no remaining `pending` rows anywhere in the session.

Check for fan-in completion first:

```sql
-- database: session_store
SELECT COUNT(*) AS pending_count
FROM   nl_research
WHERE  session_id = '<session_id>' AND status = 'pending';
```

If `pending_count > 0`, do not mark the stage `done` yet. Return control to the
editor after finishing the assigned shard.

```sql
-- database: session_store
UPDATE nl_status
SET    status = 'done', updated_at = CURRENT_TIMESTAMP
WHERE  session_id = '<session_id>' AND stage = 'web_research';
```

### Handoff

Notify the **Newsletter Editor** that the assigned shard is complete. If this
worker also observed zero pending rows and marked `stage = 'web_research'` as
`'done'`, say so explicitly. The Newsletter Writer will join research results
with articles when assembling the final newsletter.
