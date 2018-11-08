from shared.message import Message
from shared.block import Block


class Communicatable:
    def send(self, address, subject, body):
        """
        This method contains the logic for sending an email, which comprises of:
        - Checking the length of the message.
        - Splitting it accordingly in case of being to large.
        - Building the blocks and _blocks identifiers.
        - Building correctly the emails according to the email library
        - Notiifying the consumer app of the result.
        :param address: email address
        :param subject: str
        :param body: str
        :return: bool
        """
        block = Block()

        while len(msg) > 2.4e+7:
            pass

    def recv(self):
        pass

