import argparse
import markdown
import sys
from premailer import transform


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to Email-Ready HTML.")
    parser.add_argument("--markdown", required=True, help="Path to input Markdown file")
    parser.add_argument("--style", required=True, help="Path to input CSS file")
    parser.add_argument("--output", required=True, help="Path to save the output HTML file (Required)")
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

    # Wrap in boilerplate
    full_html = f"""<!DOCTYPE html>
<html>
<head><style>{css_content}</style></head>
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
