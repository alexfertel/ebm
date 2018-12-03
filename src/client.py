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
        Broker.build_message(body=f'{email}\n{password}', )
        # msg = Message(
        #     body=f'{email}\n{password}',
        #     subject={
        #         'topic': 'REGISTER',
        #         'protocol': 3
        #     })

        msg.send(self.mta, [self.server_addr])
        # self.mta.send(f'ebm@{self.server_addr}', msg)

    def login(self, email, password):
        msg = Message(
            body=f'{email}\n{password}',
            subject={
                'topic': 'LOGIN',
                'protocol': 3
            })

        msg.send(self.mta, [self.server_addr])
        # self.mta.send(f'ebm@{self.server_addr}', subject, '')

    def add_email(self, email):
        pass
