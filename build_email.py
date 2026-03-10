import argparse
import sys


if sys.version_info < (3, 11):
    sys.stderr.write(
        "Error: build_email.py requires Python 3.11+; got {}.{}.{}\n".format(
            sys.version_info[0],
            sys.version_info[1],
            sys.version_info[2],
        )
    )
    sys.stderr.write("Use 'python3' or 'uv run python'.\n")
    raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to Email-Ready HTML.")
    parser.add_argument("--markdown", required=True, help="Path to input Markdown file")
    parser.add_argument("--style", required=True, help="Path to input CSS file")
    parser.add_argument("--output", required=True, help="Path to save the output HTML file (Required)")
    parser.add_argument(
        "--max-width",
        required=False,
        help="Override body max-width (for example: 800px, 70ch, 90%%).",
    )
    args = parser.parse_args()

    try:
        import markdown
        from premailer import transform
    except ImportError as exc:
        print(
            "Error: missing dependency. Install project dependencies with '\\n"
            "  uv sync\\n"
            "or use a venv and pip before running this script.",
            file=sys.stderr,
        )
        print("Import error: {}".format(exc), file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.markdown, "r", encoding="utf-8") as md_file:
            md_content = md_file.read()

        with open(args.style, "r", encoding="utf-8") as css_file:
            css_content = css_file.read()

    except FileNotFoundError as e:
        print("Error: {}".format(e))
        sys.exit(1)

    # Convert Markdown to HTML
    raw_html = markdown.markdown(md_content, extensions=["extra"])

    # Optional width override, useful when reusing a theme for wider layouts.
    width_override = ""
    if args.max_width:
        width_override = (
            "\nbody {{ max-width: {} !important;"
            " width: 100% !important; box-sizing: border-box; }}\n"
        ).format(args.max_width)

    # Wrap in boilerplate
    full_html = """<!DOCTYPE html>
<html>
<head><style>{css_content}{width_override}</style></head>
<body>{raw_html}</body>
</html>
""".format(
        css_content=css_content,
        width_override=width_override,
        raw_html=raw_html,
    )

    # Inline the CSS
    email_ready_html = transform(full_html)

    # Save output
    with open(args.output, "w", encoding="utf-8") as out_file:
        out_file.write(email_ready_html)

    print("Successfully generated email HTML at: {}".format(args.output))


if __name__ == "__main__":
    main()
