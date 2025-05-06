import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
from chardet import detect
import os

load_dotenv()

# Hard token cap for the script
MAX_TOKENS_TOTAL = 20000
tokens_used = 0

def fetch_unread_emails():
    global tokens_used
    user = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    imap_server = os.getenv("EMAIL_IMAP")

    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(user, password)
    mail.select("inbox")

    result, data = mail.search(None, '(UNSEEN)')
    email_ids = data[0].split()
    emails = []

    for eid in email_ids:
        if tokens_used >= MAX_TOKENS_TOTAL:
            print("✅ Token usage limit reached. Stopping to avoid extra charges.")
            break

        res, msg_data = mail.fetch(eid, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, _ = decode_header(msg["Subject"])[0]
                subject = subject.decode() if isinstance(subject, bytes) else subject
                body = ""

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            raw_body = part.get_payload(decode=True)
                            detected = detect(raw_body)
                            encoding = detected['encoding'] or 'utf-8'
                            try:
                                body = raw_body.decode(encoding)
                            except UnicodeDecodeError:
                                body = raw_body.decode('utf-8', errors='replace')
                            break
                else:
                    raw_body = msg.get_payload(decode=True)
                    body = raw_body.decode(errors='replace')

                estimated_tokens = len(subject.split()) + len(body.split())
                if tokens_used + estimated_tokens > MAX_TOKENS_TOTAL:
                    print("⚠️ Token limit would be exceeded. Stopping before API call.")
                    mail.logout()
                    return emails

                tokens_used += estimated_tokens
                emails.append((subject, body))

    mail.logout()
    return emails
