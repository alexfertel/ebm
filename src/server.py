#!/usr/bin/env python3.6

import config
import fire
import hashlib
import json
import logging
import random
import rpyc
import socket
import string

from utils import inbetween
from decorators import retry, retry_times

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('SERVER')


class EBMS(rpyc.Service):
    def __init__(self, server_email_addr: str,
                 join_addr: str,
                 ip_addr: str):

        # Chord setup
        self.__id = int(hashlib.sha1(str(server_email_addr).encode()).hexdigest(), 16) % config.SIZE
        # Compute  Table computable properties (start, interval).
        # The  property is computed when a joins or leaves and at the chord start
        logger.debug(f'Initializing fingers on server: {self.exposed_identifier() % config.SIZE}')
        self.ft: list = [(-1, ('', -1)) for _ in range(config.MAX_BITS + 1)]

        self.ft[0] = 'unknown'

        self.successors = tuple()  # list of successor nodes

        # Init data file
        with open('data.json', 'w+') as fd:
            fd.write('{}')

        logger.debug(f'Capture ip address of self on server: {self.exposed_identifier() % config.SIZE}')
        # Sets this server's ip address correctly :) Thanks stackoverflow!
        if not ip_addr:
            self.addr = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]
                          or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
                               [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[
                            0], config.PORT
        else:
            self.addr = ip_addr

        logger.debug(f'Ip address of self on server: {self.exposed_identifier()} is: {self.addr}')

        logger.debug(f'Starting join of server: {self.exposed_identifier()}')
        self.join(join_addr)  # Join chord
        logger.debug(f'Ended join of server: {self.exposed_identifier()}')

    @retry_times(config.RETRY_ON_FAILURE_TIMES)
    def remote_request(self, addr, method, *args):
        if addr == self.addr:
            m = getattr(self, 'exposed_' + method)
            ans = m(*args)
        else:
            c = rpyc.connect(*addr)
            m = getattr(c.root, method)
            ans = m(*args)
            c.close()
        return ans

    def is_online(self, addr):
        if addr == self.addr:
            return True
        try:
            c = rpyc.connect(*addr)
            c.close()
            logger.error(f'Server with address: {addr} is online.')
            return True
        except:
            logger.error(f'Server with address: {addr} is down.')
            return False

    def exposed_identifier(self):
        return self.__id

    def exposed_finger_table(self):
        return tuple(self.ft)

    # Return first online successor
    def exposed_successor(self):
        logger.debug(f'Calling exposed_successor on server: {self.exposed_identifier() % config.SIZE}')
        for index, n in enumerate([self.ft[1]] + list(self.successors)):
            logger.debug(f'Successor {index} in server: {self.exposed_identifier()} is {n}')
            if self.is_online(n[1]):
                return n

    def exposed_get_successors(self):
        return self.successors

    def exposed_predecessor(self):
        logger.debug(f'Calling exposed_predecessor on server: {self.exposed_identifier() % config.SIZE}')
        return self.ft[0]

    def exposed_find_successor(self, exposed_identifier):
        logger.debug(f'Calling exposed_find_successor({exposed_identifier % config.SIZE}) '
                     f'on server: {self.exposed_identifier() % config.SIZE}')

        if self.ft[0] != 'unknown' and inbetween(self.ft[0][1] + 1, self.exposed_identifier() + 1, exposed_identifier):
            return self.exposed_identifier(), self.addr

        n_prime = self.exposed_find_predecessor(exposed_identifier)
        return self.remote_request(n_prime[1], 'successor')

    def exposed_find_predecessor(self, exposed_identifier):
        logger.debug(
            f'Calling exposed_find_predecessor({exposed_identifier % config.SIZE}) on server: {self.exposed_identifier() % config.SIZE}')
        n_prime = (self.exposed_identifier(), self.addr)
        succ = self.exposed_successor()

        if succ[0] == self.exposed_identifier():
            return self.exposed_identifier(), self.addr

        while not inbetween(n_prime[0] + 1, succ[0] + 1, exposed_identifier):
            n_prime = self.remote_request(n_prime[1], 'closest_preceding_finger', exposed_identifier)
        return n_prime

    # return closest preceding finger (id, ip)
    def exposed_closest_preceding_finger(self, exposed_identifier):
        for i in reversed(range(1, len(self.ft))):
            if inbetween(self.exposed_identifier() + 1, exposed_identifier - 1, self.ft[i][0]):
                # Found responsible for next iteration
                return self.ft[i]
        return self.exposed_identifier(), self.addr

    # # n joins the network;
    # # n' is an arbitrary in the network
    def join(self, n_prime_addr):
        if n_prime_addr:
            logger.debug(f'Joining network, connecting to  {n_prime_addr} -> server: {self.exposed_identifier()}')
            self.ft[0] = 'unknown'
            finger = self.remote_request(n_prime_addr, 'find_successor', self.exposed_identifier())
            self.ft[1] = finger
        else:  # n is the only in the network
            logger.debug(f'First of the network -> server: {self.exposed_identifier()}')
            self.ft[1] = (self.exposed_identifier(), self.addr)

        logger.debug(f'Successful join of: {self.exposed_identifier()} to chord')

        logger.debug(f'Starting stabilization of: {self.exposed_identifier()}')
        self.stabilize()

        logger.debug(f'Start fixing fingers of: {self.exposed_identifier()}')
        self.fix_fingers()

        logger.debug(f'Start updating successors of: {self.exposed_identifier()}')
        self.update_successors()

    # periodically verify n's immediate succesor,
    # and tell the exposed_successor about n.
    @retry(config.STABILIZATION_DELAY)
    def stabilize(self):
        logger.debug(f'\nStabilizing on server: {self.exposed_identifier() % config.SIZE}\n')
        succ = self.exposed_successor()
        x = self.remote_request(succ[1], 'predecessor')

        if x != 'unknown' and inbetween(self.exposed_identifier() + 1, succ[0] - 1, x[0]) and self.is_online(x[1]):
            self.ft[1] = x

        self.remote_request(self.exposed_successor()[1], 'notify', (self.exposed_identifier(), self.addr))

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
            finger = self.exposed_find_successor(self.exposed_identifier() + 2 ** (i - 1))
            self.ft[i] = finger

    @retry(config.UPDATE_SUCCESSORS_DELAY)
    def update_successors(self):
        logging.debug('Updating successor list on server: {self.exposed_identifier() % config.SIZE}')
        succ = self.exposed_successor()

        if self.addr[1] == succ[1]:
            return
        successors = [succ]
        remote_successors = list(self.remote_request(succ[1], 'get_successors'))[:config.SUCC_COUNT - 1]
        if remote_successors:
            successors += remote_successors
        self.successors = tuple(successors)

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

    # This should move keys to a new and delete them
    def move(self):
        pass


def main(server_email_addr: str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)),
         join_addr: str = None,
         ip_addr: str = None):
    t = ThreadedServer(EBMS(server_email_addr, join_addr, ip_addr), port=ip_addr[1] if ip_addr else config.PORT)
    t.start()


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer

    # import sys
    fire.Fire(main)

    # print(len(sys.argv))
    # if len(sys.argv) < 2:
    #     print('Usage: ./server.py <email_address> <ip_address>')
    #     logger.debug(f'Initializing ThreadedServer with default values: a.fertel@correo.estudiantes.matcom.uh.cu'
    #                  f' and 10.6.98.49.')
    #     t = ThreadedServer(EBMS(), port=config.PORT)
    # elif len(sys.argv) == 2:
    #     logger.debug(f'Initializing ThreadedServer with default email address: a.fertel@correo.estudiantes.matcom.uh.cu'
    #                  f' and ip address: {sys.argv[1]}')
    #     t = ThreadedServer(EBMS(ip_addr=sys.argv[1]), port=config.PORT)
    # elif len(sys.argv) == 3:
    #     logger.debug(f'Initializing ThreadedServer with default email address: a.fertel@correo.estudiantes.matcom.uh.cu'
    #                  f' and ip address: {sys.argv[1]}')
    #     t = ThreadedServer(EBMS(sys.argv[1], sys.argv[2]), port=config.PORT)
    # else:
    #     logger.debug(f'Initializing ThreadedServer with email address: {sys.argv[1]}, join address: {sys.argv[2]}'
    #                  f' and ip address: {sys.argv[3]}')
    #     t = ThreadedServer(EBMS(sys.argv[1], sys.argv[2], sys.argv[3]), port=config.PORT)
    # t.start()
