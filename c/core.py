# Client library to export and use by clients
from shared.communicatable import Communicatable
from shared.connectible import Connectible
from shared.mta import Broker

import smtplib
import imapclient
import ssl


class EBMC:
    def __init__(self, client_email_addr, server_addr):
        self.server_addr = server_addr
        self.id = -1

        self.mta: Communicatable = Broker(client_email_addr)

        # TODO: This needs tuning, i realized we aren't seeing the addresses correctly
        self.mta.connect(self.client_email_addr)

    # returns an ID
    def register(self, email, password):
        subject = {
            topic: 'REGISTER',
            protocol: 3
        }

        self.mta.send(self.server_addr, subject, '')

    def login(self, email, password):
        subject = {
            topic: 'LOGIN',
            protocol: 3
        }

        self.mta.send(self.server_addr, subject, '')

    def add_email(self, email):
        pass
