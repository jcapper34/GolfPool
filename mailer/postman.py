import os
from email.message import EmailMessage
import smtplib

from helpers import CURRENT_YEAR
import logger

class Postman:
    MAIL_SERVER = os.getenv('GOLF_POOL_EMAIL_SERVER')
    MAIL_PORT = os.getenv('GOLF_POOL_EMAIL_PORT')
    SENDER_EMAIL = os.getenv('GOLF_POOL_EMAIL_ADDRESS')
    SENDER_PASSWORD = os.getenv('GOLF_POOL_EMAIL_PASSWORD')

    def __init__(self, recipients, message_subject="Golf Pool %d" % CURRENT_YEAR, message_body=None) -> None:   # Recipients needs to be list or tuple
        self.recipients = recipients
        self.message_subject = message_subject
        self.message_body = message_body

    def send_message(self) -> None:
        logger.info("Sending email to %s" % str(self.recipients))    

        msg = EmailMessage()
        msg['From'] = self.SENDER_EMAIL
        msg['To'] = self.recipients
        msg['Subject'] = self.message_subject
        msg.set_content(self.message_body)

        with smtplib.SMTP(self.MAIL_SERVER, port=self.MAIL_PORT) as smtp_server:
            smtp_server.ehlo()
            smtp_server.starttls()
            smtp_server.login(self.SENDER_EMAIL, self.SENDER_PASSWORD)
            smtp_server.send_message(msg)

        logger.info("Email sent successfully to %s" % str(self.recipients))        

    def make_picks_message(self, ps_name, ps_pin, picks, update=False) -> None: #Picks must be level separated
        self.message_body = "Name: %s\n" % ps_name
        if update:
            self.message_subject = "Golf Pool %d - Updated Picks for %s" % (CURRENT_YEAR, ps_name)
        else:
            self.message_subject  = "Golf Pool %d - Picks for %s" % (CURRENT_YEAR, ps_name)
            self.message_body += "PIN: %s\n\n" % ps_pin


        level = 1
        for level_picks in picks:
            self.message_body += "\nLevel %d\n" % level
            for player in level_picks:
                self.message_body += "%s\n" % player.name
            level += 1