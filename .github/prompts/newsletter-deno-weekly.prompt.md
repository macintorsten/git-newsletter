---
description: "Generate a Deno weekly newsletter markdown using the bundled example profile"
name: "Newsletter Deno Weekly"
argument-hint: "[optional overrides: repo=..., branch=..., period_days=..., title=..., output_path=...]"
agent: "newsletter-editor"
---

Use profile prompt file [example-deno-weekly.prompt.md](./profiles/examples/example-deno-weekly.prompt.md).

Default inputs:
- repo: https://github.com/denoland/deno.git
- branch: main
- period_days: 7
- output_path: deno-weekly-newsletter.md

If the user supplied extra text after this slash command, treat it as optional overrides to those defaults.

Return only the final newsletter markdown.