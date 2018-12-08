# Entry point and loop of the server
from mta import Broker
from user import User

import hashlib
from config import *


class Finger:
    def __init__(self, start: int = -1, interval: tuple = tuple(), node: int = -1):
        self.start = start
        self.interval = interval
        self.node = node


class EBMS:
    def __init__(self, server_email_addr):
        # init broker
        self.mta = Broker(server_email_addr)
        self.mta.user = self

        # p2p connections
        self.p2p = []

        # subscriptions
        self.subscriptions = {}

        # DHT
        self.dht = {}

        self.answer = None

        # Chord setup
        self.__id = int(hashlib.sha1(str(identifier).encode()).hexdigest(), 16)
        # Compute Finger Table computable properties (start, interval).
        # The .node property is computed when a node joins or leaves and at the chord start
        self.ft = {
            i: Finger(start=(self.identifier + 2 ** (i - 1)) % 2 ** MAX_BITS)
            for i in range(1, MAX_BITS + 1)
        }

        for i in range(1, len(self.ft)):
            finger.interval = self.ft[i].start, self.ft[i + 1].start

        self.ft[0] = 'unknown'  # At first the predecessor is unknown

        # Map between nodes and their emails
        self.nodeSet = {}

    def subscribe(self, subscriber: User, publisher: User):
        """
            This method represents a subscription.
            :param subscriber: User
            :param publisher: User
            :return: None
            """
        self.subscriptions[publisher].append(subscriber)

    def unsubscribe(self, subscriber: User, publisher: User):
        """
        This method represents an unsubscription.
        :param subscriber: User
        :param publisher: User
        :return: None
        """
        self.subscriptions[publisher].remove(subscriber)

    def publish(self, msg):
        subscription_list_id = str(self.identifier) + 'subs'

        value = self.get(hashlib.sha1(subscription_list_id.encode()).hexdigest())

        subs = value.strip('[]').split(',')
        subs = [item.strip() for item in subs]

        for sub in subs:
            user_mail = self.get(hashlib.sha1(sub.encode()).hexdigest())

            msg = self.mta.build_message('', protocol=PROTOCOLS['PUB/SUB'], topic=TOPICS['CMD'], cmd='GET',
                                         args=f'{key}')
            # msg.send(self.mta, , msg)

        # while True:

        # value = self.get(hashlib.sha1(subscription_list_id.encode()).hexdigest())

    @property
    def identifier(self):
        return self.__id

    @property
    def successor(self) -> int:
        return self.ft[1].node

    @property
    def predecessor(self) -> int:
        return self.ft[0].node

    def find_successor(self, identifier) -> str:
        n_prime = self.find_predecessor(identifier)

        return self.nodeSet[n_prime.successor]

    def find_predecessor(self, identifier) -> int:
        # compute closest finger preceding id
        if not (self.identifier < identifier <= self.successor):
            for i in range(len(self.ft) - 1, 0, -1):
                if self.is_responsible(identifier):
                    # Found predecessor
                    return self.nodeSet[self.ft[i].node]
        # Found node responsible for next iteration
        return self.identifier

    def is_responsible(self, identifier):
        return self.ft[i].interval[0] + 1 < identifier <= self.ft[i].interval[1] + 1

    def get(self, key):
        if self.is_responsible(key):
            return self.dht[key]

        msg = self.mta.build_message('', protocol=3, topic='CMD', cmd='GET', args=f'{key}')

        self.find_successor(key)

        return self.answer

    def set(self, key, value):
        pass

    def execute(self, cmd, *args):
        attr = getattr(self, cmd)
        return attr(*args)
