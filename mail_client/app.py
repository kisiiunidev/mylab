import smtplib, os, sys, ssl
from email.message import EmailMessage
from email.headerregistry import Address
from pathlib import Path
from time import strftime

env_file = Path(__file__).parent / ".env"
for line in env_file.read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ[k] = v.strip()

password = os.environ["SMTP_PASS"]
sender = os.environ["SENDER_EMAIL"]
sender_name = os.environ["SENDER_NAME"]

def get_args():
    recipient = sys.argv[1] if len(sys.argv) > 1 else "eliezerkenya@proton.me"
    subject   = sys.argv[2] if len(sys.argv) > 2 else "Linux Logs"
    body      = sys.argv[3] if len(sys.argv) > 3 else "Hello there, seems nothing's wrong or no arg parsed here."
    return {"to": recipient, "subject": subject, "body": body}

def mail_service():
    args = get_args()

    msg = EmailMessage()
    msg["Subject"] = args["subject"]
    msg["From"] = Address(display_name=sender_name, addr_spec=sender)
    msg["To"] = args["to"]
    msg.set_content(args["body"])

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
        try:
            s.login(sender, password)
            s.send_message(msg)
            print(f"#1: | {strftime('%H:%M:%S')} | {msg['To']} | {msg['Subject']}")
        except:
            print(f"\n#0: | {strftime('%H:%M:%S')} | {msg['To']} | {msg['Subject']}\n")

if __name__ == "__main__":
    try:
        mail_service()
    except:
        print("Not sent!")
