# Agent Flow Improvements Plan

Status legend:
- [ ] Not started
- [~] In progress
- [x] Completed
- [!] Blocked

## Goals

- Improve reliability and idempotency of multi-agent orchestration.
- Improve throughput via explicit parallel research fan-out.
- Reduce instruction duplication and context pressure.
- Raise output quality consistency and auditability.

## Scope

In scope:
- `.github/agents/*`
- `.github/skills/*`
- `README.md` (only if behavior/usage changes)

Out of scope:
- Changing newsletter content style themes.
- Replacing the current session_store architecture.
- Broad refactors outside agent/skill orchestration.

## Review Strategy

Each commit chunk below is designed to be:
- Small enough to review in one pass.
- Functionally cohesive.
- Safe to rollback independently.

---

## Chunk 1: State Machine + Status Semantics

Commit intent:
- Make stage progression explicit and deterministic.

Files:
- `.github/agents/FLOW.md`
- `.github/agents/newsletter-editor.agent.md`

Tasks:
- [ ] Add explicit stage lifecycle values: `pending -> done | failed | skipped`.
- [ ] Define when `web_research` is `skipped` (no queued deep dives).
- [ ] Clarify terminal behavior when any stage is `failed`.
- [ ] Add concise polling/retry note for orchestrator.

Acceptance criteria:
- [ ] Flow doc and orchestrator agree on identical statuses.
- [ ] No ambiguous stage transitions remain.

---

## Chunk 2: DB Idempotency Contract

Commit intent:
- Make writes safe to retry and robust against partial reruns.

Files:
- `.github/agents/newsletter-editor.agent.md`
- `.github/skills/commit-analysis/SKILL.md`
- `.github/skills/web-research/SKILL.md`
- `.github/skills/newsletter-writing/SKILL.md`

Tasks:
- [ ] Add uniqueness constraints guidance for logical IDs:
  - `nl_commits(session_id, sha)`
  - `nl_articles(session_id, article_id)`
  - `nl_research(session_id, research_id)`
- [ ] Update SQL examples to use idempotent write patterns.
- [ ] Add explicit row-level upsert/update behavior per specialist.
- [ ] Clarify that stage completion happens only after all row writes succeed.

Acceptance criteria:
- [ ] Skill instructions support safe rerun with same `session_id`.
- [ ] No specialist uses non-idempotent bulk completion language.

---

## Chunk 3: Responsibility Cleanup (Agent vs Skill)

Commit intent:
- Reduce duplicated instructions and tighten boundaries.

Files:
- `.github/agents/commit-analyst.agent.md`
- `.github/agents/web-researcher.agent.md`
- `.github/agents/newsletter-writer.agent.md`
- `.github/skills/commit-analysis/SKILL.md`
- `.github/skills/web-research/SKILL.md`
- `.github/skills/newsletter-writing/SKILL.md`

Tasks:
- [ ] Keep agents focused on: role, inputs/outputs, handoff contract, done criteria.
- [ ] Keep detailed execution SQL and heuristics in skills.
- [ ] Remove repeated policy blocks from agents if already in skills.
- [ ] Ensure each agent points to one authoritative skill path.

Acceptance criteria:
- [ ] Instruction duplication reduced significantly.
- [ ] Role ownership is obvious from a quick read.

---

## Chunk 4: Parallel Research Fan-out

Commit intent:
- Enable practical concurrency with bounded context per worker.

Files:
- `.github/agents/newsletter-editor.agent.md`
- `.github/agents/web-researcher.agent.md`
- `.github/skills/web-research/SKILL.md`
- `.github/agents/FLOW.md`

Tasks:
- [ ] Add orchestrator guidance to split pending research into shards/batches.
- [ ] Pass explicit `research_id` set or shard token in handoff prompt.
- [ ] Require researcher to update only assigned rows.
- [ ] Mark stage done only after zero pending rows remain.

Acceptance criteria:
- [ ] Parallel workers cannot overwrite each other's rows.
- [ ] Flow doc describes fan-out and fan-in clearly.

---

## Chunk 5: Reliability Hardening

Commit intent:
- Reduce transient failure impact and improve observability.

Files:
- `.github/agents/newsletter-editor.agent.md`
- `.github/agents/web-researcher.agent.md`
- `.github/agents/commit-analyst.agent.md`

Tasks:
- [ ] Add retry policy for transient tool/database auth failures.
- [ ] Add failure recording guidance (stage + error note).
- [ ] Require non-fatal per-row error continuation where appropriate.
- [ ] Document recovery path for restarting from existing `session_id`.

Acceptance criteria:
- [ ] A transient first-failure can recover without losing the run.
- [ ] Failed runs are diagnosable from status tables and notes.

---

## Chunk 6: Output Quality Guardrails

Commit intent:
- Improve consistency and editorial quality with minimal overhead.

Files:
- `.github/agents/newsletter-editor.agent.md`
- `.github/skills/newsletter-writing/SKILL.md`
- `.github/skills/web-research/SKILL.md`

Tasks:
- [ ] Add selection checks to avoid duplicate/low-signal articles.
- [ ] Require clear "why it matters" in selected article output.
- [ ] Tighten source quality requirement for deep dives (primary source preferred).
- [ ] Add confidence fallback text when sources are weak.

Acceptance criteria:
- [ ] Newsletter quality rubric is explicit and testable.
- [ ] Deep-dive outputs are clearly sourced and bounded.

---

## Chunk 7: Docs + Runbook Update

Commit intent:
- Keep operations discoverable for future maintainers.

Files:
- `README.md`
- `.github/agents/FLOW.md`
- `docs/agent-flow-improvements-plan.md`

Tasks:
- [ ] Add brief runbook for troubleshooting stage failures.
- [ ] Add section on rerun behavior and idempotency assumptions.
- [ ] Note any command/flag expectations for Copilot CLI.

Acceptance criteria:
- [ ] A new maintainer can run and troubleshoot the pipeline from docs only.

---

## Execution Order

1. Chunk 1
2. Chunk 2
3. Chunk 3
4. Chunk 4
5. Chunk 5
6. Chunk 6
7. Chunk 7

Rationale:
- Establish contract/state first.
- Then make writes safe.
- Then optimize structure/concurrency.
- Then harden and polish quality/docs.

## Risks and Mitigations

- Risk: Over-editing all files at once.
  - Mitigation: Strictly one chunk per commit.
- Risk: Behavior drift between agents and skills.
  - Mitigation: Keep one source of truth per concern.
- Risk: Parallel research race conditions.
  - Mitigation: Row-scoped updates and fan-in check before stage completion.

## Progress Tracker

- [~] Plan document created
- [ ] Chunk 1 merged
- [ ] Chunk 2 merged
- [ ] Chunk 3 merged
- [ ] Chunk 4 merged
- [ ] Chunk 5 merged
- [ ] Chunk 6 merged
- [ ] Chunk 7 merged
