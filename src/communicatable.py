from .message import Message
from .block import Block
from .user import User
from imbox import Imbox
from email.message import EmailMessage

import json


class Communicatable:
    def send(self, address: str, user: User, subject: dict, body: str):
        """
        This method contains the logic for sending an email, which comprises of:
        - Connect to the smtp server
        - Checking the length of the message.
        - Splitting it accordingly in case of being to large.
        - Building the blocks and _blocks identifiers.
        - Building correctly the emails according to the email library
        - Make the subject a json
        - Notiifying the consumer app of the result.
        :param address: email address
        :param user: User
        :param subject: str
        :param body: str
        :return: bool
        """
        smtp: smtplib.SMTP = smtplib.SMTP(addr)  # smtp instance
        smtp.set_debuglevel(1)

        json_subject = json.dumps(subject, separators=(',', ':'))  # Make it a json for ease of parsing

        msg = EmailMessage()

        msg['From'] = f'{user.username}@{user.active_email}'
        msg['To'] = address
        msg['Subject'] = json_subject

        msg.set_content(body)

        smtp.send_message(msg)

        smtp.quit()

    def recv(self, addr, user: User):
        """
        This method contains the logic for fetching the next batch of messages
        from the imap server.
        :return: list[Block]
        """

        # if through_ssl:
        ssl_context = ssl.create_default_context()

        ssl_context.check_hostname = False

        ssl_context.verify_mode = ssl.CERT_NONE

        #     self.imap = imapclient.IMAPClient(addr, ssl_context=ssl_context)
        # else:
        #     self.imap = imapclient.IMAPClient(addr)

        unread = []
        with Imbox(addr,
                   username=user.username,
                   password=user.password,
                   ssl=True,
                   ssl_context=ssl_context,
                   starttls=False) as imbox:
            for _, message in imbox.messages(unread=True):
                unread.append(message)  # For now just append to the queue

        return unread
