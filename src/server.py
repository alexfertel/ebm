# Entry point and loop of the server
from .communicatable import Communicatable
from .connectible import Connectible
from .mta import Broker


class EBMS:
    def __init__(self, server_email_addr):
        # init broker
        self.mta = Broker(server_email_addr)

        # p2p connections
        self.p2p = []

        # subscriptions
        self.subscriptions = {}

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
