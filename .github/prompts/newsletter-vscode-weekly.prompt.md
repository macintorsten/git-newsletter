---
description: "Generate a VS Code weekly newsletter markdown using the bundled example profile"
name: "Newsletter VS Code Weekly"
argument-hint: "[optional overrides: repo=..., branch=..., period_days=..., title=..., output_path=...]"
agent: "newsletter-editor"
---

Use profile prompt file [example-vscode-weekly.prompt.md](./profiles/examples/example-vscode-weekly.prompt.md).

Default inputs:
- repo: https://github.com/microsoft/vscode.git
- branch: main
- period_days: 7
- output_path: vscode-weekly-newsletter.md

If the user supplied extra text after this slash command, treat it as optional overrides to those defaults.

Return only the final newsletter markdown.