# Markdown Mailer

A containerized utility to convert Markdown and CSS into inline-styled, email-ready HTML, and send it. It uses `uv` for lightning-fast dependency management.

---

## Project Structure

```
git-newsletter/
├── .devcontainer/
│   ├── devcontainer.json
│   └── Dockerfile
├── examples/
│   ├── example_input.md        ← Rich newsletter Markdown example
│   └── styles/
│       ├── 01-clean-blue.css       ← Crisp, modern default
│       ├── 02-dark-mode.css        ← Sleek dark theme
│       ├── 03-corporate-green.css  ← Professional emerald
│       ├── 04-warm-sunset.css      ← Vibrant orange/coral
│       ├── 05-terminal-hacker.css  ← Monospace green-on-black
│       ├── 06-elegant-serif.css    ← Refined editorial
│       ├── 07-purple-gradient.css  ← Bold violet gradient
│       ├── 08-ocean-breeze.css     ← Calm cool coastal
│       ├── 09-retro-pop.css        ← Bold 90s zine aesthetic
│       └── 10-minimalist-rose.css  ← Soft warm rose palette
├── pyproject.toml
├── build_email.py
├── send_email.py
└── README.md
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
```

Swap `01-clean-blue.css` for any other style from `examples/styles/` to change the look.

### 3. Send the Email

Create a `.env` file in the root directory with your SMTP credentials:

```dotenv
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASS=your_app_password
SENDER_EMAIL=your_email@example.com
```

> **Important:** The `.env` file is listed in `.gitignore` and will never be committed.

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

### `build_email.py`

Converts a Markdown file + CSS stylesheet into a single inline-styled HTML file ready for email clients.

| Argument | Required | Description |
|----------|----------|-------------|
| `--markdown` | ✅ | Path to the input `.md` file |
| `--style` | ✅ | Path to the input `.css` file |
| `--output` | ✅ | Path to write the output `.html` file |

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