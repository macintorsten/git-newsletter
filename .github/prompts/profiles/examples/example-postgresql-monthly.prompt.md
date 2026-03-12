# Example Profile: PostgreSQL Monthly

- profile_name: postgresql-monthly
- repository: https://github.com/postgres/postgres.git
- branch: master
- period_days: 30
- output_path: postgresql-monthly-newsletter.md
- title_style: PostgreSQL Engineering Ledger - Monthly

Why monthly:
- Database engine work is easier to understand when grouped into release-relevant themes rather than isolated weekly commits.

Editorial focus:
- Prioritize query planner work, replication, storage engine changes, security fixes, extension compatibility, and documentation that affects operators.
- De-emphasize minor refactors unless they have release, reliability, or compatibility implications.
- Deep-dive candidates: planner behavior, storage internals, replication semantics, and upgrade guidance.

Section preferences:
- Keep sections in this order: Core Engine, Reliability and Operations, Security and Compatibility, Performance, Notes for DBAs.
- Include one short "Questions to ask before upgrading" checklist when behavior changes may surface operational risk.

Tone and format:
- Audience: database engineers, DBAs, and platform teams.
- Write with a newsroom tone: factual, compact, and careful about evidence.