from shared.message import Message
from shared.block import Block

P2P = 1
PUBSUB = 2
CONFIG = 3


class Communicatable:
    def send(self, address, msg, protocol=CONFIG):
        """
        This method contains the logic for sending an email, which comprises of:
        - Checking the length of the message.
        - Splitting it accordingly in case of being to large.
        - Building the blocks and _blocks identifiers.
        - Building correctly the emails according to the email library
        - Notiifying the consumer app of the result.
        :param address: email address
        :param msg: text
        :return: bool
        """
        block = Block()

        while len(msg) > 2.4e+7:
            pass

    def recv(self):
        pass

