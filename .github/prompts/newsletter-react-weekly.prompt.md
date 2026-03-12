---
description: "Generate a React weekly newsletter markdown using the bundled example profile"
name: "Newsletter React Weekly"
argument-hint: "[optional overrides: repo=..., branch=..., period_days=..., title=..., output_path=...]"
agent: "newsletter-editor"
---

Use profile prompt file [example-react-weekly.prompt.md](./profiles/examples/example-react-weekly.prompt.md).

Default inputs:
- repo: https://github.com/facebook/react.git
- branch: main
- period_days: 7
- output_path: react-weekly-newsletter.md

If the user supplied extra text after this slash command, treat it as optional overrides to those defaults.

Return only the final newsletter markdown.