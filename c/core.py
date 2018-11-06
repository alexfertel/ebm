# Client library to export and use by clients
from ..shared.message import Message
from ..shared.block import Block
import smtplib
import imapclient
import ssl


class EBMC:
    def __init__(self, client_email_addr):
        self.client_email_addr = client_email_addr
        self.id = -1

        # SMTP and IMAP instances needed for communication
        self.smtp: smtplib.SMTP = None
        self.imap: imapclient.IMAPClient = None

    def connect(self, server_addr, through_ssl=False):
        self.smtp = smtplib.SMTP(server_addr)  # smtp instance
        self.smtp.set_debuglevel(1)

        # If ssl needed turn on the through_ssl flag
        if through_ssl:
            ssl_context = ssl.create_default_context()

            ssl_context.check_hostname = False

            ssl_context.verify_mode = ssl.CERT_NONE

            self.imap = imapclient.IMAPClient(server_addr, ssl_context=ssl_context)
        else:
            self.imap = imapclient.IMAPClient(server_addr)

    def disconnect(self):
        self.smtp.quit()
        self.imap.shutdown()

    def send(self, address, msg):
        """
        This method contains the logic for sending an email, which comprises of:
        - Checking the length of the message.
        - Splitting it accordingly in case of being to large.
        - Building the blocks and messages identifiers.
        - Building correctly the emails according to the email library
        - Notiifying the consumer app of the result.
        :param address: email address
        :param msg: text
        :return: bool
        """
        block = Block()

        while len(msg) > 2.4e+7:
            pass

    def recv(self):
        pass

    # returns an ID
    def register(self, email, password) -> int:
        return 1

    def login(self, email, password) -> bool:
        pass
