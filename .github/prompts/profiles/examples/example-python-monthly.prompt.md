# Example Profile: Python Monthly

- profile_name: python-monthly
- repository: https://github.com/python/cpython.git
- branch: main
- period_days: 30
- output_path: python-monthly-newsletter.md
- title_style: Python Core Monthly Ledger

Why monthly:
- Language and runtime work benefits from a longer window so implementation details can be grouped into a coherent maintainer story instead of a noisy weekly feed.

Editorial focus:
- Prioritize language behavior, standard library evolution, runtime performance, typing changes, packaging implications, and documentation that updates best practices.
- De-emphasize pure housekeeping unless it changes contributor workflow or release readiness.
- Deep-dive candidates: backwards compatibility, deprecations, interpreter internals, and packaging transitions.

Section preferences:
- Keep sections in this order: Interpreter and Language, Standard Library, Typing and Tooling, Performance, Release Notes for Maintainers.
- Include one short "Who needs to act" note when downstream library authors or distributors should care.

Tone and format:
- Audience: Python library maintainers, runtime contributors, and experienced application developers.
- Write with a literary but precise cadence; avoid hype and explain tradeoffs clearly.