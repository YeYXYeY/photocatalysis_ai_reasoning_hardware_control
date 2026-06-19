import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


def send_email(sender, password, receiver, subject, body):
    """Send a plain-text email through the QQ SMTP service."""
    smtp_server = "smtp.qq.com"
    smtp_port = 465  # QQ SMTP over SSL

    message = MIMEText(body, "plain", "utf-8")
    message["From"] = formataddr(("Sender", sender))
    message["To"] = formataddr(("Recipient", receiver))
    message["Subject"] = subject

    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender, password)
        server.sendmail(sender, [receiver], message.as_string())
        server.quit()
        print("Email sent successfully.")
    except smtplib.SMTPException as e:
        print("Failed to send email.", e)


if __name__ == "__main__":
    send_email(
        sender="1973334350@qq.com",
        password="fagpheudpzkveaba",
        receiver="Ye.YuanXiang@outlook.com",
        subject="Python SMTP Email Test",
        body="This is a test email sent from a Python script.",
    )
