# Client library to export and use by clients
from shared.communicatable import Communicatable
from shared.connectible import Connectible
from shared.mta import Broker

import smtplib
import imapclient
import ssl


class EBMC:
    def __init__(self, client_email_addr):
        self.id = -1

        self.mta = Broker(client_email_addr)

    # returns an ID
    def register(self, email, password) -> int:
        return 1

    def login(self, email, password) -> bool:
        pass
