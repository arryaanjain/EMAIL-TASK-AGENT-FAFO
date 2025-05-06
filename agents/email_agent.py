from utils.formatter import summarize_and_extract
from utils.email_reader import fetch_unread_emails

def process_emails():
    emails = fetch_unread_emails()

    for subject, body in emails:
        summary, tasks = summarize_and_extract(subject, body)
        if summary is None:
            break

        print(f"\n📧 Subject: {subject}")
        print(f"📝 Summary: {summary}")
        print(f"✅ Tasks: {tasks}")

