# Client library to export and use by clients
import email


class EBMC:
    def __init__(self, client_email_addr):
        self.client_email_addr = client_email_addr
        self.id = -1

    def connect(self, server_addr):
        pass

    def send(self, address, msg):
        """
        This method contains the logic for sending an email, which comprises of:
        - Checking the length of the email.
        - Splitting it accordingly in case of being to large.
        - Building the blocks and messages identifiers.
        - Building correctly the emails according to the email library
        - Notiifying the consumer app of the result.
        :param address: email address
        :param msg: text
        :return: bool
        """
        pass

    def recv(self):
        pass

    # returns an ID
    def register(self, email, password) -> int:
        return 1

    def login(self, email, password) -> bool:
        pass
