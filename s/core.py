# Entry point and loop of the server
from .mta import Broker


class EBMS:
    def __init__(self, email_addr):
        # init broker
        self.broker = Broker()

        # set server email
        self.email_addr = email_addr

    def connect(self, email):
        pass

    def send(self, email, msg):
        pass

    def recv(self):
        pass

    def listen(self):
        while True:
            pass
