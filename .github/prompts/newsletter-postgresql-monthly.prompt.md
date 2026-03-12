---
description: "Generate a PostgreSQL monthly newsletter markdown using the bundled example profile"
name: "Newsletter PostgreSQL Monthly"
argument-hint: "[optional overrides: repo=..., branch=..., period_days=..., title=..., output_path=...]"
agent: "newsletter-editor"
---

Use profile prompt file [example-postgresql-monthly.prompt.md](./profiles/examples/example-postgresql-monthly.prompt.md).

Default inputs:
- repo: https://github.com/postgres/postgres.git
- branch: master
- period_days: 30
- output_path: postgresql-monthly-newsletter.md

If the user supplied extra text after this slash command, treat it as optional overrides to those defaults.

Return only the final newsletter markdown.