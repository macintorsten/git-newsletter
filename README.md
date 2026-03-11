# Git Newsletter Toolkit

The main interface is an AI agent called `newsletter-editor`.
It analyzes a repository and produces newsletter markdown as output.

## Main idea

1. Run Copilot CLI with `--agent "newsletter-editor"`.
2. Pass either a direct prompt or a profile prompt file reference.
3. The agent orchestrates specialist agents to collect git activity, draft
   articles, optionally research deep dives, and assemble final markdown.
4. The main artifact is a markdown newsletter file.

Flow reference: see [`.github/agents/FLOW.md`](.github/agents/FLOW.md).

## Agent workflow (simplified)

```mermaid
flowchart LR
    Editor(["newsletter-editor\norchestrator"])
    Analyst["commit-analyst"]
    Researcher["web-researcher\noptional"]
    Writer["newsletter-writer"]
    Output([newsletter_output.md])

    Editor -->|"STEP 1"| Analyst
    Analyst -->|done| Editor
    Editor -->|"STEP 2\noptional"| Researcher
    Researcher -->|done| Editor
    Editor -->|"STEP 3"| Writer
    Writer -->|done| Editor
    Editor --> Output
```

- [`newsletter-editor`](.github/agents/newsletter-editor.agent.md) is the orchestrator and entrypoint.
- [`commit-analyst`](.github/agents/commit-analyst.agent.md) gathers git data and writes article drafts.
- `newsletter-editor` selects what to include and optionally queues research.
- [`web-researcher`](.github/agents/web-researcher.agent.md) fills research sidebars when queued.
- [`newsletter-writer`](.github/agents/newsletter-writer.agent.md) assembles final newsletter markdown.
- `newsletter-editor` returns the final output path/content.

## Python setup (required once)

Use Python 3.11+.

Install `uv`: https://docs.astral.sh/uv/getting-started/installation/

Prepare dependencies and activate the environment in the shell where you run
Copilot CLI:

```bash
uv sync
source .venv/bin/activate
```

The agents (especially commit analysis) execute Python helpers under
`.github/skills/`, so missing Python packages can break the newsletter run.

## Quickstart (Copilot CLI)

Prerequisites:

- Copilot CLI installed and authenticated
- Use `--experimental` when invoking Copilot CLI to enable session database support
- Git access to target repository URL/path

Direct prompt:

```bash
copilot --experimental -p "Create a concise weekly engineering newsletter from https://github.com/microsoft/vscode.git. Use branch main, cover the last 7 days, title it Dev Weekly, and write the final markdown to vscode-weekly-newsletter.md." --agent "newsletter-editor" --yolo
```

Prompt profile file with additional instructions:

```bash
newsletter_markdown=$(copilot --experimental -p "Use profile prompt file .github/prompts/profiles/examples/example-flask-monthly.prompt.md.
Generate a maintainers-focused monthly digest. Respond with only the final newsletter markdown content." --agent "newsletter-editor" --yolo)

printf '%s\n' "$newsletter_markdown" > flask-monthly-newsletter.md
```

Available profile prompts:

- `.github/prompts/profiles/TEMPLATE.prompt.md`
- `.github/prompts/profiles/examples/example-vscode-weekly.prompt.md`
- `.github/prompts/profiles/examples/example-kubernetes-weekly.prompt.md`
- `.github/prompts/profiles/examples/example-flask-monthly.prompt.md`

Run utility scripts with:

```bash
uv run python build_email.py --help
uv run python send_email.py --help
uv run python generate_examples.py
```

## Extra scripts (after markdown is generated)

These scripts do not call Copilot. They are optional post-processing tools.

1. Markdown/CSS to HTML:

```bash
uv run python build_email.py \
  --markdown samples/email/example_input.md \
  --style assets/email/styles/01-clean-blue.css \
  --output preview_output/ready_to_send.html
```

2. Generate all preview examples:

```bash
uv run python generate_examples.py
```

Open `preview_output/generated_html/index.html` in your browser and click through the generated files.

3. Send over SMTP (optional):

```bash
uv run python send_email.py \
  --html preview_output/ready_to_send.html \
  --to recipient@example.com \
  --subject "Automated Markdown Newsletter"
```
