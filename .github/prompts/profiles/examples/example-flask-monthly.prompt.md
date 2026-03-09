# Example Profile: Flask Monthly

- profile_name: flask-monthly
- repository: https://github.com/pallets/flask.git
- branch: main
- period_days: 30
- output_path: flask-monthly-newsletter.md
- title_style: Flask Maintainer Update - Monthly

Why monthly:
- Commit activity is typically lower than very high-churn infrastructure repos, so a 30-day window improves signal quality.

Editorial focus:
- Prioritize framework behavior changes, security fixes, compatibility notes, Werkzeug/Jinja interactions, and docs that change recommended practices.
- De-emphasize minor housekeeping commits unless they affect maintainers.
- Deep-dive candidates: migration guidance, deprecations, and security-sensitive behavior.

Section preferences:
- Keep sections in this order: Highlights, Compatibility and Migrations, Security, Docs and DX, Maintenance.
- Include one "Action for app maintainers" checklist when relevant.

Tone and format:
- Audience: Python web developers and maintainers.
- Keep practical and migration-focused.