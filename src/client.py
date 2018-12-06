# Client library to export and use by clients
import copy
import time
import threading

from mta import Broker
from message import Message
from decorators import thread
from config import PROTOCOLS, TOPICS
from .utils import *


class EBMC:
    def __init__(self, client_email_addr, server_addr):
        self.server_addr = server_addr
        self.id = -1

        self.mta: Broker = Broker(client_email_addr)

        self.user = ''
        self.token = ''

        # TODO: This needs tuning, i realized we aren't seeing the addresses correctly
        # self.mta.connect(self.client_email_addr)

    # returns an ID
    @thread
    def register(self, user, password):
        msg = self.mta.build_message(body=f'{user}\n{password}', protocol=PROTOCOLS['CONFIG'], topic=['REGISTER'])
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
        msg = self.mta.build_message(body=f'{user}\n{password}', protocol=PROTOCOLS['CONFIG'], topic=['LOGIN'])
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
        msg = self.mta.build_message(body=f'{user}', protocol=PROTOCOLS['CONFIG'], topic=TOPICS['CMD'])
        msg.send(self.mta, self.server_addr)
        item = None
        while not item:
            item = in_queue(msg.id, copy.deepcopy(self.mta.config_queue))
            if item is not None:
                email = item.text
                self.mta.config_queue.remove(item)
                msg_data = self.mta.build_message(body=f'{data}', protocol=PROTOCOLS['DATA'], topic=TOPICS['ANSWER'],
                                                  name=self.name, user=self.user)
                msg_data.send(self.mta, email)
                break
            time.sleep(1)

    @thread
    def publish(self, event: str, data: str, name: str):
        msg = self.mta.build_message(body=event, protocol=PROTOCOLS['CONFIG'], topic=TOPICS['PUBLICATION'])
        msg.send(self.mta, self.server_addr)
        item = None
        while not item:
            item = in_queue(msg.id, copy.deepcopy(self.mta.config_queue))
            if item is not None:
                emails = item.text.split(';')
                self.mta.config_queue.remove(item)
                msg_data = self.mta.build_message(body=f'{data}', protocol=PROTOCOLS['DATA'], topic=['PUBLICATION'],
                                                  name=name, user=self.user)
                for email in emails:
                    msg_data.send(self.mta, email)
                break
            time.sleep(1)

    @thread
    def create_event(self, name: str):
        msg = self.mta.build_message(body=name, protocol=PROTOCOLS['CONFIG'], topic=TOPICS['CMD'])
        msg.send(self.mta, self.server_addr)

    @thread
    def subscribe(self, event: str):
        msg = self.mta.build_message(body=event, protocol=PROTOCOLS['CONFIG'], topic=['SUBSCRIPTION'])
        msg.send(self.mta, self.server_addr)

    @thread
    def unsubscribe(self, event: str):
        msg = self.mta.build_message(body=event, protocol=PROTOCOLS['CONFIG'], topic=TOPICS['UNSUBSCRIPTION'])
        msg.send(self.mta, self.server_addr)

    def add_email(self, email):
        pass
