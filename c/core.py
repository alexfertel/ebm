# Client library to export and use by clients
from shared.communicatable import Communicatable
from shared.connectible import Connectible

import smtplib
import imapclient
import ssl


class EBMC(Connectible, Communicatable):
    def __init__(self, client_email_addr):
        super().__init__(client_email_addr)
        self.id = -1

    # returns an ID
    def register(self, email, password) -> int:
        return 1

    def login(self, email, password) -> bool:
        pass
