# Markdown Mailer + Git Newsletter Editor

A containerized utility to convert Markdown and CSS into inline-styled,
email-ready HTML, send it via SMTP, and — new! — **automatically generate a
developer newsletter** from recent git activity using an AI agent pipeline. It
uses `uv` for lightning-fast dependency management.

---

## ✨ Newsletter Editor (new)

The newsletter editor is an AI-agent pipeline that researches your git
repository and produces a friendly, emoji-filled Markdown newsletter for your
team. It follows an **editor → analyst → researcher → writer** model:

| Role | What it does |
|---|---|
| 📰 **Newsletter Editor** (orchestrator) | Delegates work, makes editorial decisions, confirms output |
| 🔍 **Commit Analyst** | Fetches git data AND writes newsletter articles in a single pass |
| 🌐 **Web Researcher** | Researches deep-dive topics on the internet |
| ✍️ **Newsletter Writer** | Assembles the final polished Markdown newsletter |

See [`.github/agents/FLOW.md`](.github/agents/FLOW.md) for the full
agent interaction diagram with handoffs.

### Quick start

Main path: start with natural language and let `newsletter-editor` orchestrate.

```bash
# 1) Non-interactive kickoff (recommended)
copilot -p "Create a concise weekly engineering newsletter from https://github.com/microsoft/vscode.git. Use branch main, cover the last 7 days, title it Dev Weekly, and write the final markdown to vscode-weekly-newsletter.md." --agent "newsletter-editor" --yolo

# 2) Profile-based kickoff (example)
newsletter_markdown=$(copilot -p "Use profile prompt file .github/prompts/profiles/examples/example-flask-monthly.prompt.md.
Generate a maintainers-focused monthly digest. Respond with only the final newsletter markdown content." --agent "newsletter-editor" --yolo)

printf '%s\n' "$newsletter_markdown" > flask-monthly-newsletter.md
```

Optional prompt files:

- Template: `.github/prompts/profiles/TEMPLATE.prompt.md`
- Example profile: `.github/prompts/profiles/examples/example-vscode-weekly.prompt.md`
- Example profile: `.github/prompts/profiles/examples/example-flask-monthly.prompt.md`

### Agent & skill definitions

The agents are `.agent.md` files in `.github/agents/` that VS Code Copilot
loads automatically. Each agent has `handoffs` in its frontmatter so Copilot
displays action buttons to guide users through the pipeline:

| Path | Purpose |
|---|---|
| `.github/agents/newsletter-editor.agent.md` | Orchestrator / editor |
| `.github/agents/commit-analyst.agent.md` | Git data + article writing (single pass) |
| `.github/agents/web-researcher.agent.md` | Deep-dive topic research |
| `.github/agents/newsletter-writer.agent.md` | Final newsletter assembly |
| `.github/agents/FLOW.md` | Agent interaction diagram |
| `.github/skills/commit-analysis/SKILL.md` | Combined git research + commit analysis skill |
| `.github/skills/commit-analysis/git_skills.py` | Git helper functions used by commit analysis |
| `.github/skills/web-research/SKILL.md` | Web research skill |
| `.github/skills/newsletter-writing/SKILL.md` | Newsletter writing skill (includes emoji instructions) |

### Newsletter structure

A typical output looks like this:

```markdown
# 📰 my-repo Dev Digest
> Covering the last 7 days of activity on `main`.

## 🚀 Newly Shipped (merged to main)
## 🌿 Release Branches
## 🔨 Development Branches
## 🕸️ Stale Branches
```

Deep-dive articles (chosen by the editor for 0–3 important topics) are
rendered as blockquotes directly after the related change:

```markdown
**Merged:** `feature/auth-refresh` by @alice

Brief summary of the change…

> 📖 **Deep Dive: What is OAuth token refresh?**
>
> <web-research article>
>
> 🔗 [Learn more](https://...)
```

## Project Structure

```
git-newsletter/
├── .devcontainer/          # Container setup for local dev
├── .github/
│   ├── agents/             # Copilot agent definitions + flow
│   ├── prompts/            # Optional prompt helpers and profiles
│   │   └── profiles/       # TEMPLATE + example profile configurations
│   └── skills/             # Agent skills and helper scripts
├── examples/               # Sample markdown, styles, generated HTML
├── build_email.py          # Markdown + CSS -> inline HTML
├── send_email.py           # SMTP sender
└── pyproject.toml
```

---

## How to Build and Run Manually (Docker)

If you are not using VS Code Dev Containers, you can run this tool entirely through standard Docker.

### 1. Build the Image

From the root of the project, build the Docker image using the provided `.devcontainer/Dockerfile`.

```bash
docker build -t markdown-mailer -f .devcontainer/Dockerfile .
```

### 2. Generate the Email HTML

Run the container, mounting your current directory (`$PWD`) into the container's `/workspace` so the script can read your inputs and write the output back to your host machine.

```bash
docker run --rm -v "$PWD:/workspace" markdown-mailer python build_email.py \
  --markdown examples/example_input.md \
  --style examples/styles/01-clean-blue.css \
  --output examples/ready_to_send.html

# Optional: generate a wider layout without editing the CSS file
docker run --rm -v "$PWD:/workspace" markdown-mailer python build_email.py \
  --markdown examples/example_input.md \
  --style examples/styles/01-clean-blue.css \
  --output examples/ready_to_send-wide.html \
  --max-width 900px
```

Swap `01-clean-blue.css` for any other style from `examples/styles/` to change the look.

### 3. Send the Email

Copy the provided template to create your `.env` file, then fill in your real SMTP credentials:

```bash
cp .env.example .env
```

The template (`.env.example`) looks like this:

```dotenv
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASS=your_app_password_here
SENDER_EMAIL=your_email@example.com
```

> **Important:** `.env.example` is safe to commit — it contains only placeholder values.  
> The actual `.env` file is listed in `.gitignore` and will never be committed.

Then, run the sender script through Docker:

```bash
docker run --rm -v "$PWD:/workspace" markdown-mailer python send_email.py \
  --html examples/ready_to_send.html \
  --to recipient@example.com \
  --subject "Automated Markdown Newsletter"
```

---

## How to Use with VS Code Dev Containers

1. Open the project folder in VS Code.
2. When prompted, click **"Reopen in Container"** (or run `Dev Containers: Reopen in Container` from the command palette).
3. VS Code will build the Docker image and attach to the container automatically.
4. Run scripts directly in the integrated terminal:

```bash
python build_email.py \
  --markdown examples/example_input.md \
  --style examples/styles/01-clean-blue.css \
  --output examples/ready_to_send.html

# Optional width override
python build_email.py \
  --markdown examples/example_input.md \
  --style examples/styles/01-clean-blue.css \
  --output examples/ready_to_send-wide.html \
  --max-width 900px
```

---

## Available Themes

| File | Style | Palette |
|------|-------|---------|
| `01-clean-blue.css` | Clean Blue | Crisp blue on off-white |
| `02-dark-mode.css` | Dark Mode | Cyan on deep navy |
| `03-corporate-green.css` | Corporate Green | Emerald on mint |
| `04-warm-sunset.css` | Warm Sunset | Orange/coral on cream |
| `05-terminal-hacker.css` | Terminal Hacker | Matrix green on black |
| `06-elegant-serif.css` | Elegant Serif | Gold-trimmed editorial |
| `07-purple-gradient.css` | Purple Gradient | Violet gradient on lavender |
| `08-ocean-breeze.css` | Ocean Breeze | Sky blue on pale aqua |
| `09-retro-pop.css` | Retro Pop | Hot pink & yellow on white |
| `10-minimalist-rose.css` | Minimalist Rose | Rose red on blush white |

---

## Running Locally (without Docker)

If you have Python 3.11+ and `uv` installed locally:

```bash
# Install dependencies
uv pip install -r pyproject.toml

# Build email
python build_email.py \
  --markdown examples/example_input.md \
  --style examples/styles/01-clean-blue.css \
  --output examples/ready_to_send.html

# Send email (requires a configured .env file)
python send_email.py \
  --html examples/ready_to_send.html \
  --to recipient@example.com \
  --subject "My Newsletter"
```

---

## Script Reference

### `generate_examples.py`

Builds all example outputs in one command using:

- `examples/example_input.md`
- Every stylesheet in `examples/styles/`

All generated files are written to `examples/generated_html/`:

- Standard outputs: `<style-name>.html`
- Wide outputs: `<style-name>-wide.html`
- Gallery index: `index.html`

```bash
python generate_examples.py
```

### `build_email.py`

Converts a Markdown file + CSS stylesheet into a single inline-styled HTML file ready for email clients.

| Argument | Required | Description |
|----------|----------|-------------|
| `--markdown` | ✅ | Path to the input `.md` file |
| `--style` | ✅ | Path to the input `.css` file |
| `--output` | ✅ | Path to write the output `.html` file |
| `--max-width` | ❌ | Override `body` max width (e.g. `900px`, `70ch`, `90%`) |

### `send_email.py`

Sends an HTML file as an email via SMTP. Reads credentials from a `.env` file or environment variables.

| Argument | Required | Description |
|----------|----------|-------------|
| `--html` | ✅ | Path to the HTML file to send |
| `--to` | ✅ | Recipient email address |
| `--subject` | ✅ | Email subject line |

**Required environment variables (in `.env`):**

| Variable | Description |
|----------|-------------|
| `SMTP_SERVER` | Hostname of your SMTP server |
| `SMTP_PORT` | SMTP port (default: `587`) |
| `SMTP_USER` | Your SMTP username / email |
| `SMTP_PASS` | Your SMTP password or app password |
| `SENDER_EMAIL` | Sender address (defaults to `SMTP_USER`) |