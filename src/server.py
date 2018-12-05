#!/usr/bin/env python3.6

import rpyc
import socket
import config
import random
import hashlib
import logging
import json

from utils import inbetween
from decorators import retry

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('SERVER')


class Finger:
    def __init__(self, identifier, ip):
        self.node = [identifier, ip]

    def __repr__(self):
        return f'(id: {self.node[0]} | ip: {self.node[1]})'


class EBMS(rpyc.Service):
    def __init__(self, server_email_addr: str = 'a.fertel@estudiantes.matcom.uh.cu',
                 join_addr: str = None,
                 ip_addr: str = None):
        # Chord node setup
        self.__id = int(hashlib.sha1(str(server_email_addr).encode()).hexdigest(), 16) % config.SIZE
        # Compute Finger Table computable properties (start, interval).
        # The .node property is computed when a node joins or leaves and at the chord start
        logger.debug(f'Initializing fingers on server: {self.identifier % config.SIZE}')
        self.ft: list = [Finger(-1, '') for _ in range(config.MAX_BITS + 1)]

        self.ft[0] = 'unknown'

        # self.ft[0] = Finger()  # At first the predecessor is unknown

        # Init data file
        with open('data.json', 'w+') as fd:
            fd.write('{}')

        logger.debug(f'Capture ip address of self on server: {self.identifier % config.SIZE}')
        # Sets this server's ip address correctly :) Thanks stackoverflow!
        if not ip_addr:
            self.ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]
                        or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
                             [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
        else:
            self.ip = ip_addr

        logger.debug(f'Ip address of self on server: {self.identifier} is: {self.ip}')

        logger.debug(f'Starting join of server: {self.identifier}')
        self.join(join_addr)  # Join chord
        logger.debug(f'Ended join of server: {self.identifier}')

    @property
    def identifier(self):
        return self.__id

    @property
    def successor(self):
        logger.debug(f'Calling successor on server: {self.identifier % config.SIZE}')
        node = rpyc.connect(self.ft[1].node[1], config.PORT).root if self.ft[1].node[0] != self.identifier else self
        logger.debug(f'Successor on server: {self.identifier % config.SIZE} yielded {node.identifier}')
        return node

    @property
    def predecessor(self):
        logger.debug(f'Calling predecessor on server: {self.identifier % config.SIZE}')
        if self.ft[0] == 'unknown':
            return self

        logger.debug(f'Debugging error AttributeError: list object has no attribute node')
        logger.debug(f'self.ft {self.ft} | self.identifier {self.identifier}')
        node = rpyc.connect(self.ft[0].node[1], config.PORT).root if self.ft[0].node[0] != self.identifier else self
        logger.debug(f'Predecessor on server: {self.identifier % config.SIZE} yielded {node.identifier}')
        return node

    def find_successor(self, identifier):
        logger.debug(f'Calling find_successor({identifier % config.SIZE}) on server: {self.identifier % config.SIZE}')
        n_prime = self.find_predecessor(identifier)
        return n_prime.successor

    def find_predecessor(self, identifier):
        logger.debug(f'Calling find_predecessor({identifier % config.SIZE}) on server: {self.identifier % config.SIZE}')
        n_prime = self
        # compute closest finger preceding id
        if n_prime.successor.identifier == self.identifier:
            return self
        while not inbetween(n_prime.identifier + 1, n_prime.successor.identifier, identifier):
            logger.debug(
                f'While condition inside find_predecessor({identifier}) on server: {self.identifier % config.SIZE}\n\t'
                f'n_prime.identifier: {n_prime.identifier}\tn_prime.successor:{n_prime.successor.identifier}')
            n_prime = n_prime.closest_preceding_finger(identifier)
        else:
            logger.debug(
                f'Else of while of find_predecessor({identifier % config.SIZE}) on server: {self.identifier % config.SIZE}')

        # Found predecessor
        logger.debug(f'End of find_predecessor({identifier % config.SIZE}) on server: {self.identifier % config.SIZE}')
        return n_prime

    # return closest preceding finger (id, ip)
    def closest_preceding_finger(self, identifier):
        for i in reversed(range(1, len(self.ft))):
            logger.debug(f'inbetween({self.identifier + 1, identifier - 1, self.ft[i].node[0]})')
            if inbetween(self.identifier + 1, identifier - 1, self.ft[i].node[0]):
                # Found node responsible for next iteration
                # Here, we should make a remote call
                logger.debug(f'If condition inside closest_preceding_finger({identifier % config.SIZE}) on server: '
                             f'{self.identifier % config.SIZE}\n\t'
                             f'index {i} yielded that responsible node is: {self.ft[i].node[1]}')
                n_prime = rpyc.connect(self.ft[i].node[1], config.PORT).root
                return n_prime
                # n_primer = n_prime.ft[i].node
        else:
            logger.debug(f'Did not enter inbetween if')
        return self

    # # node n joins the network;
    # # n' is an arbitrary node in the network
    def join(self, n_prime_addr):
        if n_prime_addr:
            logger.debug(f'Joining network to the node {n_prime_addr} -> server: {self.identifier}')
            self.ft[0] = 'unknown'

            print(n_prime_addr)
            n_prime = rpyc.connect(n_prime_addr, config.PORT).root
            # print(n_prime.ft)

            node = n_prime.find_successor(self.identifier)
            self.ft[1].node[0] = node.identifier
            self.ft[1].node[1] = node.ip
        else:  # n is the only node in the network
            logger.debug(f'First node of the network -> server: {self.identifier}')
            self.ft[1].node[0] = self.identifier
            self.ft[1].node[1] = self.ip
            # for i in range(1, config.MAX_BITS + 1):
            # FIXME Rebuild the image to add this line
            # self.ft[i].node[0] = self.identifier
            # self.ft[i].node[1] = self.ip
            logger.debug(f'Successor of the first node of the network {self.ft[1].node}')
            logger.debug(f'Predecessor of the first node of the network {self.ft[0]}')

        logger.debug(f'Successor of node: {self.identifier} is {self.ft[1].node}')
        logger.debug(
            f'Predecessor of node: {self.identifier} is {self.ft[0].node if self.ft[0] != "unknown" else self.ft[0]}')
        logger.debug(f'Finger Table values of node: {self.identifier} are {self.ft}')
        logger.debug(f'Successful join of node: {self.identifier} to chord')

        logger.debug(f'Starting stabilization of node: {self.identifier}')
        self.stabilize()
        logger.debug(f'Start fixing fingers of node: {self.identifier}')
        self.fix_fingers()

    # periodically verify n's immediate succesor,
    # and tell the successor about n.
    @retry(3)
    def stabilize(self):
        logger.debug(f'\nStabilizing on server: {self.identifier % config.SIZE}\n')
        logger.debug(f'self.ft[1].node[1]: {self.ft[1].node[1]}\n')
        n_prime = rpyc.connect(self.ft[1].node[1], config.PORT).root if self.ft[1].node[0] != self.identifier else self
        logger.debug(f'N_prime on stabilizing on server: {n_prime}\n')
        logger.debug(f'succ(N_prime) on stabilizing on server: {n_prime.successor}\n')
        x = n_prime.successor.predecessor
        # logger.debug(f'\nStabilizing on server: {self.identifier % config.SIZE}\n')
        if inbetween(self.identifier + 1, self.ft[1].node[0] - 1, x.identifier):
            self.ft[1].node[0] = x.identifier
            self.ft[1].node[1] = x.ip
        n_prime.notify(tuple([self.identifier, self.ip]))

    # n' thinks it might be our predecessor.
    def notify(self, n_prime_key_addr: tuple):
        logger.debug(f'Notifying on server: {self.identifier % config.SIZE}')
        # logger.debug(f'{self.ft[0]}')
        if self.ft[0] == 'unknown' or inbetween(self.ft[0].node[0] + 1, self.identifier - 1, n_prime_key_addr[0]):
            self.ft[0] = list(n_prime_key_addr)
            # self.ft[0].node[0] = n_prime_key_addr[0]
            # self.ft[0].node[1] = n_prime_key_addr[1]

    # periodically refresh finger table entries
    @retry(2)
    def fix_fingers(self):
        logger.debug(f'Fixing fingers on server: {self.identifier % config.SIZE}')
        if config.MAX_BITS + 1 > 2:
            i = random.randint(2, config.MAX_BITS)
            node = self.find_successor(self.identifier + 2 ** (i - 1))
            self.ft[i].node[0] = node.identifier
            self.ft[i].node[1] = node.ip

    def get(self, key):
        node = self.find_successor(key)
        return node.load()[key]

    def set(self, key, value):
        node = self.find_successor(key)
        dictionary = node.load()
        dictionary[key] = value
        node.save(dictionary)

    def save(self, dictionary: dict):
        with open('data.json', 'w+') as fd:
            json.dump(dictionary, fd)

    def load(self):
        with open('data.json', 'r+') as fd:
            return json.load(fd)

    # This should move keys to a new node and delete them
    def move(self):
        pass


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    import sys

    # print(len(sys.argv))

    if len(sys.argv) < 2:
        print('Usage: ./server.py <email_address> <ip_address>')
        logger.debug(f'Initializing ThreadedServer with default values: a.fertel@correo.estudiantes.matcom.uh.cu'
                     f' and 10.6.98.49.')
        t = ThreadedServer(EBMS(), port=config.PORT, protocol_config={
            'allow_public_attrs': True,
        })
        # t = ThreadedServer(MyService, port=config.PORT)
    elif len(sys.argv) == 2:
        logger.debug(f'Initializing ThreadedServer with default email address: a.fertel@correo.estudiantes.matcom.uh.cu'
                     f' and ip address: {sys.argv[1]}')
        t = ThreadedServer(EBMS(ip_addr=sys.argv[1]), port=config.PORT, protocol_config={
            'allow_public_attrs': True,
        })
    elif len(sys.argv) == 3:
        logger.debug(f'Initializing ThreadedServer with default email address: a.fertel@correo.estudiantes.matcom.uh.cu'
                     f' and ip address: {sys.argv[1]}')
        t = ThreadedServer(EBMS(sys.argv[1], sys.argv[2]), port=config.PORT, protocol_config={
            'allow_public_attrs': True,
        })
    else:
        logger.debug(f'Initializing ThreadedServer with email address: {sys.argv[1]}, join address: {sys.argv[2]}'
                     f' and ip address: {sys.argv[3]}')
        t = ThreadedServer(EBMS(sys.argv[1], sys.argv[2], sys.argv[3]), port=config.PORT, protocol_config={
            'allow_public_attrs': True,
        })
        # t = ThreadedServer(MyService, port=config.PORT)

    t.start()
