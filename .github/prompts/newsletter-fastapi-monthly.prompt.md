---
description: "Generate a FastAPI monthly newsletter markdown using the bundled example profile"
name: "Newsletter FastAPI Monthly"
argument-hint: "[optional overrides: repo=..., branch=..., period_days=..., title=..., output_path=...]"
agent: "newsletter-editor"
---

Use profile prompt file [example-fastapi-monthly.prompt.md](./profiles/examples/example-fastapi-monthly.prompt.md).

Default inputs:
- repo: https://github.com/fastapi/fastapi.git
- branch: master
- period_days: 30
- output_path: fastapi-monthly-newsletter.md

If the user supplied extra text after this slash command, treat it as optional overrides to those defaults.

Return only the final newsletter markdown.