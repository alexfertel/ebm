#!/usr/bin/env python3.6
import time

import config
import copy
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
from utils import inbetween, hashing
from decorators import *
from rpyc.utils.server import ThreadedServer

# logging.basicConfig(level=logging.FATAL)
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
        self.__id = hashing(server_email_addr) if server_email_addr else hashing(''.join(random.choices(string.ascii_lowercase + string.digits, k=6)))
        # Compute  Table computable properties (start, interval).

        self.server_info = User(server_email_addr, pwd)
        # self.server_info = None  # Testing purposes

        # Setup broker
        self.mta = Broker(email_server, self.server_info) if server_email_addr else None
        # self.mta = None  # Testing purposes

        # The  property is computed when a joins or leaves and at the chord start
        logger.info(f'Initializing fingers on server: {self.exposed_identifier() % config.SIZE}')
        self.ft: list = [(-1, ('', -1)) for _ in range(config.MAX_BITS + 1)]

        self.ft[0] = 'unknown'

        self.successors = tuple()  # list of successor nodes

        self.failed_nodes = []  # list of successor nodes

        self.next_replica = 0

        # This server keys
        self.data = {}

        # This replicated keys
        self.replicas = {}

        logger.info(f'Capture ip address of self on server: {self.exposed_identifier() % config.SIZE}')
        # Sets this server's ip address correctly :) Thanks stackoverflow!
        if not ip_addr:
            self.addr = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]
                          or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
                               [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[
                            0], config.PORT
        else:
            self.addr = ip_addr

        self.me = self.exposed_identifier(), self.addr

        logger.info(f'Ip address of self on server: {self.exposed_identifier()} is: {self.addr}')

        logger.info(f'Starting join of server: {self.exposed_identifier()}')
        self.exposed_join(join_addr)  # Join chord
        logger.info(f'Ended join of server: {self.exposed_identifier()}')

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
                logger.info(f'\nRemote request: {method} in to address: {addr} could not be done.\n'
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
            logger.info(f'Server with address: {addr} is down.')
            logger.info(f'Exception: "{e}" was thrown.')
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
        # logger.info(f'Calling exposed_successor on server: {self.exposed_identifier() % config.SIZE}')
        candidates = [self.ft[1]] + list(self.successors)

        if len(candidates) == 0:  # Trying to fix fingers without having stabilized
            return self.me

        for index, n in enumerate(candidates):
            # logger.info(f'Successor {index} in server: {self.exposed_identifier()} is {n}')
            if n and self.is_online(n[1]):
                # logger.info(f'Successor {index} was selected.')
                return n
        else:
            logger.info(f'There is no online successor, thus we are our successor')
            return self.me

    def exposed_get_successors(self):
        return self.successors

    def exposed_predecessor(self):
        # logger.info(f'Calling exposed_predecessor on server: {self.exposed_identifier() % config.SIZE}')
        if self.ft[0] != 'unknown' and self.is_online(self.ft[0][1]):
            return self.ft[0]
        self.ft[0] = 'unknown'
        return self.ft[0]

    def exposed_find_successor(self, identifier):
        # logger.info(f'Calling exposed_find_successor({identifier % config.SIZE}) '
        #             f'on server: {self.exposed_identifier() % config.SIZE}')

        if self.ft[0] != 'unknown' and inbetween(self.ft[0][0] + 1, self.exposed_identifier(), identifier):
            return self.me

        n_prime = self.exposed_find_predecessor(identifier)
        return self.remote_request(n_prime[1], 'successor')

    def exposed_find_predecessor(self, identifier):
        # logger.info(f'Calling exposed_find_predecessor({identifier % config.SIZE}) on server: {self.exposed_identifier() % config.SIZE}')
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
            logger.info(f'Joining network, connecting to  {n_prime_addr} -> server: {self.exposed_identifier()}')
            self.ft[0] = 'unknown'
            finger = self.remote_request(n_prime_addr, 'find_successor', self.exposed_identifier())
            self.ft[1] = finger
        else:  # n is the only in the network
            logger.info(f'First of the network -> server: {self.exposed_identifier()}')
            self.ft[1] = self.me

        logger.info(f'Successful join of: {self.exposed_identifier()} to chord')

        logger.info(f'Starting stabilization of: {self.exposed_identifier()}')
        self.stabilize()

        logger.info(f'Start fixing fingers of: {self.exposed_identifier()}')
        self.fix_fingers()

        logger.info(f'Start updating successors of: {self.exposed_identifier()}')
        self.update_successors()

        logger.info(f'Start replicating data of: {self.exposed_identifier()}')
        self.next_replica = 0  # If a node rejoins network, restart replication.
        self.replicate()

        logger.info(f'Start checking ownership of data')
        self.check_ownership()

        if self.mta:
            logger.info(f'Start multiplexing in: {self.exposed_identifier()}')
            self.multiplexer()

    # periodically verify n's immediate succesor,
    # and tell the exposed_successor about n.
    @retry(config.STABILIZATION_DELAY)
    def stabilize(self):
        logger.info(f'\nStabilizing on server: {self.exposed_identifier() % config.SIZE}\n')
        succ = self.exposed_successor()
        x = self.remote_request(succ[1], 'predecessor')

        if x and x != 'unknown' and inbetween(self.exposed_identifier() + 1, succ[0] - 1, x[0]) and self.is_online(
                x[1]):
            self.ft[1] = x

        self.remote_request(self.exposed_successor()[1], 'notify', self.me)

    # n' thinks it might be our exposed_predecessor.
    def exposed_notify(self, n_prime_key_addr: tuple):
        logger.info(f'Notifying on server: {self.exposed_identifier() % config.SIZE}')

        if self.ft[0] == 'unknown' or inbetween(self.ft[0][0] + 1, self.exposed_identifier() - 1, n_prime_key_addr[0]):
            self.ft[0] = n_prime_key_addr

    # periodically refresh finger table entries
    @retry(config.FIX_FINGERS_DELAY)
    def fix_fingers(self):
        logger.info(f'Fixing fingers on server: {self.exposed_identifier() % config.SIZE}')
        if config.MAX_BITS + 1 > 2:
            i = random.randint(2, config.MAX_BITS)
            finger = self.exposed_find_successor((self.exposed_identifier() + (2 ** (i - 1))) % config.SIZE)
            if finger:
                self.ft[i] = finger
                logger.info(f'Finger {i} on server: {self.exposed_identifier() % config.SIZE} fixed to {self.ft[i]}')

    @retry(config.UPDATE_SUCCESSORS_DELAY)
    def update_successors(self):
        logger.info(f'Updating successor list on server: {self.exposed_identifier() % config.SIZE}')
        succ = self.exposed_successor()

        if self.addr[1] == succ[1]:
            return
        successors = [succ]
        remote_successors = list(self.remote_request(succ[1], 'get_successors'))[:config.SUCC_COUNT - 1]
        logger.info(f'Remote successors: {remote_successors}')
        if remote_successors:
            successors += remote_successors
        self.successors = tuple(successors)
        logger.info(f'Successors: {successors}')

    # ##################################################### DATA ######################################################
    # Get this nodes data
    def exposed_get_data(self):
        return pickle.dumps(self.data)

    # Get the owner of some data
    def exposed_get_owner(self, key):
        predecessor = self.exposed_predecessor()
        if predecessor == 'unknown':
            return None
        if self.data.get(key, None) or inbetween(predecessor[0] + 1, self.exposed_identifier(), key):
            return self.me

        start_node = self.me
        current_node = self.exposed_successor()

        while current_node[0] != start_node[0]:
            predecessor = self.remote_request(current_node[1], 'predecessor')
            if inbetween(predecessor[0] + 1, current_node[0], key):
                return current_node
            current_node = self.remote_request(current_node[1], 'successor')
        return None

    # Returned data will be a 'pickled' object
    def exposed_get(self, key):
        # logger.info(f'Key at get is: {key}')
        data = self.data.get(key, None)
        replica = self.replicas.get(key, None)
        if data:
            return pickle.dumps(data)
        elif replica:
            return pickle.dumps(replica)
        else:
            if self.exposed_predecessor() != 'unknown':
                if inbetween(self.exposed_predecessor()[0] + 1, self.exposed_identifier(), key):
                    logger.info(f"This key {key} belongs to us, but we don't have it, thus chord doesn't have it")
                    return None
                else:
                    succ = self.exposed_find_successor(key)
                    return self.remote_request(succ[1], 'get', key)
            else:
                time.sleep(1)
                return self.exposed_get(key)

    # value param must be a 'pickled' object
    def exposed_set(self, key, value):
        if inbetween(self.exposed_predecessor()[0] + 1, self.exposed_identifier(), key):
            logger.info(f'\n\n\nNode {self.me} holds key {key}\n\n\n')
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
    # Get this nodes data
    def exposed_get_replicas(self):
        return pickle.dumps(self.replicas)

    # This should periodically move keys to a new node
    @retry(config.REPLICATION_DELAY)
    def replicate(self):
        # i = random.randint(0, len(self.successors))
        # Check if there's only one Chord Node
        logger.info(f'\n\nEntered replicate method()\n')
        if self.exposed_successor()[0] != self.exposed_identifier():
            for k, v in self.data.items():
                self.remote_request(self.successors[self.next_replica][1], 'take_replica', k, pickle.dumps(v))

            logger.info(f"\n\nReplicated, increasing self.next_replica.\n")
            self.next_replica = (self.next_replica + 1) % config.SUCC_COUNT
        else:
            logger.info(f"\nThere's only one Chord node")

    # Dummy method to help with replication
    def exposed_take_replica(self, k, v):
        logger.info(f"\n\nNode {self.exposed_identifier()} has a replica of key {k} with value {v}.\n")
        self.replicas[k] = pickle.loads(v)

    # Periodically check ownership of replicated data
    @retry(config.CHECK_REPLICAS_DELAY)
    def check_ownership(self):
        logger.info(f"\nChecking Ownership.\n")
        replicas = copy.deepcopy(self.replicas)

        for key in replicas.keys():
            logger.info(f"\n\n\nKey {key}, Value {replicas[key]}")
            logger.info(f"Am I the owner?: {'Yes' if self.exposed_get_owner(key) == self.addr else 'No'}")
            owner = self.exposed_get_owner(key)
            if not owner:
                logger.info(f"Something went wrong!!! No owner found for a key!")
                return

            replica_owner_responsible = self.exposed_find_predecessor(key)
            self.remote_request(replica_owner_responsible[1], 'set', key, pickle.dumps(self.replicas[key]))

            # I'm the owner so make it my data
            # logger.info(f"Pass ownership of key {key} to node {self.exposed_identifier()}")
            # self.exposed_set(key, pickle.dumps(self.replicas[key]))
            successors = self.remote_request(owner[1], 'get_successors')
            logger.info(f"\nOwner {owner} has successors: {successors}.\n")
            if self.me not in successors:
                del self.replicas[key]

    # ####################################################### MQ #######################################################
    @required_auth
    def subscribe(self, subscriber: str, event: str, email_client: str, message_id: str, token: str):
        """
            This method represents a subscription.
            :param token: str
            :param subscriber: str
            :param event: str
            :param email_client: str
            :param message_id: str
            :return: None
            """
        subscription_list_id = hashing(event)

        exists = self.exposed_get(subscription_list_id)
        subscription_list = pickle.loads(exists) if exists else None

        if subscription_list:
            user_id = hashing(subscriber)
            # user_id = int(hashlib.sha1(subscriber.encode()).hexdigest(), 16)
            subscription_list['list'].push(user_id)
            subscription_list = pickle.dumps(subscription_list)
            self.exposed_set(subscription_list_id, subscription_list)

            msg = self.mta.build_message('SUBSCRIBED', protocol=config.PROTOCOLS['PUB/SUB'],
                                         topic=config.TOPICS['ANSWER'], message_id=message_id)
        else:
            msg = self.mta.build_message('ERROR', protocol=config.PROTOCOLS['PUB/SUB'], topic=config.TOPICS['ANSWER'],
                                         message_id=message_id)
        msg.send(self.mta, email_client, self.server_info)

        # self.add(subscription_list_id, subscriber)

    @required_auth
    def unsubscribe(self, subscriber: str, event: str, email_client: str, message_id: str, token: str):
        """
        This method represents an unsubscription.
        :param message_id: str
        :param email_client: str
        :param subscriber: str
        :param event: str
        :return: None
        """
        subscription_list_id = hashing(event)
        exists = self.exposed_get(subscription_list_id)
        subscription_list = pickle.loads(exists) if exists else None

        if subscription_list:
            user_id = hashing(subscriber)
            if user_id:
                subscription_list['list'].remove(user_id)
                subscription_list = pickle.dumps(subscription_list)
                self.exposed_set(subscription_list_id, subscription_list)
            msg = self.mta.build_message('UNSUBSCRIBED', protocol=config.PROTOCOLS['PUB/SUB'],
                                         topic=config.TOPICS['ANSWER'], message_id=message_id)
        else:
            msg = self.mta.build_message('ERROR', protocol=config.PROTOCOLS['PUB/SUB'], topic=config.TOPICS['ANSWER'],
                                         message_id=message_id)

        msg.send(self.mta, email_client, self.server_info)

    
    @required_auth
    def publish(self, user: str, event: str, email_client: str, message_id: str, token: str):

        subscription_list_id = hashing(event)
        # subscription_list_id = int(hashlib.sha1(event.encode()).hexdigest(), 16)
        user_id = hashing(user)
        # user_id = hashlib.sha1(user.encode()).hexdigest()

        exists = self.exposed_get(subscription_list_id)

        subscriptions = pickle.loads(exists) if exists else None
        if subscriptions and user_id == subscriptions['admin']:
            # TODO: no esty para arreglar lo de los loads aqui, aunque no tienen pq dar problemas ya q son usuarios registrados
            content = ';'.join([
                pickle.loads(self.exposed_get(user_id))['mail'] for user_id in subscriptions['list']
            ])

            msg = self.mta.build_message(body=content, protocol=config.PROTOCOLS['PUB/SUB'],
                                         topic=config.TOPICS['ANSWER'], message_id=message_id)
        else:
            msg = self.mta.build_message('YOU DO NOT HAVE PERMISSION', protocol=config.PROTOCOLS['PUB/SUB'],
                                         topic=config.TOPICS['ANSWER'], message_id=message_id)

        msg.send(self.mta, email_client, self.server_info)
    
    
    @required_auth
    def create_event(self, user: str, event: str, email_client: str, message_id: str, token: str):
        subscription_list_id = hashing(event)
        user_id = hashing(user)
        # subscription_list_id = hashlib.sha1(event.encode()).hexdigest()
        # user_id = hashlib.sha1(user.encode()).hexdigest()
        exists = self.exposed_get(subscription_list_id)
        subscriptions = pickle.loads(exists) if exists else None

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

    @required_auth
    def send(self, user: str, email_client: str, message_id: str, token: str):
        user_id = hashing(user)
        # user_id = hashlib.sha1(user.encode()).hexdigest()
        exists = self.exposed_get(user_id)
        user_mail = pickle.loads(exists)['mail'] if exists else None
        if user_mail:
            msg = self.mta.build_message(user_mail, protocol=config.PROTOCOLS['DATA'], topic=config.TOPICS['ANSWER'],
                                         message_id=message_id)
        else:
            logger.info(f'User {user} not found in chord')
            msg = self.mta.build_message('ERROR', protocol=config.PROTOCOLS['DATA'],
                                         topic=config.TOPICS['ANSWER'], message_id=message_id)
        msg.send(self.mta, email_client, self.server_info)

    def login(self, user: str, pwd: str, user_mail: str, message_id: str):
        user_id = hashing(user)
        pwd = hashing(pwd)

        # user_id = hashlib.sha1(user.encode()).hexdigest()
        # pwd = hashlib.sha1(pwd.encode()).hexdigest()

        exists = self.exposed_get(user_id)
        chord_user = pickle.loads(exists) if exists else None
        if chord_user:
            if chord_user['pwd'] == pwd:
                msg = self.mta.build_message(str(user_id), protocol=config.PROTOCOLS['CONFIG'],
                                             topic=config.TOPICS['LOGIN'], message_id=message_id)
            else:
                msg = self.mta.build_message('', protocol=config.PROTOCOLS['CONFIG'],
                                             topic=config.TOPICS['LOGIN'], message_id=message_id)

            msg.send(self.mta, user_mail, self.server_info)

    def register(self, user: str, pwd: str, user_mail: str, message_id: str):
        user_id = hashing(user)
        # user_id = hashlib.sha1(user.encode()).hexdigest()
        exists = self.exposed_get(user_id)
        chord_user = pickle.loads(exists) if exists else None
        if not chord_user:
            pwd = hashing(pwd)
            # pwd = hashlib.sha1(pwd.encode()).hexdigest()
            user = pickle.dumps(
                {
                    'mail': user_mail,
                    'pwd': pwd,
                    'user': user
                }
            )
            self.exposed_set(user_id, user)
            msg = self.mta.build_message(str(user_id), protocol=config.PROTOCOLS['CONFIG'],
                                         topic=config.TOPICS['REGISTER'], message_id=message_id)
        else:
            msg = self.mta.build_message('ERROR', protocol=config.PROTOCOLS['CONFIG'],
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
                        self.register(user_pass_email[0], user_pass_email[1], user_pass_email[2], block.subject['message_id'])
                    elif block.subject['topic'] == config.TOPICS['LOGIN']:
                        user_pass = block.text.split('\n')
                        self.login(user_pass[0], user_pass[1], block['From'], block.subject['message_id'])
                    elif block.subject['topic'] == config.TOPICS['CMD']:
                        self.send(block.text, block['From'], block.subject['message_id'], block.subject['token'])
                    elif block.subject['topic'] == config.TOPICS['PUBLICATION']:
                        self.publish(block.subject['user'], block.text, block['From'], block.subject['message_id'], token=block.subject['token'])
                    elif block.subject['topic'] == config.TOPICS['SUBSCRIPTION']:
                        self.subscribe(block.subject['user'], block.text, block['From'], block.subject['message_id'], token=block.subject['token'])
                    elif block.subject['topic'] == config.TOPICS['UNSUBSCRIPTION']:
                        self.unsubscribe(block.subject['user'], block.text, block['From'], block.subject['message_id'], token=block.subject['token'])
                    else:
                        # block.subject['topic'] == config.TOPICS['CREATE']
                        self.create_event(block.subject['user'], block.text, block['From'], block.subject['message_id'], token=block.subject['token'])


def main(server_email_addr: str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)),
         join_addr: tuple = None,
         server: str = 'correo.estudiantes.matcom.uh.cu',
         pwd: str = '#1S1m0l5enet',
         ip_addr: tuple = None):
    t = ThreadedServer(
        EBMS(server_email_addr,
             pwd,
             server,
             join_addr,
             ip_addr),
        port=ip_addr[1] if ip_addr else config.PORT)
    t.start()


def deploy(server_email_addr: str = None,
           pwd: str = None,
           email_server: str = None,
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
    # import sys
    fire.Fire(deploy)
    # fire.Fire(main)
