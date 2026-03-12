#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jinja2>=3.1.4",
# ]
# ///
"""Generate fixed-width (600 px) + flowing example HTML previews and a single index.

All output files are written into preview_output/generated_html/.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


ROOT = Path(__file__).resolve().parent
MARKDOWN_FILE = ROOT / "samples/email/vscode-weekly-newsletter-2026-03-10.md"
STYLES_DIR = ROOT / "assets/email/styles"
OUTPUT_DIR = ROOT / "preview_output/generated_html"
INDEX_TEMPLATE = ROOT / "assets/email/templates/index.html.j2"


def run_build(
    style_file: Path,
    output_file: Path,
    max_width: str | None = None,
    no_max_width: bool = False,
) -> None:
    cmd = [
        sys.executable,
        str(ROOT / "build_email.py"),
        "--markdown",
        str(MARKDOWN_FILE),
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


def main() -> int:
    if not MARKDOWN_FILE.exists():
        raise FileNotFoundError(f"Missing markdown file: {MARKDOWN_FILE}")
    if not STYLES_DIR.exists():
        raise FileNotFoundError(f"Missing styles directory: {STYLES_DIR}")
    if not INDEX_TEMPLATE.exists():
        raise FileNotFoundError(f"Missing index template: {INDEX_TEMPLATE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    style_files = sorted(STYLES_DIR.glob("*.css"))
    if not style_files:
        raise RuntimeError(f"No CSS styles found in: {STYLES_DIR}")

    cards: list[dict[str, str]] = []
    for style_file in style_files:
        stem = style_file.stem
        fixed_name = f"{stem}-fixed.html"
        flowing_name = f"{stem}-flowing.html"

        # Fixed width: 600 px is the widely accepted safe email column width.
        run_build(style_file=style_file, output_file=OUTPUT_DIR / fixed_name)
        # Flowing: no max-width, fills the reader's window.
        run_build(
            style_file=style_file,
            output_file=OUTPUT_DIR / flowing_name,
            no_max_width=True,
        )

        cards.append(
            {
                "title": stem.replace("-", " ").title(),
                "style_file": style_file.name,
                "fixed_file": fixed_name,
                "flowing_file": flowing_name,
            }
        )

    render_index(cards)
    print(f"Generated {len(style_files) * 2} HTML previews in: {OUTPUT_DIR}")
    print(f"Gallery index: {OUTPUT_DIR / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
