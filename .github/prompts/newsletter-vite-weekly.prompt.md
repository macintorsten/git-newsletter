---
description: "Generate a Vite weekly newsletter markdown using the bundled example profile"
name: "Newsletter Vite Weekly"
argument-hint: "[optional overrides: repo=..., branch=..., period_days=..., title=..., output_path=...]"
agent: "newsletter-editor"
---

Use profile prompt file [example-vite-weekly.prompt.md](./profiles/examples/example-vite-weekly.prompt.md).

Default inputs:
- repo: https://github.com/vitejs/vite.git
- branch: main
- period_days: 7
- output_path: vite-weekly-newsletter.md

If the user supplied extra text after this slash command, treat it as optional overrides to those defaults.

Return only the final newsletter markdown.