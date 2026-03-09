# Example Profile: Kubernetes Weekly

- profile_name: kubernetes-weekly
- repository: https://github.com/kubernetes/kubernetes.git
- branch: master
- period_days: 7
- output_path: kubernetes-weekly-newsletter.md
- title_style: Kubernetes Engineering Weekly

Editorial focus:
- Prioritize API behavior changes, control plane reliability, scheduling, networking, storage, security hardening, and release-critical fixes.
- De-emphasize broad mechanical refactors unless risk-relevant.
- Deep-dive candidates: major KEP-related implementation milestones, security changes, backward-compatibility notes.

Section preferences:
- Keep sections in this order: Cluster Reliability, API and Compatibility, Security, Performance, Bug Fixes.
- Add a "Potential operator impact" bullet list when behavior changes are user-visible.

Tone and format:
- Audience: platform engineers and SREs.
- Emphasize operational impact and upgrade risk.