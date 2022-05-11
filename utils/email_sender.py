import os
import smtplib
from email.header import Header
from email.utils import formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import win32com.client as win32

from constants import __PROD__, SEND_EMAIL
from logger import logger


PORT = 587
HOST = 'smtp.gmail.com'
SENDER = os.getenv('EMAIL_SENDER')
TO = [os.getenv('EMAIL_RECEIVER')]

CHT_OA_HOSTNAME = os.getenv('CHT_OA_HOSTNAME')

EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')


def send_email(
    subject: str, content: str, assign_receivers: Optional[List[str]] = None
) -> None:
    if not SEND_EMAIL:
        return

    if 'COMPUTERNAME' in os.environ and os.environ['COMPUTERNAME'] == CHT_OA_HOSTNAME:
        # CHT OA, use native outlook app
        outlook = win32.Dispatch('Outlook.Application')
        mail = outlook.CreateItem(0)
        mail.To = assign_receivers if assign_receivers is not None else ", ".join(TO)
        mail.Subject = subject
        mail.Body = content
        # mail.HTMLBody = '<h2>HTML Message body</h2>'  # this field is optional

        # To attach a file to the email (optional):
        # attachment = "Path to the attachment"
        # mail.Attachments.Add(attachment)

        mail.Send()
        logger.info("email sent from CHT OA's outlook")

    else:
        email_content = MIMEMultipart()
        email_content["subject"] = subject
        email_content["from"] = formataddr((str(Header('Maven 梅文', 'utf-8')), SENDER))
        email_content["to"] = (
            assign_receivers if assign_receivers is not None else ", ".join(TO)
        )
        email_content.attach(MIMEText(content))

        with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp_sender:
            smtp_sender.ehlo()
            smtp_sender.starttls()
            smtp_sender.login(SENDER, str(EMAIL_PASSWORD))
            smtp_sender.send_message(email_content)
            logger.info('email sent')
