# Entry point and loop of the server
from shared.communicatable import Communicatable
from shared.connectible import Connectible
from shared.mta import Broker


class EBMS:
    def __init__(self, server_email_addr):
        # init broker
        self.mta = Broker(server_email_addr)

    def listen(self):
        while True:
            pass
