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
    def __init__(self, start: int = -1, interval: tuple = (-1, -1), node: list = None):
        self.start = start
        self.interval = interval
        self.node = node if node else [-1, '']

    def __repr__(self):
        return f'start: {self.start}, interval: [{self.interval[0]}, {self.interval[1]}), node: {self.node}'


class EBMS(rpyc.Service):
    def __init__(self, server_email_addr: str = 'a.fertel@estudiantes.matcom.uh.cu', join_addr: str = None):
        # Chord node setup
        self.__id = int(hashlib.sha1(str(server_email_addr).encode()).hexdigest(), 16)
        # Compute Finger Table computable properties (start, interval).
        # The .node property is computed when a node joins or leaves and at the chord start
        logger.debug(f'Initializing fingers on server: {self.identifier}')
        self.ft = {
            i: Finger(start=(self.identifier + 2 ** (i - 1)) % 2 ** config.MAX_BITS)
            for i in range(1, config.MAX_BITS + 1)
        }

        for i in range(1, len(self.ft)):
            self.ft[i].interval = self.ft[i].start, self.ft[i + 1].start

        self.ft[0] = Finger()  # At first the predecessor is unknown

        # Init data file
        with open('data.json', 'w+') as fd:
            fd.write('{}')

        logger.debug(f'Capture ip address of self on server: {self.identifier}')
        # Sets this server's ip address correctly :) Thanks stackoverflow!
        self.ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]
                    or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
                         [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]

        logger.debug(f'Starting join of server: {self.identifier}')
        self.join(join_addr)  # Join chord
        logger.debug(f'Ended join of server: {self.identifier}')

    @property
    def identifier(self):
        return self.__id

    @property
    def successor(self):
        logger.debug(f'Calling successor on server: {self.identifier}')
        node = rpyc.connect(self.ft[1].node[1], config.PORT).root
        return node

    @property
    def predecessor(self):
        logger.debug(f'Calling predecessor on server: {self.identifier}')
        node = rpyc.connect(self.ft[0].node[1], config.PORT).root
        return node

    def find_successor(self, identifier):
        logger.debug(f'Calling find_successor() on server: {self.identifier}')
        n_prime = self.find_predecessor(identifier)
        return n_prime.successor

    def find_predecessor(self, identifier):
        logger.debug(f'Calling find_predecessor() on server: {self.identifier}')
        n_prime = self
        # compute closest finger preceding id
        while not (n_prime.identifier < identifier <= n_prime.successor):
            for i in range(len(n_prime.ft) - 1, 0, -1):
                if inbetween(n_prime.ft[i].interval[0] + 1, n_prime.ft[i].interval[1] + 1, identifier):
                    # Found node responsible for next iteration
                    # Here, we should make a remote call
                    n_prime = rpyc.connect(n_prime.ft[i].node[1], config.PORT).root

                    # n_primer = n_prime.ft[i].node
        # Found predecessor
        return n_prime

    # # node n joins the network;
    # # n' is an arbitrary node in the network
    def join(self, n_prime_addr):
        if n_prime_addr:
            logger.debug(f'Joining network -> server: {self.identifier}')
            self.ft[0].node[0] = -1

            print(n_prime_addr)
            n_prime = rpyc.connect(n_prime_addr, config.PORT).root

            self.ft[1] = n_prime.find_successor(self.identifier)
        else:  # n is the only node in the network
            logger.debug(f'First node of the network -> server: {self.identifier}')
            for i in range(len(self.ft)):
                # FIXME Rebuild the image to add this line
                self.ft[i].node[0] = self.identifier
                self.ft[i].node[1] = self.ip

    # periodically verify n's immediate succesor,
    # and tell the successor about n.
    @retry(3)
    def stabilize(self):
        logger.debug(f'Stabilizing on server: {self.identifier}')
        n_prime = rpyc.connect(self.ft[1].node[1], config.PORT).root
        x = n_prime.successor.predecessor
        if inbetween(self.identifier + 1, self.ft[1].node[0] - 1):
            self.ft[1].node[0] = x.identifier
            self.ft[1].node[1] = x.ip
        n_prime.notify(self.identifier)

    # n' thinks it might be our predecessor.
    def notify(self, n_prime):
        logger.debug(f'Notifying on server: {self.identifier}')
        if self.ft[0] == 'unknown' or inbetween(self.ft[0].node[0] + 1, self.identifier - 1, n_prime):
            self.ft[0].node[0] = n_prime
            # self.ft[0].node[1] = self.ip  # FIXME I think this will be missing

    # periodically refresh finger table entries
    @retry(2)
    def fix_fingers(self):
        logger.debug(f'Fixing fingers on server: {self.identifier}')
        if len(self.ft) > 2:
            i = random.randint(2, len(self.ft))
            node = self.find_successor(self.ft[i].start)
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

    if len(sys.argv) < 3:
        print('Usage: ./server.py <email_address> <ip_address>')
        logger.debug(f'Initializing ThreadedServer with default values: a.fertel@correo.estudiantes.matcom.uh.cu'
                     f' and 10.6.98.49.')
        t = ThreadedServer(EBMS(), port=config.PORT, protocol_config={
            'allow_public_attrs': True,
        })
        # t = ThreadedServer(MyService, port=config.PORT)
        t.start()
    else:
        logger.debug(f'Initializing ThreadedServer with email address: {sys.argv[1]} and join address: {sys.argv[2]}')
        t = ThreadedServer(EBMS(sys.argv[1], sys.argv[2]), port=config.PORT, protocol_config={
            'allow_public_attrs': True,
        })
        # t = ThreadedServer(MyService, port=config.PORT)
        t.start()
