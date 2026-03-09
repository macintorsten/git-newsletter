import argparse
import smtplib
import os
import sys
from email.message import EmailMessage
from dotenv import load_dotenv


def main():
    load_dotenv()  # Loads SMTP config from a local .env file

    parser = argparse.ArgumentParser(description="Send an HTML email via SMTP.")
    parser.add_argument("--html", required=True, help="Path to the HTML file to send")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", required=True, help="Email subject line")
    args = parser.parse_args()

    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT", 587)
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    sender_email = os.getenv("SENDER_EMAIL", smtp_user)

    if not all([smtp_server, smtp_user, smtp_pass]):
        print("Error: Missing SMTP credentials in environment or .env file.")
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
        print(f"Connecting to {smtp_server}...")
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print(f"Success! Email sent to {args.to}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
