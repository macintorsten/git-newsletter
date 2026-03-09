# Newsletter Prompt Template

Purpose: Single reusable template for direct `newsletter-editor` prompts.
Use this file by referencing or pasting it in your Copilot CLI prompt.

## Core inputs

- repo: <required local path or remote URL>
- branch: <optional, default main>
- period_days: <optional, default 7>
- title: <optional newsletter title override>
- output_path: <optional, default newsletter_output.md>

## Minimal prompt block

Inputs:
- repo: <repo>
- branch: <branch>
- period_days: <period_days>
- title: <title>
- output_path: <output_path>

Optional additions:
- Include profile prompt file: <path>
- Extra instructions: <text>

## Profile metadata

- profile_name: <short name>
- repository: <https://github.com/owner/repo.git>
- branch: <main|master|other>
- period_days: <7|14|30|...>
- output_path: <newsletter_output.md>
- title_style: <how title should be phrased>

## Editorial focus

- Primary audience: <team/personas>
- Prioritize: <features/fixes/perf/security/release notes>
- De-emphasize: <chores/noise>
- Deep-dive policy: <0-3 topics, what qualifies>

## Section preferences

- Include sections: shipped, bugs, performance, docs, release readiness, stale branches
- Keep section order: <custom order or default>
- Keep summary length: <short|medium|long>

## Tone and format

- Tone: warm, practical, educational
- Explain jargon on first use
- Use emojis in headings and highlights
- Mention contributor names when possible

## Constraints

- If commit volume is low, widen context with notable PRs/issues
- If repository is less active, use a longer period_days
- If no meaningful changes exist, produce a short status update with recommendations
