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
- [x] Add explicit stage lifecycle values: `pending -> done | failed | skipped`.
- [x] Define when `web_research` is `skipped` (no queued deep dives).
- [x] Clarify terminal behavior when any stage is `failed`.
- [x] Add concise polling/retry note for orchestrator.

Acceptance criteria:
- [x] Flow doc and orchestrator agree on identical statuses.
- [x] No ambiguous stage transitions remain.

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
- [x] Add uniqueness constraints guidance for logical IDs:
  - `nl_commits(session_id, sha)`
  - `nl_articles(session_id, article_id)`
  - `nl_research(session_id, research_id)`
- [x] Update SQL examples to use idempotent write patterns.
- [x] Add explicit row-level upsert/update behavior per specialist.
- [x] Clarify that stage completion happens only after all row writes succeed.

Acceptance criteria:
- [x] Skill instructions support safe rerun with same `session_id`.
- [x] No specialist uses non-idempotent bulk completion language.

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
- [x] Keep agents focused on: role, inputs/outputs, handoff contract, done criteria.
- [x] Keep detailed execution SQL and heuristics in skills.
- [x] Remove repeated policy blocks from agents if already in skills.
- [x] Ensure each agent points to one authoritative skill path.

Acceptance criteria:
- [x] Instruction duplication reduced significantly.
- [x] Role ownership is obvious from a quick read.

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
- [x] Add orchestrator guidance to split pending research into shards/batches.
- [x] Pass explicit `research_id` set or shard token in handoff prompt.
- [x] Require researcher to update only assigned rows.
- [x] Mark stage done only after zero pending rows remain.

Acceptance criteria:
- [x] Parallel workers cannot overwrite each other's rows.
- [x] Flow doc describes fan-out and fan-in clearly.

---

## Chunk 5: Reliability Hardening

Commit intent:
- Reduce transient failure impact and improve observability.

Files:
- `.github/agents/newsletter-editor.agent.md`
- `.github/agents/web-researcher.agent.md`
- `.github/agents/commit-analyst.agent.md`

Tasks:
- [x] Add retry policy for transient tool/database auth failures.
- [x] Add failure recording guidance (stage + error note).
- [x] Require non-fatal per-row error continuation where appropriate.
- [x] Document recovery path for restarting from existing `session_id`.

Acceptance criteria:
- [x] A transient first-failure can recover without losing the run.
- [x] Failed runs are diagnosable from status tables and notes.

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

## Chunk 7: Output Format Contract (No Frontmatter)

Commit intent:
- Ensure generated newsletter Markdown is content-only and never starts with YAML frontmatter.

Files:
- `.github/skills/newsletter-writing/SKILL.md`
- `.github/agents/newsletter-writer.agent.md`
- `README.md` (only if output-format expectations are documented)

Research findings (current behavior):
- The writer skill currently provides a canonical output template that starts with YAML frontmatter (`---` metadata block).
- A generated sample newsletter in `samples/email/` includes that frontmatter at the top, confirming this behavior in practice.
- The desired contract is markdown output without frontmatter, so current writer instructions conflict with product expectations.

Tasks:
- [x] Remove frontmatter from the canonical newsletter template in writer instructions.
- [x] Replace metadata block with plain markdown header/subheader content (title/period/repo/branch) in-body.
- [x] Add explicit negative requirement: "Do not include YAML/frontmatter delimiters (`---`) at document start."
- [x] Add a simple validation step in writer guidance that checks first non-empty line is not `---`.

Acceptance criteria:
- [x] Generated `newsletter_md` never begins with `---`.
- [x] Writer agent and writer skill are consistent on no-frontmatter output format.
- [x] Existing section structure still renders correctly in markdown-to-HTML conversion.

---

## Chunk 8: Docs + Runbook Update

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
8. Chunk 8

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
- [~] Chunk 1 implemented (not merged)
- [~] Chunk 2 implemented (not merged)
- [~] Chunk 3 implemented (not merged)
- [~] Chunk 4 implemented (not merged)
- [~] Chunk 5 implemented (not merged)
- [~] Chunk 7 implemented (not merged)
- [ ] Chunk 2 merged
- [ ] Chunk 3 merged
- [ ] Chunk 4 merged
- [ ] Chunk 5 merged
- [ ] Chunk 6 merged
- [ ] Chunk 7 merged
- [ ] Chunk 8 merged
