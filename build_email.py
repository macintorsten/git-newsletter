# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "markdown>=3.5.2",
#   "css-inline>=0.20.0",
# ]
# ///

import argparse
import sys
from html.parser import HTMLParser


if sys.version_info < (3, 11):
    sys.stderr.write(
        "Error: build_email.py requires Python 3.11+; got {}.{}.{}\n".format(
            sys.version_info[0],
            sys.version_info[1],
            sys.version_info[2],
        )
    )
    sys.stderr.write("Use 'uv run build_email.py' to let uv select a compatible interpreter.\n")
    raise SystemExit(1)


class _BodyWrapper(HTMLParser):
    """Rewrite the HTML stream so that inline styles on <body> are moved to an
    inner <div> wrapper instead.

    Gmail (and several other clients) strip all attributes from the <body>
    element when a message is forwarded, discarding background colour, padding,
    max-width, and every other style inlined there.  Keeping those styles on a
    plain <div> inside the body ensures they survive forwarding intact.

    Using HTMLParser rather than regex avoids brittle edge-cases around escaped
    quotes or unusual attribute ordering in the serialised output.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self._out: list[str] = []
        self._div_opened = False

    def handle_decl(self, decl: str) -> None:
        self._out.append(f"<!{decl}>")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "body":
            style = next((v for k, v in attrs if k == "style"), None)
            other_attrs = "".join(
                f' {k}="{v}"' if v is not None else f" {k}"
                for k, v in attrs
                if k != "style"
            )
            self._out.append(f"<body{other_attrs}>")
            if style:
                self._out.append(f'<div style="{style}">')
                self._div_opened = True
        else:
            attr_str = "".join(
                f' {k}="{v}"' if v is not None else f" {k}" for k, v in attrs
            )
            self._out.append(f"<{tag}{attr_str}>")

    def handle_endtag(self, tag: str) -> None:
        if tag == "body" and self._div_opened:
            self._out.append("</div>")
            self._div_opened = False
        self._out.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        self._out.append(data)

    def handle_comment(self, data: str) -> None:
        self._out.append(f"<!--{data}-->")

    def handle_entityref(self, name: str) -> None:
        self._out.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self._out.append(f"&#{name};")

    def handle_pi(self, data: str) -> None:
        self._out.append(f"<?{data}>")

    def result(self) -> str:
        return "".join(self._out)


def _wrap_body_content(html: str) -> str:
    """Move inline styles from <body> to an inner <div> wrapper."""
    wrapper = _BodyWrapper()
    wrapper.feed(html)
    return wrapper.result()


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to Email-Ready HTML.")
    parser.add_argument("--markdown", required=True, help="Path to input Markdown file")
    parser.add_argument("--style", required=True, help="Path to input CSS file")
    parser.add_argument("--output", required=True, help="Path to save the output HTML file (Required)")
    width_group = parser.add_mutually_exclusive_group()
    width_group.add_argument(
        "--max-width",
        required=False,
        help="Override body max-width (for example: 800px, 70ch, 90%%).",
    )
    width_group.add_argument(
        "--no-max-width",
        action="store_true",
        help="Remove max-width constraint for a flowing, full-width layout.",
    )
    args = parser.parse_args()

    try:
        import css_inline
        import markdown
    except ImportError as exc:
        print(
            "Error: missing dependency. Run this script with:\n"
            "  uv run build_email.py\n"
            "to let uv resolve dependencies automatically.",
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
    if args.no_max_width:
        # box-sizing: border-box ensures padding is included in the 100% width
        # rather than added on top of it, which would cause a horizontal scrollbar.
        width_override = (
            "\nbody { max-width: none !important; width: 100% !important;"
            " box-sizing: border-box !important; }\n"
        )
    elif args.max_width:
        width_override = (
            "\nbody {{ max-width: {0} !important;"
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

    # Inline the CSS.
    # keep_at_rules=True preserves @media queries for clients that support them.
    # css_inline (Rust-based) correctly handles pseudo-selectors like
    # tr:nth-child(even) that premailer silently dropped.
    inliner = css_inline.CSSInliner(keep_at_rules=True)
    email_ready_html = inliner.inline(full_html)

    # Move inline styles from <body> to an inner <div> wrapper.
    # Gmail strips <body> attributes when an email is forwarded, so any styling
    # on the body element (background colour, padding, max-width…) would be
    # lost.  Keeping those styles on a regular <div> inside the body ensures
    # they survive forwarding.
    email_ready_html = _wrap_body_content(email_ready_html)

    # Save output
    with open(args.output, "w", encoding="utf-8") as out_file:
        out_file.write(email_ready_html)

    print("Successfully generated email HTML at: {}".format(args.output))


if __name__ == "__main__":
    main()
