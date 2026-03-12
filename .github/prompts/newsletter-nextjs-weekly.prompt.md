---
description: "Generate a Next.js weekly newsletter markdown using the bundled example profile"
name: "Newsletter Next.js Weekly"
argument-hint: "[optional overrides: repo=..., branch=..., period_days=..., title=..., output_path=...]"
agent: "newsletter-editor"
---

Use profile prompt file [example-nextjs-weekly.prompt.md](./profiles/examples/example-nextjs-weekly.prompt.md).

Default inputs:
- repo: https://github.com/vercel/next.js.git
- branch: canary
- period_days: 7
- output_path: nextjs-weekly-newsletter.md

If the user supplied extra text after this slash command, treat it as optional overrides to those defaults.

Return only the final newsletter markdown.