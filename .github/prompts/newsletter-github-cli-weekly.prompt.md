---
description: "Generate a GitHub CLI weekly newsletter markdown using the bundled example profile"
name: "Newsletter GitHub CLI Weekly"
argument-hint: "[optional overrides: repo=..., branch=..., period_days=..., title=..., output_path=...]"
agent: "newsletter-editor"
---

Use profile prompt file [example-github-cli-weekly.prompt.md](./profiles/examples/example-github-cli-weekly.prompt.md).

Default inputs:
- repo: https://github.com/cli/cli.git
- branch: trunk
- period_days: 7
- output_path: github-cli-weekly-newsletter.md

If the user supplied extra text after this slash command, treat it as optional overrides to those defaults.

Return only the final newsletter markdown.