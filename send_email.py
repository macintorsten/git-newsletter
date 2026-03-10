import argparse
import smtplib
import os
import sys
from email.message import EmailMessage


def main():
    try:
        from dotenv import load_dotenv
    except ImportError as exc:
        print(
            "Error: missing dependency 'python-dotenv'. Install dependencies with '\\n"
            "  uv sync\\n"
            "or use a venv and pip before running this script.",
            file=sys.stderr,
        )
        print(f"Import error: {exc}", file=sys.stderr)
        sys.exit(1)

    load_dotenv()  # Loads SMTP config from a local .env file

    parser = argparse.ArgumentParser(description="Send an HTML email via SMTP.")
    parser.add_argument("--html", required=True, help="Path to the HTML file to send")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", required=True, help="Email subject line")
    parser.add_argument(
        "--smtp-server",
        default=os.getenv("SMTP_SERVER"),
        help="SMTP server hostname (defaults to SMTP_SERVER env var)",
    )
    parser.add_argument(
        "--smtp-port",
        type=int,
        default=int(os.getenv("SMTP_PORT", "587")),
        help="SMTP server port (defaults to SMTP_PORT env var or 587)",
    )
    parser.add_argument(
        "--smtp-user",
        default=os.getenv("SMTP_USER"),
        help="SMTP username (defaults to SMTP_USER env var)",
    )
    parser.add_argument(
        "--smtp-pass",
        default=os.getenv("SMTP_PASS"),
        help="SMTP password (defaults to SMTP_PASS env var)",
    )
    parser.add_argument(
        "--sender-email",
        default=os.getenv("SENDER_EMAIL"),
        help="From address (defaults to SENDER_EMAIL env var, then SMTP user)",
    )
    parser.add_argument(
        "--no-starttls",
        action="store_true",
        help="Disable STARTTLS (useful for local SMTP catchers)",
    )
    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="Disable SMTP AUTH login (useful for local SMTP catchers)",
    )
    args = parser.parse_args()

    smtp_server = args.smtp_server
    smtp_port = args.smtp_port
    smtp_user = args.smtp_user
    smtp_pass = args.smtp_pass
    sender_email = args.sender_email or smtp_user

    if not smtp_server:
        print("Error: Missing SMTP server. Set SMTP_SERVER or pass --smtp-server.")
        sys.exit(1)
    if not args.no_auth and not all([smtp_user, smtp_pass]):
        print("Error: Missing SMTP credentials. Set SMTP_USER/SMTP_PASS or pass --no-auth.")
        sys.exit(1)
    if not sender_email:
        print("Error: Missing sender email. Set SENDER_EMAIL or pass --sender-email.")
        sys.exit(1)

    try:
        with open(args.html, "r", encoding="utf-8") as file:
            html_content = file.read()
    except FileNotFoundError:
        print(f"Error: Could not find HTML file {args.html}")
        sys.exit(1)

    msg = EmailMessage()
    msg["Subject"] = args.subject
    msg["From"] = sender_email
    msg["To"] = args.to
    msg.set_content("Please enable HTML to view this email.")
    msg.add_alternative(html_content, subtype="html")

    try:
        print(f"Connecting to {smtp_server}:{smtp_port}...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if not args.no_starttls:
                server.starttls()
            if not args.no_auth:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print(f"Success! Email sent to {args.to}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
