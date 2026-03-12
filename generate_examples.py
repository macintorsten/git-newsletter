#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jinja2>=3.1.4",
#   "markdown>=3.5.2",
#   "css-inline>=0.20.0",
# ]
# ///
"""Generate fixed-width (600 px) + flowing example HTML previews and a single index.

All output files are written into preview_output/generated_html/.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


if sys.version_info < (3, 11):
    sys.stderr.write(
        "Error: generate_examples.py requires Python 3.11+; got {}.{}.{}\n".format(
            sys.version_info[0],
            sys.version_info[1],
            sys.version_info[2],
        )
    )
    sys.stderr.write("Use 'uv run generate_examples.py' to let uv select a compatible interpreter.\n")
    raise SystemExit(1)


ROOT = Path(__file__).resolve().parent
PROMPTS_DIR = ROOT / ".github/prompts/profiles/examples"
COMMAND_PROMPTS_DIR = ROOT / ".github/prompts"
STYLES_DIR = ROOT / "assets/email/styles"
MARKDOWN_SAMPLES_DIR = ROOT / "samples/email/examples"
OUTPUT_DIR = ROOT / "preview_output/generated_html"
INDEX_TEMPLATE = ROOT / "assets/email/templates/index.html.j2"
REQUIRED_METADATA = {
    "profile_name",
    "repository",
    "branch",
    "period_days",
    "output_path",
    "title_style",
}

EXAMPLE_DEFINITIONS = [
    {
        "prompt_file": "example-vscode-weekly.prompt.md",
        "style_file": "01-clean-blue.css",
        "markdown_file": "vscode-weekly-example.md",
        "summary": "Prompt example for editor and extension-platform coverage, shown here with the clean blue theme.",
    },
    {
        "prompt_file": "example-kubernetes-weekly.prompt.md",
        "style_file": "02-dark-mode.css",
        "markdown_file": "kubernetes-weekly-example.md",
        "summary": "Prompt example for operator-facing infrastructure updates, shown here with the dark mode theme.",
    },
    {
        "prompt_file": "example-flask-monthly.prompt.md",
        "style_file": "03-corporate-green.css",
        "markdown_file": "flask-monthly-example.md",
        "summary": "Prompt example for slower, migration-focused maintainer updates, shown here with the corporate green theme.",
    },
    {
        "prompt_file": "example-nextjs-weekly.prompt.md",
        "style_file": "04-warm-sunset.css",
        "markdown_file": "nextjs-weekly-example.md",
        "summary": "Prompt example for frontend product and platform teams, shown here with the warm sunset theme.",
    },
    {
        "prompt_file": "example-github-cli-weekly.prompt.md",
        "style_file": "05-terminal-hacker.css",
        "markdown_file": "github-cli-weekly-example.md",
        "summary": "Prompt example for terminal-heavy workflows and automation, shown here with the terminal hacker theme.",
    },
    {
        "prompt_file": "example-python-monthly.prompt.md",
        "style_file": "06-elegant-serif.css",
        "markdown_file": "python-monthly-example.md",
        "summary": "Prompt example for language and runtime change reviews, shown here with the elegant serif theme.",
    },
    {
        "prompt_file": "example-react-weekly.prompt.md",
        "style_file": "07-purple-gradient.css",
        "markdown_file": "react-weekly-example.md",
        "summary": "Prompt example for rendering-model and compiler updates, shown here with the purple gradient theme.",
    },
    {
        "prompt_file": "example-deno-weekly.prompt.md",
        "style_file": "08-ocean-breeze.css",
        "markdown_file": "deno-weekly-example.md",
        "summary": "Prompt example for runtime and deploy ergonomics, shown here with the ocean breeze theme.",
    },
    {
        "prompt_file": "example-vite-weekly.prompt.md",
        "style_file": "09-retro-pop.css",
        "markdown_file": "vite-weekly-example.md",
        "summary": "Prompt example for fast-moving frontend tooling, shown here with the retro pop theme.",
    },
    {
        "prompt_file": "example-fastapi-monthly.prompt.md",
        "style_file": "10-minimalist-rose.css",
        "markdown_file": "fastapi-monthly-example.md",
        "summary": "Prompt example for Python API maintainers, shown here with the minimalist rose theme.",
    },
    {
        "prompt_file": "example-postgresql-monthly.prompt.md",
        "style_file": "11-newsprint-ledger.css",
        "markdown_file": "postgresql-monthly-example.md",
        "summary": "Prompt example for database operators and maintainers, shown here with the newsprint ledger theme.",
    },
    {
        "prompt_file": "example-terraform-weekly.prompt.md",
        "style_file": "12-executive-brief.css",
        "markdown_file": "terraform-weekly-example.md",
        "summary": "Prompt example for leadership-friendly infrastructure briefs, shown here with the executive brief theme.",
    },
]


@dataclass(frozen=True)
class ExampleDefinition:
    prompt_file: Path
    style_file: Path
    markdown_file: Path
    summary: str


@dataclass(frozen=True)
class ExampleProfile:
    source_file: Path
    title: str
    body: str
    metadata: dict[str, str]
    command_file: Path

    @property
    def slug(self) -> str:
        return self.source_file.stem.replace(".prompt", "")


def parse_prompt_file(prompt_file: Path) -> ExampleProfile:
    text = prompt_file.read_text(encoding="utf-8")
    heading = next(
        (line[2:].strip() for line in text.splitlines() if line.startswith("# ")),
        prompt_file.stem.replace(".prompt", "").replace("-", " ").title(),
    )
    metadata = parse_metadata_block(text, prompt_file)
    missing = sorted(REQUIRED_METADATA - metadata.keys())
    if missing:
        raise ValueError(f"Missing metadata in {prompt_file}: {', '.join(missing)}")

    command_file = COMMAND_PROMPTS_DIR / f"newsletter-{metadata['profile_name']}.prompt.md"
    if not command_file.exists():
        raise FileNotFoundError(f"Missing command prompt for {prompt_file}: {command_file}")

    return ExampleProfile(
        source_file=prompt_file,
        title=heading.removeprefix("Example Profile: ").strip(),
        body=text,
        metadata=metadata,
        command_file=command_file,
    )


def parse_metadata_block(text: str, prompt_file: Path) -> dict[str, str]:
    metadata: dict[str, str] = {}
    in_block = False
    for line in text.splitlines():
        if line.startswith("- "):
            in_block = True
            match = re.match(r"^-\s+([a-z0-9_]+):\s*(.+?)\s*$", line)
            if not match:
                raise ValueError(f"Invalid metadata line in {prompt_file}: {line}")
            metadata[match.group(1)] = match.group(2)
            continue
        if in_block:
            if not line.strip():
                break
            raise ValueError(
                f"Metadata block must be a contiguous bullet list in {prompt_file}: {line}"
            )
    return metadata


def discover_examples() -> list[tuple[ExampleDefinition, ExampleProfile]]:
    examples: list[tuple[ExampleDefinition, ExampleProfile]] = []
    for item in EXAMPLE_DEFINITIONS:
        prompt_file = PROMPTS_DIR / item["prompt_file"]
        style_file = STYLES_DIR / item["style_file"]
        markdown_file = MARKDOWN_SAMPLES_DIR / item["markdown_file"]
        if not prompt_file.exists():
            raise FileNotFoundError(f"Missing prompt file: {prompt_file}")
        if not style_file.exists():
            raise FileNotFoundError(f"Missing style file: {style_file}")
        if not markdown_file.exists():
            raise FileNotFoundError(f"Missing markdown sample: {markdown_file}")

        example_definition = ExampleDefinition(
            prompt_file=prompt_file,
            style_file=style_file,
            markdown_file=markdown_file,
            summary=item["summary"],
        )
        examples.append((example_definition, parse_prompt_file(prompt_file)))
    return examples


def relpath_for_gallery(path: Path) -> str:
    return Path(os.path.relpath(path, OUTPUT_DIR)).as_posix()


def build_cli_command(profile: ExampleProfile) -> str:
    prompt_path = profile.source_file.relative_to(ROOT).as_posix()
    return (
        "copilot --experimental -p \"Use profile prompt file "
        f"{prompt_path}. Generate a newsletter markdown with the profile defaults. "
        "Apply any override text that follows this instruction. Respond with only the final newsletter markdown.\" "
        '--agent "newsletter-editor" --yolo'
    )


def run_build(
    markdown_file: Path,
    style_file: Path,
    output_file: Path,
    max_width: str | None = None,
    no_max_width: bool = False,
) -> None:
    cmd = [
        sys.executable,
        str(ROOT / "build_email.py"),
        "--markdown",
        str(markdown_file),
        "--style",
        str(style_file),
        "--output",
        str(output_file),
    ]
    if no_max_width:
        cmd.append("--no-max-width")
    elif max_width:
        cmd.extend(["--max-width", max_width])

    subprocess.run(cmd, check=True)


def render_index(cards: list[dict[str, str]]) -> None:
    env = Environment(loader=FileSystemLoader(str(INDEX_TEMPLATE.parent)), autoescape=True)
    template = env.get_template(INDEX_TEMPLATE.name)
    html = template.render(cards=cards)
    (OUTPUT_DIR / "index.html").write_text(html, encoding="utf-8")


def clean_output_dir() -> None:
    for output_file in OUTPUT_DIR.glob("*.html"):
        output_file.unlink()


def main() -> int:
    if not PROMPTS_DIR.exists():
        raise FileNotFoundError(f"Missing prompts directory: {PROMPTS_DIR}")
    if not STYLES_DIR.exists():
        raise FileNotFoundError(f"Missing styles directory: {STYLES_DIR}")
    if not MARKDOWN_SAMPLES_DIR.exists():
        raise FileNotFoundError(f"Missing markdown samples directory: {MARKDOWN_SAMPLES_DIR}")
    if not INDEX_TEMPLATE.exists():
        raise FileNotFoundError(f"Missing index template: {INDEX_TEMPLATE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    clean_output_dir()
    examples = discover_examples()

    cards: list[dict[str, str]] = []
    for example_definition, profile in examples:
        stem = profile.slug
        fixed_name = f"{stem}-fixed.html"
        flowing_name = f"{stem}-flowing.html"

        # Fixed width: 600 px is the widely accepted safe email column width.
        run_build(
            markdown_file=example_definition.markdown_file,
            style_file=example_definition.style_file,
            output_file=OUTPUT_DIR / fixed_name,
        )
        # Flowing: no max-width, fills the reader's window.
        run_build(
            markdown_file=example_definition.markdown_file,
            style_file=example_definition.style_file,
            output_file=OUTPUT_DIR / flowing_name,
            no_max_width=True,
        )

        cards.append(
            {
                "title": profile.title,
                "summary": example_definition.summary,
                "profile_name": profile.metadata["profile_name"],
                "repository": profile.metadata["repository"],
                "branch": profile.metadata["branch"],
                "period_days": profile.metadata["period_days"],
                "title_style": profile.metadata["title_style"],
                "style_file": example_definition.style_file.name,
                "style_name": example_definition.style_file.stem.replace("-", " ").title(),
                "prompt_file": relpath_for_gallery(profile.source_file),
                "prompt_file_label": profile.source_file.relative_to(ROOT).as_posix(),
                "command_file": relpath_for_gallery(profile.command_file),
                "command_file_label": profile.command_file.relative_to(ROOT).as_posix(),
                "markdown_file": relpath_for_gallery(example_definition.markdown_file),
                "markdown_file_label": example_definition.markdown_file.relative_to(ROOT).as_posix(),
                "prompt_body": profile.body,
                "slash_command": f"/{profile.command_file.stem.replace('.prompt', '')} [optional overrides]",
                "cli_command": build_cli_command(profile),
                "fixed_file": fixed_name,
                "flowing_file": flowing_name,
            }
        )

    render_index(cards)
    print(f"Generated {len(examples) * 2} HTML previews in: {OUTPUT_DIR}")
    print(f"Gallery index: {OUTPUT_DIR / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
