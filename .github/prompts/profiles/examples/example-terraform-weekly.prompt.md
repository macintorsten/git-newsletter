# Example Profile: Terraform Weekly

- profile_name: terraform-weekly
- repository: https://github.com/hashicorp/terraform.git
- branch: main
- period_days: 7
- output_path: terraform-weekly-newsletter.md
- title_style: Terraform Executive Brief - Weekly

Editorial focus:
- Prioritize provider lifecycle behavior, state handling, plan/apply semantics, testing and policy workflows, and security or upgrade implications.
- De-emphasize low-level refactors unless they could affect enterprise rollout or ecosystem compatibility.
- Deep-dive candidates: state migration, provider protocol changes, policy enforcement, or breaking workflow assumptions.

Section preferences:
- Keep sections in this order: Executive Summary, Provider and State Impact, Policy and Governance, Performance and Reliability, Action Items.
- Include a short "Who should care" note for platform leadership and a checklist for operators when needed.

Tone and format:
- Audience: platform leaders, infra maintainers, and implementation teams.
- Keep it concise, boardroom-readable, and explicit about operational consequences.