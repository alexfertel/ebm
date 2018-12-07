# Client library to export and use by clients
import copy
import time

from src.mta import Broker
from src.decorators import thread
from src.config import PROTOCOLS, TOPICS
from src.utils import *
from src.user import User


# self, server_email_addr: str,
#                  join_addr: str,
#                  server: str,
#                  pwd: str,
#                  ip_addr: str,
#                  user_email: str = ''


class EBMC:
    def __init__(self, user, client_email_addr, server_addr, pwd):
        """
        :rtype:
        :param user: user to login in server
        :param client_email_addr: email
        :param server_addr: server
        :param pwd: password
        """
        self.server_addr = server_addr
        self.id = -1

        self.server_info = User(user, client_email_addr, user, pwd)

        self.mta = Broker(server_addr, self.server_info)

        self.user = ''
        self.token = ''

        # TODO: This needs tuning, i realized we aren't seeing the addresses correctly

    # returns an ID
    @thread
    def register(self, user, password):
        content = user+'\n'+password+'\n'+self.server_info.active_email
        msg = self.mta.build_message(
            body= content,
            protocol=PROTOCOLS['CONFIG'],
            topic=TOPICS['REGISTER']
        )

        msg.send(self.mta, self.server_addr)

        item = None
        while not item:
            item = in_queue(msg.id, copy.deepcopy(self.mta.config_queue))
            if item is not None:
                self.token = item.text
                break
            time.sleep(1)

    @thread
    def login(self, user, password):
        msg = self.mta.build_message(body=user+'\n'+password, protocol=PROTOCOLS['CONFIG'], topic=TOPICS['LOGIN'])
        msg.send(self.mta, self.server_addr)

        item = None
        while not item:
            item = in_queue(msg.id, copy.deepcopy(self.mta.config_queue))
            if item is not None:
                self.token = item.text
                break
            time.sleep(1)

    @thread
    def send(self, user: str, data: str, name: str):
        """"
        :param user:  user to send
        :param data:
        :param name: name of package
        """
        msg = self.mta.build_message(body=user, protocol=PROTOCOLS['CONFIG'], topic=TOPICS['CMD'])
        msg.send(self.mta, self.server_addr)
        item = None
        while not item:
            item = in_queue(msg.id, copy.deepcopy(self.mta.config_queue))
            if item is not None:
                email = item.text
                self.mta.config_queue.remove(item)
                msg_data = self.mta.build_message(body=data, protocol=PROTOCOLS['DATA'], topic=TOPICS['ANSWER'],
                                                  name=name, user=self.user, token=self.token)
                msg_data.send(self.mta, email)
                break
            time.sleep(1)

    @thread
    def publish(self, event: str, data: str, name: str):
        """"
        :param event: name of event
        :param data: data to publish
        :param name: name of package
        """
        msg = self.mta.build_message(body=event, protocol=PROTOCOLS['CONFIG'], topic=TOPICS['PUBLICATION'])
        msg.send(self.mta, self.server_addr)
        item = None
        while not item:
            item = in_queue(msg.id, copy.deepcopy(self.mta.config_queue))
            if item is not None:
                emails = item.text.split(';')
                self.mta.config_queue.remove(item)
                msg_data = self.mta.build_message(body=data, protocol=PROTOCOLS['DATA'], topic=TOPICS['PUBLICATION'],
                                                  name=name, user=self.user, token=self.token)
                for email in emails:
                    msg_data.send(self.mta, email)
                break
            time.sleep(1)

    @thread
    def create_event(self, name: str):
        msg = self.mta.build_message(body=name, protocol=PROTOCOLS['CONFIG'], topic=TOPICS['CREATE'], token=self.token)
        msg.send(self.mta, self.server_addr)

    @thread
    def subscribe(self, event: str):
        msg = self.mta.build_message(body=event, protocol=PROTOCOLS['CONFIG'], topic=TOPICS['SUBSCRIPTION'], token=self.token)
        msg.send(self.mta, self.server_addr)

    @thread
    def unsubscribe(self, event: str):
        msg = self.mta.build_message(body=event, protocol=PROTOCOLS['CONFIG'], topic=TOPICS['UNSUBSCRIPTION'], token=self.token)
        msg.send(self.mta, self.server_addr)

    @property
    def recived(self) -> tuple:
        """
        :return: list: (id_message, name_location)
        """
        return self.mta.complete_messages

    def add_email(self, email):
        pass
