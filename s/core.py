# Entry point and loop of the server
# TODO: Refactor sending and receiving logic into another file.
from shared.mta import Broker


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
