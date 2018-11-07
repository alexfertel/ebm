import imapclient
import smtplib
import ssl


class Connectible:
    def __init__(self, email_addr):
        self.client_email_addr = email_addr

        # SMTP and IMAP instances needed for communication
        self.smtp: smtplib.SMTP = None
        self.imap: imapclient.IMAPClient = None

    def connect(self, addr, through_ssl=False):
        self.smtp = smtplib.SMTP(addr)  # smtp instance
        self.smtp.set_debuglevel(1)

        # If ssl needed turn on the through_ssl flag
        if through_ssl:
            ssl_context = ssl.create_default_context()

            ssl_context.check_hostname = False

            ssl_context.verify_mode = ssl.CERT_NONE

            self.imap = imapclient.IMAPClient(addr, ssl_context=ssl_context)
        else:
            self.imap = imapclient.IMAPClient(addr)

    def disconnect(self):
        self.smtp.quit()
        self.imap.shutdown()

