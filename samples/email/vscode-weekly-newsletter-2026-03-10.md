# 📰 Dev Weekly — VS Code

> *A massive week for AI-assisted development: the Sessions feature matured dramatically, the Debug Panel gained OpenTelemetry superpowers, and a wave of performance, terminal, and security improvements landed across the board — 420 commits from dozens of contributors.*

**Period:** 4 Mar 2026 – 10 Mar 2026 · **Branch:** `main` · **Commits:** 420

---

## 🚀 This Week's Highlights

---

### 🤖 AI Sessions: The Next Level of Agent-Assisted Development

The biggest story this week is the continued evolution of **VS Code Sessions** — the feature that lets Copilot agents work alongside you in a dedicated, isolated workspace. Think of it as a co-pilot who gets their own room: a full coding environment where they can browse files, run commands, and make changes, while you stay in control.

#### What landed this week

- **Draft PR prompts** 📝 — When a Copilot session completes work, it can now prompt you to create a draft pull request, making the handoff from agent to human review smoother (Ladislau Szomoru).
- **Mode picker in Sessions app** 🎛️ — You can now switch between different agent modes directly inside the Sessions UI, so you can go from a quick-fix agent to a deep-dive coding agent without leaving context (Sandeep Somavarapu).
- **Toolbar and action tweaks** 🔧 — The session toolbar got cleaner icons, new filtering actions, and smoother UX across the board (Ladislau Szomoru, BeniBenj).
- **Worktree branch names in the files view** 🌿 — Sessions now shows the correct worktree branch name (a *worktree* is a Git concept that lets you check out multiple branches simultaneously in separate folders), giving you better context at a glance.
- **Base branch information exposed** — Sessions now surfaces the base branch of the current session, critical for knowing where a PR will eventually merge.
- **Workspace data sent to extension host** 📡 — The Sessions app now sends workspace data by default to the extension host, enabling richer integrations.
- **Context key calculation updated** 🔑 — Internal improvements to how session state is tracked ensure UI elements like buttons and menus appear at the right time.

#### Why it matters

Sessions is shaping up to be VS Code's killer feature for AI-assisted development. Each improvement this week makes the human↔agent handoff feel less like handing off to a black box and more like working with a junior developer who has their own desk, their own branch, and a clear checklist. The PR draft prompt alone will save teams significant back-and-forth.

🙌 **Contributors:** Ladislau Szomoru, Sandeep Somavarapu, BeniBenj (Benjamin Christopher Simmonds), Benjamin Pasero

> 📖 **Deep Dive: How does VS Code Copilot Coding Agent compare to Cursor and JetBrains?**
>
> **VS Code Copilot Coding Agent** runs entirely in a **GitHub Actions cloud environment** — fully isolated, GitHub-hosted, and asynchronous. You assign an issue to `@copilot` or delegate from chat; the agent works in the background (even when VS Code is closed) and delivers a pull request ready for your review. The tight GitHub integration means the entire code-review workflow (comments, re-runs, approvals) happens natively.
>
> **Cursor's Background Agents** (launched Feb 2026) also run autonomously but use a remote computer-use model — the agent spins up a virtual machine, browses, types, and runs commands as if it were a human. This gives it broader tool access but at the cost of predictability.
>
> **JetBrains AI Assistant** focuses primarily on interactive, in-editor AI assistance (code completion, explanations, test generation) and doesn't yet offer a comparable fully autonomous background agent tied to a CI/CD pipeline.
>
> The key VS Code differentiator: seamless GitHub Actions infra + native PR lifecycle = fits directly into teams already using GitHub, with no new tooling to adopt. 🚀
>
> 🔗 [Learn more](https://code.visualstudio.com/docs/copilot/copilot-coding-agent)

---

### 💬 Chat Gets Smarter: Symbols, Inline Completions & Model Picker Polish

VS Code's chat panel — your primary interface for talking to Copilot — received a meaningful round of improvements this week, tightening the loop between what you type, what the AI understands, and what you see.

#### Symbol paste provider ✨

Connor Peet added a **symbol paste provider** to chat. When you copy a symbol (a function name, class, or variable) from your editor and paste it into the chat input, VS Code now automatically resolves it to a rich reference rather than pasting raw text. This means Copilot knows *exactly* which `render()` function you mean — no more ambiguity.

#### Quick suggestions enhanced with inline completions 🚀

Johannes Rieken enhanced **quick suggestions** (the small grey ghost text that appears as you type) by wiring them into the inline completions engine. This means the suggestions you see while typing can now draw from the same AI-powered completions used by Copilot, making autocomplete feel noticeably more intelligent in more contexts.

#### Model picker improvements 🎛️

Sandeep Somavarapu made it easier to manage AI models:
- A **"Manage models"** action now appears directly in the search input, so you can switch or add models without hunting through settings.
- The model picker delegate was refactored for cleaner code and a smoother UX.

#### Plugin system: enable/disable like extensions 🔌

Connor Peet added the ability to **disable and re-enable agent plugins** (think of plugins as extra skills you give Copilot, like "search the web" or "run tests") through the same UI you use to manage VS Code extensions. Previously, removing a plugin was all-or-nothing; now you can temporarily disable one without uninstalling it.

#### MCP elicitations 🤝

The **Model Context Protocol (MCP)** — an open standard for letting AI models ask for structured information from tools — now uses a proper "ask questions" flow (`askquestions`) for *elicitations* (moments when the AI needs to clarify something before proceeding). This replaces a more ad-hoc approach and makes agent interactions feel more polished.

🙌 **Contributors:** Connor Peet, Johannes Rieken, Sandeep Somavarapu, Matt Bierner

---

### 🔭 Debug Panel Gets OpenTelemetry Superpowers

Vijay Upadya landed a significant addition to the Debug Panel: **OpenTelemetry (oTel) data source support**, complete with import and export capabilities.

#### What is OpenTelemetry?

**OpenTelemetry** (often shortened to *oTel*) is an open-source observability framework — a standardised way of collecting and exporting *telemetry data*: traces (how a request flows through your system), metrics (counts, durations, gauges), and logs. It's become the industry standard for understanding what production software is actually doing.

#### What changed

The VS Code Debug Panel can now:
- **Connect to an oTel data source** directly — meaning you can pull live or recorded telemetry into your debugging session without leaving VS Code.
- **Import and export** oTel data — so you can share a trace with a colleague, load a production trace into a local debugging session, or save a session for later analysis.

#### Why it matters 🎯

Debugging distributed systems (microservices, serverless functions, cloud apps) is notoriously hard because the bug might not be in *your* code — it could be a slow database call, a network timeout, or a cascading failure three hops away. By bringing oTel data right into the debugger, VS Code is bridging the gap between local development and production observability.

> **Note:** this feature was briefly reverted and re-landed this week as some CI issues were sorted out — the final version is stable and enabled.

🙌 **Contributor:** Vijay Upadya

> 📖 **Deep Dive: Why does native oTel in your IDE debugger matter?**
>
> **OpenTelemetry (oTel)** is a CNCF (Cloud Native Computing Foundation) open standard for collecting and exporting *traces* (request flows), *metrics* (counts/durations), and *logs* from software systems. It is vendor-neutral — data can flow to Jaeger, Prometheus, Grafana, Azure Monitor, Datadog, or any compatible backend.
>
> Bringing oTel support into the VS Code Debug Panel is significant because **production debugging changes fundamentally**: instead of adding `console.log` statements and redeploying, a developer can load a real production trace — showing exactly which microservice was slow, which database query timed out, which function threw — directly into their debugging session.
>
> Popular workflows now enabled:
> - 🔍 Load a Jaeger trace of a production incident into VS Code and step through the code that caused it
> - 📊 Correlate Prometheus metrics with the exact code path being debugged
> - ☁️ Import Azure Monitor traces when debugging cloud-native apps
>
> With first-party oTel integrations in Next.js, Quarkus, Argo Workflows, and most major cloud SDKs, the ecosystem is mature and the VS Code integration arrives at exactly the right moment. 🎯
>
> 🔗 [Learn more](https://opentelemetry.io/docs/what-is-opentelemetry/)

---

### 🖥️ Terminal Reliability: PTY Fixes, Kitty Protocol & IME Improvements

The VS Code integrated terminal received a quiet but impactful set of reliability fixes this week, addressing some gnarly edge cases that frustrated users on macOS and in CJK (Chinese, Japanese, Korean) input workflows.

#### PTY multiline write fix on macOS 🐛

Jamie Cansdale fixed a long-standing bug where writing **multiline output to the PTY** (pseudo-terminal — the software layer that emulates a hardware terminal) on macOS could silently corrupt data. The root cause: macOS has a 1024-byte buffer limit per PTY write. When VS Code sent a chunk larger than that in a single call, bytes were dropped or scrambled. The fix chunks multiline writes to stay within the buffer limit, making terminal output reliable for long commands and scripts.

#### Kitty keyboard protocol fix ⌨️

Anthony Kim bumped the **xterm.js** library (the terminal emulator powering VS Code's terminal) to pick up a fix for the *Kitty keyboard protocol* — an extended keyboard input protocol used by modern terminal applications (like Neovim with the right config) to distinguish keystrokes that vanilla terminals can't tell apart (e.g., `Ctrl+I` vs `Tab`). Users relying on Kitty-aware terminal apps should see better key handling.

#### IME overflow fix 🌏

The same xterm.js bump also includes a fix for **IME overflow** — *IME* stands for *Input Method Editor*, the system used to type CJK characters using a phonetic keyboard. Previously, certain IME compositions could overflow the terminal's character grid, causing visual glitches.

#### Terminal benchmark fix 🔧

Megan Rogge fixed a crash in the terminal benchmark suite (`cannot read properties of undefined (reading 'getCell')`) that was blocking automated performance tests from running.

🙌 **Contributors:** Jamie Cansdale, Anthony Kim, Megan Rogge

---

### 🏎️ Performance Round-Up: Editor, Chat & Extension Discovery

A cluster of performance improvements landed this week across different parts of VS Code, each shaving latency in a different area.

#### Editor line height optimisation ✨

Aiday Marlen Kyzy optimised `_doRemoveCustomLineHeight`, an internal function responsible for recalculating line heights when custom decorations are removed (e.g., when diff decorations or diagnostics are cleared). The change avoids unnecessary reflows, making editors with lots of decorations more responsive.

#### Chat anchor widget optimisation 💬

Rob Lourens optimised the **chat anchor widget** — the small UI element that anchors a Copilot chat conversation to a specific file location. The old code was doing redundant work on every re-render; the optimised version caches state more aggressively, reducing jank during active chat sessions.

#### Faster extension discovery ⚡

Paul optimised the extension discovery process (the phase where VS Code scans for installed extensions at startup) by:
- **Removing an unnecessary `await`** in the discovery phase, allowing work to proceed synchronously where async wasn't needed.
- **Parallelising** parts of the scan that were previously sequential.

These changes can shave meaningful milliseconds off startup time, especially in environments with many installed extensions.

#### SCM view grouping performance 🗂️

Osvaldo Ortega changed the Source Control Manager (SCM) view to use `update()` instead of `refresh()` when toggling grouping, avoiding a full re-render of the repository tree.

🙌 **Contributors:** Aiday Marlen Kyzy, Rob Lourens, Paul, Osvaldo Ortega

---

### 🪟 Modal Editor: Resize, Persist State & UI Polish

Benjamin Pasero continued iterating on the **modal editor** — a new editing mode that opens files in a focused, distraction-free overlay rather than a regular editor tab — with three quality-of-life improvements this week.

#### Resizable modal editor 📐

The modal editor can now be **resized** by dragging its edges (fixing [#293915](https://github.com/microsoft/vscode/issues/293915)). Previously it was fixed-size, which was frustrating when working with wide files or long diffs. This was one of the most-requested usability improvements since the feature launched.

#### Persistent state 💾

The modal editor now **persists its state** — size, position, and which file was open — across sessions. So if you close VS Code while a modal is open, it'll restore to the same state next time. This is powered by VS Code's standard *memento* (key-value storage) system.

#### Adaptive padding fix 🎨

A layout bug where the chat input had incorrect padding when the modal was in a narrow configuration was fixed, making the editor look polished at all sizes.

🙌 **Contributor:** Benjamin Pasero

---

### 🔒 MCP Sandboxing & Browser Tool Hardening

Security and reliability improvements landed for two of VS Code's newer capability areas: the **MCP sandbox** and the built-in **browser tool**.

#### MCP sandbox path extraction fix 🛡️

dileepyavan improved the regex used to extract file paths from **MCP sandbox** error messages. The MCP (Model Context Protocol) sandbox is a security layer that restricts what file paths an AI tool can access. When the sandbox blocks an operation, it generates an error; VS Code parses that error to give useful feedback. A more robust regex means fewer false negatives — paths are correctly identified and reported even in edge cases.

#### Terminal sandbox experiment mode 🧪

An **experiment mode** was added to the terminal sandbox, making it possible to test sandboxing behaviour in controlled scenarios without affecting production users. This is infrastructure work that will allow the team to gradually roll out stricter sandboxing.

#### Browser tool: URL normalisation 🌐

Kyle Cutler fixed URL normalisation in the built-in browser tool's tool calls — ensuring that URLs are consistently formatted before being passed to the browser, preventing subtle bugs where the same page could be treated as different URLs.

#### Browser tool: prevent system sleep 😴

The browser tool was preventing the system from sleeping even when idle — a battery-draining bug. Kyle Cutler fixed this so the browser tool correctly releases the wake lock when not actively in use.

🙌 **Contributors:** dileepyavan, Kyle Cutler

---

### 📦 Dependency Updates & Housekeeping

A steady flow of dependency bumps and cleanup commits kept the codebase healthy this week.

#### Notable dependency updates

| Package | Change | Why it matters |
|---|---|---|
| **xterm.js** | Bumped ×2 | IME overflow + Kitty keyboard fixes (see terminal article) |
| **@vscode/codicons v0.0.45-14** 🎨 | Updated | Refreshed icon set — new icons and fixes (Lee Murray) |
| **DOMPurify 3.2.7 → 3.3.2** 🔒 | Security bump | Prevents XSS in Markdown preview; staying current matters (dependabot) |
| **express-rate-limit 8.2.1 → 8.3.0** | Minor bump | Used in MCP test harness (dependabot) |

#### Code quality 🧹

Matt Bierner continued a steady stream of TypeScript type-safety improvements:
- Reduced `any` usage across multiple files, replacing loose types with proper interfaces.
- Cleaned up unused imports and removed confusing API surface from the chat session types.
- Bumped the default extension target version for VS Code's extension build tooling.

🙌 **Contributors:** Lee Murray, dependabot, Matt Bierner

---

## 🌿 Active Development Branches

These branches had significant commit activity this week alongside `main`:

| Branch | Commits (7d) | Last Author | Last Active |
|---|---|---|---|
| `aeschli/low-tapir-336` | 401 | Martin Aeschlimann | 10 Mar 2026 |
| `alexr00/disappointed-aardvark` | 386 | Alex Ross | 10 Mar 2026 |
| `DileepY/sandbox_domain` | 42 | Dileep Yavanmandha | 4 Mar 2026 |

The `aeschli` and `alexr00` branches are clearly tracking major in-progress work (401 and 386 commits respectively!) — watch for those to land on `main` soon. 👀

---

## ⚠️ Stale Branches to Watch

These branches haven't seen activity in over 30 days and may be candidates for cleanup:

| Branch | Last Author | Age |
|---|---|---|
| `DileepY/terminal_sandboxing_testing` | Dileep Yavanmandha | ~96 days |
| `DileepY/testing_linux` | Ubuntu | ~111 days |
| `TylerLeonhardt/*` (multiple) | Tyler Leonhardt | ~1,600+ days (2021!) |

The `TylerLeonhardt` branches from 2021 are very old — if they've been superseded by later work, now might be a good time to archive or delete them. 🧹

---

## 🙌 Contributor Shoutout

A massive thank you to everyone who shipped this week! Special recognition to:

- 🏆 **Ladislau Szomoru** — drove much of the Sessions feature forward
- 🏆 **Matt Bierner** — tireless TypeScript quality improvements across dozens of files
- 🏆 **Connor Peet** — symbol paste, MCP improvements, and plugin management
- 🏆 **Osvaldo Ortega** — a burst of Sessions grouping features and SCM perf fixes
- 🏆 **Benjamin Pasero** — modal editor polish that makes a real UX difference

---

*Generated by the git-newsletter editor • 10 Mar 2026*
