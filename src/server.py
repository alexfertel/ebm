#!/usr/bin/env python3.6
import config
import fire
import hashlib
import logging
import pickle
import random
import rpyc
import socket
import string

from mta import Broker
from user import User
from utils import inbetween
from decorators import *
from data import Data

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('SERVER')


class EBMS(rpyc.Service):
    def __init__(self, server_email_addr: str,
                 pwd: str,
                 email_server: str,
                 join_addr: tuple,
                 ip_addr: tuple):
        # Active users
        self.active_users = []

        # Chord setup
        self.__id = int(hashlib.sha1(str(server_email_addr).encode()).hexdigest(), 16) % config.SIZE
        # Compute  Table computable properties (start, interval).

        self.server_info = User(server_email_addr, pwd)

        # Setup broker
        self.mta = Broker(email_server, self.server_info)

        # The  property is computed when a joins or leaves and at the chord start
        logger.debug(f'Initializing fingers on server: {self.exposed_identifier() % config.SIZE}')
        self.ft: list = [(-1, ('', -1)) for _ in range(config.MAX_BITS + 1)]

        self.ft[0] = 'unknown'

        self.successors = tuple()  # list of successor nodes

        self.failed_nodes = []  # list of successor nodes

        # This server keys
        self.data = {}

        logger.debug(f'Capture ip address of self on server: {self.exposed_identifier() % config.SIZE}')
        # Sets this server's ip address correctly :) Thanks stackoverflow!
        if not ip_addr:
            self.addr = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]
                          or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
                               [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[
                            0], config.PORT
        else:
            self.addr = ip_addr

        self.me = self.exposed_identifier(), self.addr

        logger.debug(f'Ip address of self on server: {self.exposed_identifier()} is: {self.addr}')

        logger.debug(f'Starting join of server: {self.exposed_identifier()}')
        self.exposed_join(join_addr)  # Join chord
        logger.debug(f'Ended join of server: {self.exposed_identifier()}')

        self.multiplexer()

    # @retry_times(config.RETRY_ON_FAILURE_TIMES)
    def remote_request(self, addr, method, *args):
        if addr == self.addr:
            m = getattr(self, 'exposed_' + method)
            ans = m(*args)
        else:
            if self.is_online(addr):
                c = rpyc.connect(*addr)
                m = getattr(c.root, method)
                ans = m(*args)
                c.close()
            else:
                logger.error(f'\nRemote request: {method} in to address: {addr} could not be done.\n'
                             f'Server {addr} is down.')
                return
        return ans

    def is_online(self, addr):
        if addr == self.addr:
            return True
        try:
            c = rpyc.connect(*addr)
            c.close()
            logger.info(f'Server with address: {addr} is online.')
            if addr in self.failed_nodes:
                logger.info(f'Server with address: {addr} was down. Execute remote join.')
                self.failed_nodes.remove(addr)
                self.remote_request(addr, 'join', self.me)
            return True
        except Exception as e:
            logger.error(f'Server with address: {addr} is down.')
            logger.error(f'Exception: "{e}" was thrown.')
            if addr not in self.failed_nodes:
                self.failed_nodes.append(addr)
            return False

    def exposed_identifier(self):
        return self.__id

    def exposed_failed_nodes(self):
        return self.failed_nodes

    # ##################################################### CHORD ######################################################
    def exposed_finger_table(self):
        return tuple(self.ft)

    # Return first online successor
    def exposed_successor(self):
        # logger.debug(f'Calling exposed_successor on server: {self.exposed_identifier() % config.SIZE}')
        candidates = [self.ft[1]] + list(self.successors)

        if len(candidates) == 0:  # Trying to fix fingers without having stabilized
            return self.me

        for index, n in enumerate(candidates):
            logger.debug(f'Successor {index} in server: {self.exposed_identifier()} is {n}')
            if n and self.is_online(n[1]):
                logger.debug(f'Successor {index} was selected.')
                return n
        else:
            logger.error(f'There is no online successor, thus we are our successor')
            return self.me

    def exposed_get_successors(self):
        return self.successors

    def exposed_predecessor(self):
        logger.debug(f'Calling exposed_predecessor on server: {self.exposed_identifier() % config.SIZE}')
        return self.ft[0]

    def exposed_find_successor(self, identifier):
        logger.debug(f'Calling exposed_find_successor({identifier % config.SIZE}) '
                     f'on server: {self.exposed_identifier() % config.SIZE}')

        if self.ft[0] != 'unknown' and inbetween(self.ft[0][0] + 1, self.exposed_identifier(), identifier):
            return self.me

        n_prime = self.exposed_find_predecessor(identifier)
        return self.remote_request(n_prime[1], 'successor')

    def exposed_find_predecessor(self, identifier):
        # logger.debug(f'Calling exposed_find_predecessor({identifier % config.SIZE}) on server: {self.exposed_identifier() % config.SIZE}')
        n_prime = self.me
        succ = self.exposed_successor()

        if succ[0] == self.me[0]:
            return self.me

        while not inbetween(n_prime[0] + 1, succ[0] + 1, identifier):
            n_prime = self.remote_request(n_prime[1], 'closest_preceding_finger', identifier)
            succ = self.remote_request(n_prime[1], 'successor')
            # if not n_prime:
            #     return self.exposed_successor()
        return n_prime

    # return closest preceding finger (id, ip)
    def exposed_closest_preceding_finger(self, exposed_identifier):
        for i in range(len(self.ft) - 1, 0, -1):
            if self.ft[i] != (-1, ('', -1)) and inbetween(self.exposed_identifier() + 1, exposed_identifier - 1,
                                                          self.ft[i][0]):
                # Found responsible for next iteration
                return self.ft[i]
        succ = self.exposed_successor()
        return succ \
            if inbetween(self.exposed_identifier() + 1, exposed_identifier - 1, succ[0]) \
            else self.me

    # # n joins the network;
    # # n' is an arbitrary in the network
    def exposed_join(self, n_prime_addr):
        if n_prime_addr:
            logger.debug(f'Joining network, connecting to  {n_prime_addr} -> server: {self.exposed_identifier()}')
            self.ft[0] = 'unknown'
            finger = self.remote_request(n_prime_addr, 'find_successor', self.exposed_identifier())
            self.ft[1] = finger
        else:  # n is the only in the network
            logger.debug(f'First of the network -> server: {self.exposed_identifier()}')
            self.ft[1] = self.me

        logger.debug(f'Successful join of: {self.exposed_identifier()} to chord')

        logger.debug(f'Starting stabilization of: {self.exposed_identifier()}')
        self.stabilize()

        logger.debug(f'Start fixing fingers of: {self.exposed_identifier()}')
        self.fix_fingers()

        logger.debug(f'Start updating successors of: {self.exposed_identifier()}')
        self.update_successors()

        logger.debug(f'Start replicating data of: {self.exposed_identifier()}')
        self.update_successors()

    # periodically verify n's immediate succesor,
    # and tell the exposed_successor about n.
    @retry(config.STABILIZATION_DELAY)
    def stabilize(self):
        logger.debug(f'\nStabilizing on server: {self.exposed_identifier() % config.SIZE}\n')
        succ = self.exposed_successor()
        x = self.remote_request(succ[1], 'predecessor')

        if x and x != 'unknown' and inbetween(self.exposed_identifier() + 1, succ[0] - 1, x[0]) and self.is_online(
                x[1]):
            self.ft[1] = x

        self.remote_request(self.exposed_successor()[1], 'notify', self.me)

    # n' thinks it might be our exposed_predecessor.
    def exposed_notify(self, n_prime_key_addr: tuple):
        logger.debug(f'Notifying on server: {self.exposed_identifier() % config.SIZE}')

        if self.ft[0] == 'unknown' or inbetween(self.ft[0][0] + 1, self.exposed_identifier() - 1, n_prime_key_addr[0]):
            self.ft[0] = n_prime_key_addr

    # periodically refresh finger table entries
    @retry(config.FIX_FINGERS_DELAY)
    def fix_fingers(self):
        logger.debug(f'Fixing fingers on server: {self.exposed_identifier() % config.SIZE}')
        if config.MAX_BITS + 1 > 2:
            i = random.randint(2, config.MAX_BITS)
            finger = self.exposed_find_successor((self.exposed_identifier() + (2 ** (i - 1))) % config.SIZE)
            if finger:
                self.ft[i] = finger
                logger.debug(f'Finger {i} on server: {self.exposed_identifier() % config.SIZE} fixed to {self.ft[i]}')

    @retry(config.UPDATE_SUCCESSORS_DELAY)
    def update_successors(self):
        logging.debug(f'Updating successor list on server: {self.exposed_identifier() % config.SIZE}')
        succ = self.exposed_successor()

        if self.addr[1] == succ[1]:
            return
        successors = [succ]
        remote_successors = list(self.remote_request(succ[1], 'get_successors'))[:config.SUCC_COUNT - 1]
        logging.info(f'Remote successors: {remote_successors}')
        if remote_successors:
            successors += remote_successors
        self.successors = tuple(successors)
        logging.info(f'Successors: {successors}')

    # ##################################################### DATA ######################################################
    # Get this nodes data
    def exposed_get_data(self):
        return pickle.dumps(self.data)

    # Returned data will be a 'pickled' object
    def exposed_get(self, key):
        data = self.data.get(key, None)
        if data:
            return data.to_tuple() if isinstance(data, Data) else data

        succ = self.exposed_find_successor(key)
        return self.remote_request(succ[1], 'get', key)

    # value param must be a 'pickled' object
    def exposed_set(self, key, value):
        if inbetween(self.exposed_predecessor()[0] + 1, self.exposed_identifier(), key):
            logger.debug(f'Node {self.me} holds key {key}')
            self.data[key] = pickle.loads(value)
        else:
            succ = self.exposed_find_successor(key)
            self.remote_request(succ[1], 'set', key, value)

    def exposed_get_all(self):
        start_node = self.exposed_identifier()
        current_node = self.exposed_successor()

        data = self.data  # start with start_node -self- keys

        while current_node[0] != start_node:
            current_data = pickle.loads(self.remote_request(current_node[1], 'get_data'))

            # Ours should have correct state of the keys, successors may not have correct replicas
            current_data.update(data)

            data = current_data
            current_node = self.remote_request(current_node[1], 'successor')

        return pickle.dumps(data)

    # ################################################## REPLICATION ###################################################
    # This should periodically move keys to a new node
    @retry(config.REPLICATION_DELAY)
    def replicate(self):
        i = random.randint(0, len(self.successors))
        for k, v in self.data.items():
            self.remote_request(self.successors[i][1], 'set', k, pickle.dumps(v))

    # ####################################################### MQ #######################################################
    def subscribe(self, subscriber: str, event: str, email_client: str, message_id: str):
        """
            This method represents a subscription.
            :param subscriber: str
            :param event: str
            :param email_client: str
            :param message_id: str
            :return: None
            """
        # TODO: ver como retorna los objetos el self.get
        subscription_list_id = hashlib.sha1(event.encode()).hexdigest()
        subscription_list = Data.from_tuple(pickle.loads(self.exposed_get(subscription_list_id)))
        if subscription_list:
            user_id = hashlib.sha1(subscriber.encode()).hexdigest()
            subscription_list['list'].push(user_id)
            subscription_list = pickle.dumps(subscription_list)
            self.exposed_set(subscription_list_id, subscription_list)

            msg = self.mta.build_message('SUBSCRIBED', protocol=config.PROTOCOLS['PUB/SUB'],
                                         topic=config.TOPICS['ANSWER'], message_id=message_id)
        else:
            msg = self.mta.build_message('error', protocol=config.PROTOCOLS['PUB/SUB'], topic=config.TOPICS['ANSWER'],
                                         message_id=message_id)
        msg.send(self.mta, email_client, self.server_info)

        # self.add(subscription_list_id, subscriber)

    def unsubscribe(self, subscriber: str, event: str, email_client: str, message_id: str):
        """
        This method represents an unsubscription.
        :param message_id: str
        :param email_client: str
        :param subscriber: str
        :param event: str
        :return: None
        """
        subscription_list_id = hashlib.sha1(event.encode()).hexdigest()
        subscription_list = Data.from_tuple(pickle.loads(self.exposed_get(subscription_list_id)))
        # TODO: ver que retorna para q no se roma el if
        if subscription_list:
            user_id = hashlib.sha1(subscriber.encode()).hexdigest()
            subscription_list['list'].remove(user_id)
            subscription_list = pickle.dumps(subscription_list)

            self.exposed_set(subscription_list_id, subscription_list)

            msg = self.mta.build_message('UNSUBSCRIBED', protocol=config.PROTOCOLS['PUB/SUB'],
                                         topic=config.TOPICS['ANSWER'], message_id=message_id)
        else:
            msg = self.mta.build_message('ERROR', protocol=config.PROTOCOLS['PUB/SUB'], topic=config.TOPICS['ANSWER'],
                                         message_id=message_id)

        msg.send(self.mta, email_client, self.server_info)

    def publish(self, user: str, event: str, email_client: str, message_id: str):
        subscription_list_id = hashlib.sha1(event.encode()).hexdigest()
        user_id = hashlib.sha1(user.encode()).hexdigest()

        subscriptions = Data.from_tuple(pickle.loads(self.exposed_get(subscription_list_id)))
        if user_id == subscriptions['admin']:
            content = ';'.join([
                Data.from_tuple(pickle.loads(self.exposed_get(user_id)))['mail'] for user_id in subscriptions['list']
            ])

            msg = self.mta.build_message(body=content, protocol=config.PROTOCOLS['PUB/SUB'],
                                         topic=config.TOPICS['ANSWER'], message_id=message_id)
        else:
            msg = self.mta.build_message('YOU DO NOT HAVE PERMISSION', protocol=config.PROTOCOLS['PUB/SUB'],
                                         topic=config.TOPICS['ANSWER'], message_id=message_id)

        msg.send(self.mta, email_client, self.server_info)

    def create_event(self, user: str, event: str, email_client: str, message_id: str):
        subscription_list_id = hashlib.sha1(event.encode()).hexdigest()
        user_id = hashlib.sha1(user.encode()).hexdigest()
        subscriptions = Data.from_tuple(pickle.loads(self.exposed_get(subscription_list_id)))
        # TODO: ver que retorna no valla a ser que el if no funcione
        if not subscriptions:
            event = pickle.dumps({
                'list': [],
                'admin': user_id
            })
            self.exposed_set(subscription_list_id, event)
            msg = self.mta.build_message('EVENT CREATED', protocol=config.PROTOCOLS['PUB/SUB'],
                                         topic=config.TOPICS['ANSWER'], message_id=message_id)
        else:
            msg = self.mta.build_message('ERROR TO CREATE EVENT', protocol=config.PROTOCOLS['PUB/SUB'],
                                         topic=config.TOPICS['ANSWER'], message_id=message_id)

        msg.send(self.mta, email_client, self.server_info)

    def send(self, user: str, email_client: str, message_id: str):
        user_id = hashlib.sha1(user.encode()).hexdigest()
        user_mail = Data.from_tuple(pickle.loads(self.exposed_get(user_id)))['mail']

        msg = self.mta.build_message(user_mail, protocol=config.config.PROTOCOLS['DATA'], topic=config.TOPICS['ANSWER'],
                                     message_id=message_id)
        msg.send(self.mta, email_client, self.server_info)

    def login(self, user: str, pwd: str, user_mail: str, message_id: str):
        user_id = hashlib.sha1(user.encode()).hexdigest()
        pwd = hashlib.sha1(pwd.encode()).hexdigest()

        user = Data.from_tuple(pickle.loads(self.exposed_get(user_id)))
        if user['pass'] == pwd:
            msg = self.mta.build_message(user_id, protocol=config.config.PROTOCOLS['CONFIG'],
                                         topic=config.TOPICS['LOGIN'], message_id=message_id)
        else:
            msg = self.mta.build_message('ERROR AUTHENTICATION', protocol=config.config.PROTOCOLS['CONFIG'],
                                         topic=config.TOPICS['LOGIN'], message_id=message_id)

        msg.send(self.mta, user_mail, self.server_info)

    def register(self, user: str, pwd: str, user_mail: str, message_id: str):
        user_id = hashlib.sha1(user.encode()).hexdigest()
        user = Data.from_tuple(pickle.loads(self.exposed_get(user_id)))
        # TODO: ver que rerorna esto, pq puede que no sira el if
        if not user:
            pwd = hashlib.sha1(pwd.encode()).hexdigest()
            user = pickle.dumps(
                {
                    'mail': user_mail,
                    'pwd': pwd,
                    'user': user
                }
            )
            self.exposed_set(user_id, user)
            msg = self.mta.build_message(user_id, protocol=config.config.PROTOCOLS['CONFIG'],
                                         topic=config.TOPICS['REGISTER'], message_id=message_id)
        else:
            msg = self.mta.build_message('ERROR', protocol=config.config.PROTOCOLS['CONFIG'],
                                         topic=config.TOPICS['REGISTER'], message_id=message_id)

        msg.send(self.mta, user_mail, self.server_info)

    @thread
    def multiplexer(self):
        while True:
            if len(self.mta.config_queue) > 0:
                block = self.mta.config_queue.pop(0)
                if block.subject['protocol'] == config.PROTOCOLS['CONFIG']:
                    if block.subject['topic'] == config.TOPICS['REGISTER']:
                        user_pass_email = block.text.split('\n')
                        self.register(user_pass_email[0], user_pass_email[1], user_pass_email[2], block.id)
                    elif block.subject['topic'] == config.TOPICS['LOGIN']:
                        user_pass = block.text.split('\n')
                        self.login(user_pass[0], user_pass[1], block.email, block['From'])
                    elif block.subject['topic'] == config.TOPICS['CMD']:
                        self.send(block.text, block['From'], block.id)
                    elif block.subject['topic'] == config.TOPICS['PUBLICATION']:
                        self.publish(block.subject['user'], block.text, block.email, block.id)
                    elif block.subject['topic'] == config.TOPICS['SUBSCRIPTION']:
                        self.subscribe(block.subject['user'], block.text, block.email, block.id)
                    elif block.subject['topic'] == config.TOPICS['UNSUBSCRIPTION']:
                        self.unsubscribe(block.subject['user'], block.text, block.email, block.id)
                    else:
                        # block.subject['topic'] == config.TOPICS['CREATE']
                        self.create_event(block.subject['user'], block.text, block.email, block.id)


def main(server_email_addr: str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)),
         join_addr: str = None,
         server: str = 'correo.estudiantes.matcom.uh.cu',
         pwd: str = '#1S1m0l5enet',
         ip_addr: str = None):
    t = ThreadedServer(
        EBMS(server_email_addr, join_addr, server, pwd, ip_addr),
        port=ip_addr[1] if ip_addr else config.PORT)
    t.start()


def deploy(server_email_addr: str,
           pwd: str,
           email_server: str,
           join_addr: tuple = None,
           ip_addr: tuple = None):
    """
    Method exposing EBMS instance
    :param server_email_addr: The server email address (ebms@gmail.com)
    :param pwd: The password for the server_email_address (ebmspassword)
    :param email_server: The email server handling an MX DNS record (correo.estudiantes.matcom.uh.cu)
    :param join_addr: The chord node to join address (('10.6.98.41'), 18861). In case of being None, this is the first chord node
    :param ip_addr: The server ip address. This is useful when testing in localhost, or in a dockerized environment
    :return: None
    """
    t = ThreadedServer(
        EBMS(server_email_addr, pwd, email_server, join_addr, ip_addr),
        port=ip_addr[1] if ip_addr else config.PORT)
    t.start()


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer

    # import sys
    fire.Fire(deploy)
