# Agent Interaction Flow

This document shows how the newsletter agents hand off work to each other.
Each agent is defined as a `.agent.md` file in this directory.

## Pipeline Overview

```
User invokes @newsletter-editor
         │
         ▼
┌─────────────────────────────┐
│      newsletter-editor      │  initialises session_store schema,
│      (orchestrator)         │  session_id, and nl_status rows
└──────────────┬──────────────┘
               │
               │  STEP 1 ── handoff ──────────────────────────────────────┐
               │  "🔍 Analyse commits & write articles"                    │
               │                                                           ▼
               │                               ┌──────────────────────────────────┐
               │                               │        commit-analyst            │
               │                               │  Phase 1: run git_skills.py,     │
               │                               │    INSERT nl_commits +           │
               │                               │    nl_branches                   │
               │                               │  Phase 2: group commits,         │
               │                               │    write & INSERT nl_articles    │
               │                               │  Marks commit_analysis = done    │
               │                               └──────────────┬───────────────────┘
               │                                              │
               │  ◄────────────── handoff back ───────────────┘
               │  "↩️ Return to editor — commit analysis done"
               │
               │  EDITORIAL REVIEW (editor selects articles,
               │  optionally queues 0–3 deep-dive research tasks)
               │
               ├─── deep dives queued? ──────────────────────────────────────┐
               │                                                  yes         │
               │                                                              │
               │  STEP 2 (optional) ── handoff ──────────────────────────────▼
               │  "🌐 Research deep-dive topics"       ┌───────────────────────────────┐
               │                                       │       web-researcher          │
               │                                       │  fetches web pages,           │
               │                                       │  writes summaries to          │
               │                                       │  nl_research rows             │
               │                                       │  Marks web_research = done    │
               │                                       └──────────────┬────────────────┘
               │                                                      │
               │  ◄─────────────────── handoff back ──────────────────┘
               │  "↩️ Return to editor — web research done"
               │
               │  STEP 3 ── handoff ──────────────────────────────────────┐
               │  "✍️ Write the newsletter"                                │
               │                                                           ▼
               │                               ┌──────────────────────────────────┐
               │                               │      newsletter-writer           │
               │                               │  reads nl_articles (selected),   │
               │                               │  nl_research (done),             │
               │                               │  nl_branches                     │
               │                               │  assembles Markdown file         │
               │                               │  Marks writing = done            │
               │                               └──────────────┬───────────────────┘
               │                                              │
               │  ◄────────────── handoff back ───────────────┘
               │  "↩️ Return to editor — newsletter written"
               │
               ▼
┌─────────────────────────────┐
│      newsletter-editor      │  reads nl_output, confirms file
│      (finalise)             │  path and content to the user
└─────────────────────────────┘
               │
               ▼
        newsletter_output.md
```

Parallelism note: when multiple deep-dive rows are queued in `nl_research`,
the `web-researcher` may process those rows concurrently before marking
`web_research` as done.

## State machine (`nl_status`)

All stages are tracked in `session_store`:

| Stage             | Set by          | Meaning                            |
|-------------------|-----------------|------------------------------------|
| `commit_analysis` | commit-analyst  | Git data collected + articles done |
| `web_research`    | web-researcher  | Deep-dive summaries written        |
| `writing`         | newsletter-writer | Final Markdown assembled         |

Each stage follows the lifecycle: `pending` → `done` (or `failed`).

## Handoff summary

| From                | To                  | Trigger                              |
|---------------------|---------------------|--------------------------------------|
| newsletter-editor   | commit-analyst      | Pipeline start                       |
| commit-analyst      | newsletter-editor   | `commit_analysis` = done             |
| newsletter-editor   | web-researcher      | Deep-dive tasks queued in nl_research |
| web-researcher      | newsletter-editor   | `web_research` = done                |
| newsletter-editor   | newsletter-writer   | Articles selected, research done     |
| newsletter-writer   | newsletter-editor   | `writing` = done                     |

## Session store schema

```
nl_sessions   ← one row per pipeline run (repo, branch, period)
nl_commits    ← raw commit data (collected by commit-analyst, phase 1)
nl_branches   ← branch activity and stale-branch data
nl_articles   ← newsletter articles (written by commit-analyst, phase 2)
nl_research   ← deep-dive research tasks and results
nl_output     ← final assembled newsletter Markdown
nl_status     ← stage progress flags (commit_analysis | web_research | writing)
```
