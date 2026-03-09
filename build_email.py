import argparse
import markdown
import sys
from premailer import transform


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to Email-Ready HTML.")
    parser.add_argument("--markdown", required=True, help="Path to input Markdown file")
    parser.add_argument("--style", required=True, help="Path to input CSS file")
    parser.add_argument("--output", required=True, help="Path to save the output HTML file (Required)")
    parser.add_argument(
        "--max-width",
        required=False,
        help="Override body max-width (for example: 800px, 70ch, 90%).",
    )
    args = parser.parse_args()

    try:
        with open(args.markdown, "r", encoding="utf-8") as md_file:
            md_content = md_file.read()

        with open(args.style, "r", encoding="utf-8") as css_file:
            css_content = css_file.read()

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Convert Markdown to HTML
    raw_html = markdown.markdown(md_content, extensions=["extra"])

    # Optional width override, useful when reusing a theme for wider layouts.
    width_override = ""
    if args.max_width:
        width_override = (
            "\nbody {"
            f" max-width: {args.max_width} !important;"
            " width: 100% !important;"
            " box-sizing: border-box;"
            " }\n"
        )

    # Wrap in boilerplate
    full_html = f"""<!DOCTYPE html>
<html>
<head><style>{css_content}{width_override}</style></head>
<body>{raw_html}</body>
</html>
"""

    # Inline the CSS
    email_ready_html = transform(full_html)

    # Save output
    with open(args.output, "w", encoding="utf-8") as out_file:
        out_file.write(email_ready_html)

    print(f"Successfully generated email HTML at: {args.output}")


if __name__ == "__main__":
    main()
