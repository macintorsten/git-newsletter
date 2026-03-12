---
description: "Generate a Kubernetes weekly newsletter markdown using the bundled example profile"
name: "Newsletter Kubernetes Weekly"
argument-hint: "[optional overrides: repo=..., branch=..., period_days=..., title=..., output_path=...]"
agent: "newsletter-editor"
---

Use profile prompt file [example-kubernetes-weekly.prompt.md](./profiles/examples/example-kubernetes-weekly.prompt.md).

Default inputs:
- repo: https://github.com/kubernetes/kubernetes.git
- branch: master
- period_days: 7
- output_path: kubernetes-weekly-newsletter.md

If the user supplied extra text after this slash command, treat it as optional overrides to those defaults.

Return only the final newsletter markdown.