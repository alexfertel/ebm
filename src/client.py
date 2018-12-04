# Client library to export and use by clients
from mta import Broker
from message import Message


class EBMC:
    def __init__(self, client_email_addr, server_addr):
        self.server_addr = server_addr
        self.id = -1

        self.mta: Broker = Broker(client_email_addr)

        # TODO: This needs tuning, i realized we aren't seeing the addresses correctly
        # self.mta.connect(self.client_email_addr)

    # returns an ID
    def register(self, email, password):
        msg = self.mta.build_message(body=f'{email}\n{password}', protocol=2, topic='REGISTER')
        msg.send(self.mta, [self.server_addr])

    def login(self, email, password):
        msg = self.mta.build_message(body=f'{email}\n{password}', protocol=2, topic='LOGIN')
        msg.send(self.mta, [self.server_addr])

    def add_email(self, email):
        pass
