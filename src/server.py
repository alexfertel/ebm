# Entry point and loop of the server
from mta import Broker
from user import User

import hashlib
from config import MAX_BITS


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

    def connect(self, user1: User, user2: User):
        """
        This method represents a p2p connection.
        :param user1: User
        :param user2: User
        :return: None
        """
        self.p2p.append((user1, user2))

    def disconnect(self, user1: User, user2: User):
        """
        This method represents a p2p disconnection
        :param user1: User
        :param user2: User
        :return: None
        """
        self.p2p.remove((user1, user2))

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
        pass

    def set(self, key, value):
        pass

    def execute(self, cmd, *args):
        attr = getattr(self, cmd)
        return attr(*args)
