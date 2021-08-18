import os
import sys
import smtplib
import traceback
from email.header import Header
from email.utils import formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List

from constants import __PROD__, SEND_EMAIL

from logger import logger


PORT = 587
HOST = 'smtp.gmail.com'
SENDER = 'mavenfadacai@gmail.com'
TO = ['theshaneyu@smail.nchu.edu.tw']

EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
if EMAIL_PASSWORD is None:
    raise Exception('no email password found in .env')

if __PROD__ and SEND_EMAIL:
    with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(SENDER, str(EMAIL_PASSWORD))  # 登入寄件者gmail
            logger.info('SMTP log in successfully')
        except Exception:
            logger.info(traceback.format_exc())
            logger.info('SMTP fail to log in')
            sys.exit()


def send_email(
    subject: str, content: str, assign_receivers: Optional[List['str']] = None
) -> None:
    if not SEND_EMAIL:
        return

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
