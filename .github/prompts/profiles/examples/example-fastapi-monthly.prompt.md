# Example Profile: FastAPI Monthly

- profile_name: fastapi-monthly
- repository: https://github.com/fastapi/fastapi.git
- branch: master
- period_days: 30
- output_path: fastapi-monthly-newsletter.md
- title_style: FastAPI Maintainer Notes - Monthly

Why monthly:
- FastAPI changes are easier to evaluate in monthly clusters where framework polish, dependency shifts, and migration notes can be grouped into a coherent maintainer update.

Editorial focus:
- Prioritize request and response behavior, dependency injection, validation, compatibility with Starlette and Pydantic, deployment guidance, and developer experience changes.
- De-emphasize trivial housekeeping unless it affects real services or maintainer workflows.
- Deep-dive candidates: migration notes, behavior changes, validation semantics, or security-relevant request handling.

Section preferences:
- Keep sections in this order: Highlights, Compatibility and Upgrades, Validation and Data Models, Docs and DX, Maintainer Checklist.
- Include one short checklist for application teams when version bumps or migrations matter.

Tone and format:
- Audience: backend Python teams, API platform maintainers, and consultants shipping FastAPI in production.
- Keep the writing calm, minimal, and actionable.