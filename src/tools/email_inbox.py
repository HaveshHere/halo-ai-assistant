from email import policy
from email.parser import BytesParser
from pathlib import Path


def _parse_sample_emails(path="data/emails.txt"):
    email_path = Path(path)

    if not email_path.exists():
        return {"ok": False, "error": "Sample email file is missing: data/emails.txt.", "emails": []}

    content = email_path.read_text().strip()
    if not content:
        return {"ok": True, "error": None, "emails": []}

    emails = []
    blocks = content.split("\n\n")

    for block in blocks:
        email = {"from": "Unknown sender", "subject": "No subject", "date": "Sample data"}

        for line in block.splitlines():
            if line.startswith("From: "):
                email["from"] = line.removeprefix("From: ")
            elif line.startswith("Subject: "):
                email["subject"] = line.removeprefix("Subject: ")

        emails.append(email)

    return {"ok": True, "error": None, "emails": emails}


def fetch_recent_emails():
    return _parse_sample_emails()