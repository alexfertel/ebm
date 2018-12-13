# Client library to export and use by clients
import copy
import time
import logging
import os

from .mta import Broker
from .decorators import thread
from .config import PROTOCOLS, TOPICS
from .utils import *
from .user import User



logger = logging.getLogger('CLIENT')


class EBMC:
    def __init__(self, client_email_addr, server_email_addr, email_server, pwd):
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
        print('+++++++++INSTANCIA DE BROKER++++++++++++')

        self.token = ''

    # returns an ID
    @thread
    def register(self, user, password):
        content = f'{user}\n{password}\n{user}'
        # content = user+'\n'+password+'\n'+self.user_info.active_email
        msg = self.mta.build_message(
            body=content,
            protocol=PROTOCOLS['CONFIG'],
            topic=TOPICS['REGISTER']
        )
        logger.info(f'{user}\n{password}\n{self.server_email_addr}')
        logger.info(f'Msg is: {msg}')
        msg.send(self.mta, self.server_email_addr, self.user_info)

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
        msg.send(self.mta, self.server_email_addr, self.user_info)

        item = None
        while not item:
            print(f'Id en cliente  {id(self.mta._config_queue)}')
            item = in_queue(msg.id, copy.deepcopy(self.mta.config_queue))
            if item is not None:
                self.token = item.text
                break
            time.sleep(1)

    @thread
    def send(self, user: str, file_location: str, name: str):
        """"
        :param user: user to send
        :param data: data
        :param name: name of package
        """
        msg = self.mta.build_message(body=f'{user}', protocol=PROTOCOLS['CONFIG'], topic=TOPICS['CMD'], user=self.user_info.active_email, token=self.token)
        msg.send(self.mta, self.server_email_addr, self.user_info)
        item = None
        while not item:
            item = in_queue(msg.id, copy.deepcopy(self.mta.config_queue))
            if item is not None:
                # # self.mta.config_queue.remove(item)
                with open(file_location, 'r') as file:
                    size = os.path.getsize(file_location)
                    email = item.text
                    for _ in range(int(size / 1000)):
                        # self.mta.config_queue.remove(item)
                        msg_data = self.mta.build_message(body=file.read(1000), protocol=PROTOCOLS['DATA'], topic=TOPICS['ANSWER'],
                                                          name=file.name, user=self.user_info.active_email, token=self.token)
                        msg_data.send(self.mta, email, self.user_info)

                    if size % 1000:
                        msg_data = self.mta.build_message(body=file.read(size % 1000), protocol=PROTOCOLS['DATA'],
                                                          topic=TOPICS['ANSWER'],
                                                          name=file.name, user=self.user_info.active_email,
                                                          token=self.token)
                        msg_data.send(self.mta, email, self.user_info)

                os.remove(file_location)
                break
            time.sleep(1)

    @thread
    def publish(self, event: str, file_location: str, name: str):
        """"
        :param event: name of event
        :param data: data to publish
        :param name: name of package
        """
        msg = self.mta.build_message(body=event, protocol=PROTOCOLS['CONFIG'], topic=TOPICS['PUBLICATION'], user=self.user_info.active_email, token=self.token)
        msg.send(self.mta, self.server_email_addr, self.user_info)
        item = None
        while not item:
            item = in_queue(msg.id, copy.deepcopy(self.mta.config_queue))
            if item is not None:
                emails = item.text.split(';')
                # self.mta.config_queue.remove(item)

                with open(file_location, 'r') as file:
                    size = os.path.getsize(file_location)
                    # TODO: cambia 1000 por el tamanno maximo permitido
                    for _ in range(int(size / 1000)):
                        email = item.text
                        # self.mta.config_queue.remove(item)
                        msg_data = self.mta.build_message(body=file.read(1000), protocol=PROTOCOLS['DATA'], topic=TOPICS['PUBLICATION'],
                                                          name=name, user=self.user_info.active_email, token=self.token)
                        for email in emails:
                            msg_data.send(self.mta, email,self.user_info)

                    if size % 1000:
                        msg_data = self.mta.build_message(body=file.read(size % 1000), protocol=PROTOCOLS['DATA'],
                                                          topic=TOPICS['PUBLICATION'],
                                                          name=name, user=self.user_info.active_email,
                                                          token=self.token)
                        for email in emails:
                            msg_data.send(self.mta, email, self.user_info)

                os.remove(file_location)
                break


            time.sleep(1)

    @thread
    def create_event(self, name: str):
        msg = self.mta.build_message(body=name, protocol=PROTOCOLS['CONFIG'], topic=TOPICS['CREATE'], user=self.user_info.active_email, token=self.token)
        msg.send(self.mta, self.server_email_addr, self.user_info)

    @thread
    def subscribe(self, event: str):
        msg = self.mta.build_message(body=event, protocol=PROTOCOLS['CONFIG'], topic=TOPICS['SUBSCRIPTION'], user=self.user_info.active_email, token=self.token)
        msg.send(self.mta, self.server_email_addr, self.user_info)


    @thread
    def unsubscribe(self, event: str):
        msg = self.mta.build_message(body=event, protocol=PROTOCOLS['CONFIG'], topic=TOPICS['UNSUBSCRIPTION'], user=self.user_info.active_email, token=self.token)
        msg.send(self.mta, self.server_email_addr, self.user_info)

    @property
    def received(self) -> tuple:
        """
        :return: list: (id_message, name_location)
        """
        return self.mta.complete_messages

    def add_email(self, email):
        pass
