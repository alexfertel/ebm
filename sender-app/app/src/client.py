# Client library to export and use by clients
import copy
import time

from .mta import Broker
from .decorators import thread
from .config import PROTOCOLS, TOPICS
from .utils import *
from .user import User

import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('CLIENT')


class EBMC:
    def __init__(self, client_email_addr, email_server, server_email_addr, pwd):
        """
        :param client_email_addr: email
        :param email_server: server
        :param pwd: password
        """
        self.server_email_addr = server_email_addr
        self.email_server = email_server
        self.id = -1

        self.user_info = User(client_email_addr, pwd)

        self.mta: Broker = Broker(email_server, self.user_info)

        self.user = ''
        self.token = ''

        # TODO: This needs tuning, i realized we aren't seeing the addresses correctly

    # returns an ID
    @thread
    def register(self, user, password):
        content = user+'\n'+password+'\n'+self.user_info.active_email
        msg = self.mta.build_message(
            body= content,
            protocol=PROTOCOLS['CONFIG'],
            topic=TOPICS['REGISTER']
        )
        logger.info(f'User: {user} Pass: {password} Server {self.server_email_addr}')
        logger.info(f'Msg is: {msg}')
        msg.send(self.mta, self.server_email_addr)

        item = None
        while not item:
            item = in_queue(msg.id, copy.deepcopy(self.mta.config_queue))
            if item is not None:
                self.token = item.text
                break
            time.sleep(1)

    @thread
    def login(self, user, password):
        msg = self.mta.build_message(body=f'{user}\n{password}', protocol=PROTOCOLS['CONFIG'], topic=TOPICS['LOGIN'])
        msg.send(self.mta, self.server_email_addr)

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
        :param user: user to send
        :param data: data
        :param name: name of package
        """
        msg = self.mta.build_message(body=f'{user}', protocol=PROTOCOLS['CONFIG'], topic=TOPICS['CMD'])
        msg.send(self.mta, self.server_email_addr)
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
        msg.send(self.mta, self.server_email_addr)
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
        msg.send(self.mta, self.server_email_addr)

    @thread
    def subscribe(self, event: str):
        msg = self.mta.build_message(body=event, protocol=PROTOCOLS['CONFIG'], topic=TOPICS['SUBSCRIPTION'], token=self.token)
        msg.send(self.mta, self.server_email_addr)


    @thread
    def unsubscribe(self, event: str):
        msg = self.mta.build_message(body=event, protocol=PROTOCOLS['CONFIG'], topic=TOPICS['UNSUBSCRIPTION'], token=self.token)
        msg.send(self.mta, self.server_email_addr)

    @property
    def recived(self) -> tuple:
        """
        :return: list: (id_message, name_location)
        """
        return self.mta.complete_messages

    def add_email(self, email):
        pass
