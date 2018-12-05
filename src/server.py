#!/usr/bin/env python3.6

import rpyc
import socket
import config
import random
import hashlib
import logging
import json
import copy
import threading


from utils import inbetween
from decorators import retry

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('SERVER')


class Finger:
    def __init__(self, exposed_identifier, ip):
        self.node = [exposed_identifier, ip]

    def __repr__(self):
        return f'(id: {self.node[0]} | ip: {self.node[1]})'


class EBMS(rpyc.Service):
    def __init__(self, server_email_addr: str = 'a.fertel@estudiantes.matcom.uh.cu',
                 join_addr: str = None,
                 ip_addr: str = None):
        
        self.lock = threading.Lock()
        
        # Chord node setup
        self.__id = int(hashlib.sha1(str(server_email_addr).encode()).hexdigest(), 16) % config.SIZE
        # Compute Finger Table computable properties (start, interval).
        # The .node property is computed when a node joins or leaves and at the chord start
        logger.debug(f'Initializing fingers on server: {self.exposed_identifier() % config.SIZE}')
        self.ft: list = [Finger(-1, '') for _ in range(config.MAX_BITS + 1)]

        self.ft[0] = 'unknown'

        # self.ft[0] = Finger()  # At first the exposed_predecessor is unknown

        # Init data file
        with open('data.json', 'w+') as fd:
            fd.write('{}')

        logger.debug(f'Capture ip address of self on server: {self.exposed_identifier() % config.SIZE}')
        # Sets this server's ip address correctly :) Thanks stackoverflow!
        if not ip_addr:
            self.ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]
                        or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
                             [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
        else:
            self.ip = ip_addr

        logger.debug(f'Ip address of self on server: {self.exposed_identifier()} is: {self.ip}')

        logger.debug(f'Starting join of server: {self.exposed_identifier()}')
        self.join(join_addr)  # Join chord
        logger.debug(f'Ended join of server: {self.exposed_identifier()}')

        logger.debug(f'Starting stabilization of node: {self.exposed_identifier()}')
        self.stabilize()
        logger.debug(f'Start fixing fingers of node: {self.exposed_identifier()}')
        self.fix_fingers()

    def remote_request(self, ip, method, *args):
        m = None
        ans = None
        if ip == self.ip:
            m = getattr(self, 'exposed_' + method)
            ans = m(*args)
        else:
            self.lock.acquire()
            c = rpyc.connect(ip, config.PORT)
            m = getattr(c.root, method)
            ans = m(*args)
            c.close()
            self.lock.release()
        return ans

    def exposed_identifier(self):
        return self.__id

    def exposed_successor(self):
        logger.debug(f'Calling exposed_successor on server: {self.exposed_identifier() % config.SIZE}')
        return self.ft[1]

        # node = rpyc.connect(self.ft[1].node[1], config.PORT).root if self.ft[1].node[0] != self.exposed_identifier() else self
        # logger.debug(f'exposed_successor on server: {self.exposed_identifier() % config.SIZE} yielded {node.exposed_identifier()}')
        # return node

    def exposed_predecessor(self):
        logger.debug(f'Calling exposed_predecessor on server: {self.exposed_identifier() % config.SIZE}')
        return self.ft[0]
        # if self.ft[0] == 'unknown':
        #     return self

        # logger.debug(f'Debugging error AttributeError: list object has no attribute node')
        # logger.debug(f'self.ft {self.ft} | self.exposed_identifier() {self.exposed_identifier()}')
        # node = rpyc.connect(self.ft[0].node[1], config.PORT).root if self.ft[0].node[0] != self.exposed_identifier() else self
        # logger.debug(f'exposed_predecessor on server: {self.exposed_identifier() % config.SIZE} yielded {node.exposed_identifier()}')
        # return node

    def exposed_find_successor(self, exposed_identifier):
        logger.debug(
            f'Calling exposed_find_successor({exposed_identifier % config.SIZE}) on server: {self.exposed_identifier() % config.SIZE}')

        n_prime = self.exposed_find_predecessor(exposed_identifier)
        return self.remote_request(n_prime.node[1], 'successor')
        # return n_prime.exposed_successor()

    def exposed_find_predecessor(self, exposed_identifier):
        logger.debug(
            f'Calling exposed_find_predecessor({exposed_identifier % config.SIZE}) on server: {self.exposed_identifier() % config.SIZE}')
        n_prime = Finger(self.exposed_identifier(), self.ip)
        succ = self.exposed_successor()

        # succ = n_prime.exposed_successor()
        if succ.node[0] == self.exposed_identifier():
            return Finger(self.exposed_identifier(), self.ip)

        while not inbetween(n_prime.node[0] + 1, succ.node[0] + 1, exposed_identifier):
            logger.debug(
                f'While condition inside exposed_find_predecessor({exposed_identifier}) on server: {self.exposed_identifier() % config.SIZE}\n\t'
                f'n_prime.exposed_identifier(): {n_prime.exposed_identifier()}\tn_prime.exposed_successor():{n_prime.exposed_successor().exposed_identifier()}')
            # compute closest finger preceding id
            n_prime = self.remote_request(n_prime.node[1], 'closest_preceding_finger', exposed_identifier)
            # n_prime = n_prime.exposed_closest_preceding_finger(exposed_identifier)
        else:
            logger.debug(
                f'Else of while of exposed_find_predecessor({exposed_identifier % config.SIZE}) on server: {self.exposed_identifier() % config.SIZE}')

        # Found exposed_predecessor
        logger.debug(
            f'End of exposed_find_predecessor({exposed_identifier % config.SIZE}) on server: {self.exposed_identifier() % config.SIZE}')
        return n_prime

    # return closest preceding finger (id, ip)
    def exposed_closest_preceding_finger(self, exposed_identifier):
        for i in reversed(range(1, len(self.ft))):
            logger.debug(f'inbetween({self.exposed_identifier() + 1, exposed_identifier - 1, self.ft[i].node[0]})')
            if inbetween(self.exposed_identifier() + 1, exposed_identifier - 1, self.ft[i].node[0]):
                # Found node responsible for next iteration
                # Here, we should make a remote call
                logger.debug(
                    f'If condition inside exposed_closest_preceding_finger({exposed_identifier % config.SIZE}) on server: '
                    f'{self.exposed_identifier() % config.SIZE}\n\t'
                    f'index {i} yielded that responsible node is: {self.ft[i].node[1]}')

                # n_prime = rpyc.connect(self.ft[i].node[1], config.PORT).root
                return self.ft[i]
                # n_primer = n_prime.ft[i].node
        else:
            logger.debug(f'Did not enter inbetween if')
        return Finger(self.exposed_identifier(), self.ip)

    # # node n joins the network;
    # # n' is an arbitrary node in the network
    def join(self, n_prime_addr):
        if n_prime_addr:
            logger.debug(f'Joining network to the node {n_prime_addr} -> server: {self.exposed_identifier()}')
            self.ft[0] = 'unknown'

            print(n_prime_addr)
            finger = self.remote_request(n_prime_addr, 'find_successor', self.exposed_identifier())
            # n_prime = rpyc.connect(n_prime_addr, config.PORT).root
            # print(n_prime.ft)

            # node = n_prime.exposed_find_successor(self.exposed_identifier())
            self.ft[1] = finger
        else:  # n is the only node in the network
            logger.debug(f'First node of the network -> server: {self.exposed_identifier()}')
            self.ft[1].node[0] = self.exposed_identifier()
            self.ft[1].node[1] = self.ip
            # for i in range(1, config.MAX_BITS + 1):
            # self.ft[i].node[0] = self.exposed_identifier()
            # self.ft[i].node[1] = self.ip
            # logger.debug(f'exposed_successor of the first node of the network {self.ft[1].node}')
            # logger.debug(f'exposed_predecessor of the first node of the network {self.ft[0]}')

        # logger.debug(f'exposed_successor of node: {self.exposed_identifier()} is {self.ft[1]}')
        # logger.debug(f'Finger Table values of node: {self.exposed_identifier()} are {self.ft}')
        logger.debug(f'Successful join of node: {self.exposed_identifier()} to chord')

    # periodically verify n's immediate succesor,
    # and tell the exposed_successor about n.
    @retry(10)
    def stabilize(self):
        logger.debug(f'\nStabilizing on server: {self.exposed_identifier() % config.SIZE}\n')

        succ = self.exposed_successor()

        x = self.remote_request(succ.node[1], 'predecessor')

        # n_prime = rpyc.connect(self.ft[1].node[1], config.PORT).root if self.ft[1].node[0] != self.exposed_identifier() else self
        # logger.debug(f'N_prime on stabilizing on server: {n_prime}\n')
        # logger.debug(f'succ(N_prime) on stabilizing on server: {n_prime.exposed_successor()}\n')
        # x = n_prime.exposed_successor().exposed_predecessor()
        # logger.debug(f'\nStabilizing on server: {self.exposed_identifier() % config.SIZE}\n')
        if x != 'unknown' and inbetween(self.exposed_identifier() + 1, succ.node[0] - 1, x.node[0]):
            self.ft[1].node = x.node

        self.remote_request(self.exposed_successor().node[1], 'notify', (self.exposed_identifier(), self.ip))
        # n_prime.exposed_notify(tuple([self.exposed_identifier(), self.ip]))

    # n' thinks it might be our exposed_predecessor.
    def exposed_notify(self, n_prime_key_addr: tuple):
        logger.debug(f'Notifying on server: {self.exposed_identifier() % config.SIZE}')
        # logger.debug(f'{self.ft[0]}')

        if self.ft[0] == 'unknown' or inbetween(self.ft[0].node[0] + 1, self.exposed_identifier() - 1,
                                                n_prime_key_addr[0]):
            self.ft[0] = Finger(*n_prime_key_addr)
            # self.ft[0].node[0] = n_prime_key_addr[0]
            # self.ft[0].node[1] = n_prime_key_addr[1]

    # periodically refresh finger table entries
    @retry(7)
    def fix_fingers(self):
        logger.debug(f'Fixing fingers on server: {self.exposed_identifier() % config.SIZE}')
        if config.MAX_BITS + 1 > 2:
            i = random.randint(2, config.MAX_BITS)
            finger = self.exposed_find_successor(self.exposed_identifier() + 2 ** (i - 1))

            # assert isinstance(node, EBMS), 'node in fix_finger method is not an EBMS'
            # assert isinstance(node.exposed_identifier(), int), 'node.exposed_identifier() in fix_finger method is not an integer'
            # assert isinstance(node.ip, str), 'node.ip in fix_finger method is not a string'
            self.ft[i] = finger

    def get(self, key):
        node = self.exposed_find_successor(key)
        return node.load()[key]

    def set(self, key, value):
        node = self.exposed_find_successor(key)
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
        t = ThreadedServer(EBMS(), port=config.PORT)
        # t = ThreadedServer(MyService, port=config.PORT)
    elif len(sys.argv) == 2:
        logger.debug(f'Initializing ThreadedServer with default email address: a.fertel@correo.estudiantes.matcom.uh.cu'
                     f' and ip address: {sys.argv[1]}')
        t = ThreadedServer(EBMS(ip_addr=sys.argv[1]), port=config.PORT)
    elif len(sys.argv) == 3:
        logger.debug(f'Initializing ThreadedServer with default email address: a.fertel@correo.estudiantes.matcom.uh.cu'
                     f' and ip address: {sys.argv[1]}')
        t = ThreadedServer(EBMS(sys.argv[1], sys.argv[2]), port=config.PORT)
    else:
        logger.debug(f'Initializing ThreadedServer with email address: {sys.argv[1]}, join address: {sys.argv[2]}'
                     f' and ip address: {sys.argv[3]}')
        t = ThreadedServer(EBMS(sys.argv[1], sys.argv[2], sys.argv[3]), port=config.PORT)
        # t = ThreadedServer(MyService, port=config.PORT)

    t.start()
