# Example Profile: GitHub CLI Weekly

- profile_name: github-cli-weekly
- repository: https://github.com/cli/cli.git
- branch: trunk
- period_days: 7
- output_path: github-cli-weekly-newsletter.md
- title_style: GitHub CLI Power User Weekly

Editorial focus:
- Prioritize command UX, auth and token handling, API integrations, automation workflows, and shell-friendly output changes.
- De-emphasize cosmetic refactors unless they affect extensibility or scripting.
- Deep-dive candidates: breaking flag behavior, auth model changes, new automation primitives, or API parity work.

Section preferences:
- Keep sections in this order: New Commands and Flags, Automation Impact, Auth and Security, Scripting Fixes, Cleanup Worth Noting.
- Include a small "One-liner to try" callout when a change introduces a useful workflow.

Tone and format:
- Audience: terminal-heavy developers, release engineers, and internal tooling teams.
- Keep it concise, command-oriented, and slightly opinionated about workflow implications.