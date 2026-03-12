# Example Profile: React Weekly

- profile_name: react-weekly
- repository: https://github.com/facebook/react.git
- branch: main
- period_days: 7
- output_path: react-weekly-newsletter.md
- title_style: React Signal Weekly

Editorial focus:
- Prioritize rendering semantics, compiler and build pipeline work, suspense and server component changes, and docs that change recommended app architecture.
- De-emphasize internal churn unless it affects framework consumers, library authors, or migration strategy.
- Deep-dive candidates: compiler milestones, concurrent behavior, hydration changes, and ecosystem-facing RFC implementation work.

Section preferences:
- Keep sections in this order: Rendering Model, Compiler and Tooling, Library Author Impact, Performance, Bug Fixes.
- Add a short "What this means for framework integrators" note when host frameworks need to react.

Tone and format:
- Audience: senior frontend engineers, library maintainers, and framework integrators.
- Keep it energetic, technically sharp, and careful about separating landed behavior from future-facing groundwork.