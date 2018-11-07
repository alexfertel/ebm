# Entry point and loop of the server
from shared.communicatable import Communicatable
from shared.connectible import Connectible
from shared.mta import Broker


class EBMS(Connectible, Communicatable):
    def __init__(self, server_email_addr):
        super().__init__(server_email_addr)

        # init broker
        self.broker = Broker()

    def listen(self):
        while True:
            pass
