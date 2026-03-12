---
description: "Generate a Flask monthly newsletter markdown using the bundled example profile"
name: "Newsletter Flask Monthly"
argument-hint: "[optional overrides: repo=..., branch=..., period_days=..., title=..., output_path=...]"
agent: "newsletter-editor"
---

Use profile prompt file [example-flask-monthly.prompt.md](./profiles/examples/example-flask-monthly.prompt.md).

Default inputs:
- repo: https://github.com/pallets/flask.git
- branch: main
- period_days: 30
- output_path: flask-monthly-newsletter.md

If the user supplied extra text after this slash command, treat it as optional overrides to those defaults.

Return only the final newsletter markdown.