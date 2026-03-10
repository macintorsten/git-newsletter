#!/usr/bin/env python3
"""Generate standard + wide example HTML previews and a single index.

All output files are written into examples/generated_html/.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


ROOT = Path(__file__).resolve().parent
PYTHON_EXE = sys.executable
MARKDOWN_FILE = ROOT / "examples/example_input.md"
STYLES_DIR = ROOT / "examples/styles"
OUTPUT_DIR = ROOT / "examples/generated_html"
INDEX_TEMPLATE = ROOT / "templates/index.html.j2"
WIDE_WIDTH = "700px"


def run_build(style_file: Path, output_file: Path, max_width: str | None = None) -> None:
    cmd = [
        PYTHON_EXE,
        str(ROOT / "build_email.py"),
        "--markdown",
        str(MARKDOWN_FILE),
        "--style",
        str(style_file),
        "--output",
        str(output_file),
    ]
    if max_width:
        cmd.extend(["--max-width", max_width])

    subprocess.run(cmd, check=True)


def render_index(cards: list[dict[str, str]]) -> None:
    env = Environment(loader=FileSystemLoader(str(INDEX_TEMPLATE.parent)), autoescape=True)
    template = env.get_template(INDEX_TEMPLATE.name)
    html = template.render(cards=cards, wide_width=WIDE_WIDTH)
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
        standard_name = f"{stem}.html"
        wide_name = f"{stem}-wide.html"

        run_build(style_file=style_file, output_file=OUTPUT_DIR / standard_name)
        run_build(
            style_file=style_file,
            output_file=OUTPUT_DIR / wide_name,
            max_width=WIDE_WIDTH,
        )

        cards.append(
            {
                "title": stem.replace("-", " ").title(),
                "style_file": style_file.name,
                "standard_file": standard_name,
                "wide_file": wide_name,
            }
        )

    render_index(cards)
    print(f"Generated {len(style_files) * 2} HTML previews in: {OUTPUT_DIR}")
    print(f"Gallery index: {OUTPUT_DIR / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
