#!/usr/bin/env python3
import csv, random, datetime, os, smtplib, ssl, textwrap
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# CONFIG (reads secrets from environment variables in GitHub Actions)
CSV_PATH = "questions.csv"
TOPICS = ["Excel", "Power BI", "Tableau", "SQL", "Python"]
PER_TOPIC = 10

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER")      # your email (set as GitHub secret)
SMTP_PASS = os.getenv("SMTP_PASS")      # app password or SMTP password (set as GitHub secret)
TO_EMAIL  = os.getenv("TO_EMAIL")       # recipient email (set as GitHub secret)
FROM_NAME = os.getenv("FROM_NAME", "Daily Interview Bot")

def load_questions(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def select_questions(rows):
    selected = []
    for topic in TOPICS:
        pool = [r for r in rows if r["topic"].strip().lower() == topic.lower()]
        if not pool:
            continue
        # allow repetition: use random.choices; if you prefer random.sample (no repeats) use that
        chosen = random.choices(pool, k=PER_TOPIC)
        selected.extend(chosen)
    return selected

def build_html_email(date_str, selected):
    # Build tidy HTML with Q&A grouped by topic
    html = f"<h2>Daily Data Analyst Questions — {date_str}</h2>"
    for topic in TOPICS:
        html += f"<h3 style='background:#f2f2f2;padding:6px;border-radius:4px'>{topic}</h3><ol>"
        topic_qs = [q for q in selected if q["topic"].strip().lower() == topic.lower()]
        for q in topic_qs:
            qtext = q.get("question","").strip()
            ans = q.get("answer","").strip()
            html += f"<li><b>Q:</b> {qtext}<br><b>A:</b> {ans}</li><br>"
        html += "</ol>"
    html += "<hr><p>Good luck! Reply with feedback.</p>"
    return html

def send_email(subject, html_content):
    if not (SMTP_USER and SMTP_PASS and TO_EMAIL):
        raise RuntimeError("Missing SMTP_USER/SMTP_PASS/TO_EMAIL environment variables.")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{SMTP_USER}>"
    msg["To"] = TO_EMAIL
    part = MIMEText(html_content, "html", "utf-8")
    msg.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, TO_EMAIL, msg.as_string())

def main():
    rows = load_questions(CSV_PATH)
    selected = select_questions(rows)
    today = datetime.date.today().isoformat()
    html = build_html_email(today, selected)
    subject = f"📅 Daily Data Analyst Questions — {today}"
    send_email(subject, html)
    print("Email sent.")

if __name__ == "__main__":
    main()
