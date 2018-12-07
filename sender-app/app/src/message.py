import json
import logging
import time
import copy
import email

from .block import Block
from .user import User
from .utils import cut

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MESSAGE')


class Message:
    """
    This class is an email wrapper.
    """
    def __init__(self, subject: dict = None, body: str = None, message_id:str= ''):
        self._id = message_id if message_id else Message.generate_message_id()
        self._subject = subject if subject else {}
        self._body = body if body else ''
        self._blocks = []
        self._blocks = self.unwrap(self.body) if self.body else []

    def __len__(self):
        return len(self.blocks)

    def __repr__(self):
        representation = f'\nMessage:\n\tID: {self._id}\n\tBlocks: [\n\t\t'

        for block in self.blocks:
            representation += str(block) + f'\n\t\t'

        representation += f']'
        return representation

    @property
    def id(self) -> str:
        """
        _id getter.
        :return: str
        """
        return str(self._id)

    @property
    def blocks(self) -> list:
        """
        _blocks getter.
        :return: list
        """
        return copy.deepcopy(self._blocks)

    @property
    def subject(self) -> dict:
        """
        _subject getter.
        :return: dict
        """
        return self._subject

    @property
    def body(self) -> str:
        """
        _body getter.
        :return: str
        """
        return self._body

    @staticmethod
    def generate_message_id():
        """
        Should think of a way to generate message ids in order to keep
        them unique but to be easily mappable to its blocks.
        :return: int | string
        """
        return 'M' + str(int(time.time() * 10000000))

    @staticmethod
    def match_block_with_message(block, messages):
        """

        :param block: Block
        :param messages: list
        """
        pass

    def update_subject(self, sbj=None, **kwargs):
        """
        Subject setter.
        :param sbj: dict
        :param kwargs: dict
        """
        if sbj:
            self._subject.update(sbj)
        self._subject.update(kwargs)

    def add(self, text: str) -> None:
        """
        Wraps a piece of this Message in a Block.
        :param text: str
        :return: None
        """
        # Init a new Block with the text arg and a new id
        bid = Block.generate_block_id(self)
        subjectcopy = copy.copy(self.subject)
        subjectcopy.update({
            'block_id': bid,
            'message_id': self.id
        })
        block = Block(bid,
                      subject=subjectcopy,
                      text=text)

        block.set_message(self)  # Set self as the message of the new Block

        self._blocks.append(block)  # Add the new Block to this Message (self) blocks

    def unwrap(self, body: str) -> None:
        """
        Builds the blocks of a message. Given a text, unwrap() cuts it
        in pieces and makes them blocks of self (an instance of Message)
        :param body: str
        :return: None
        """
        for item in cut(body):
            self.add(item)

    def send(self,
             broker,
             addr: str,
             user: User = User('id', 'myemail@test.com', 'usr', 'passw')):
        """
        This methods represents the process of sending this message,
        which is unwrapping it (unwrap method) and enqueueing it.
        This describes a subject:
        subject = {
            'message_id': msg.id,
            'block_id': block.index,
            'topic': one of [ REGISTER, LOGIN, PUBLICATION, SUBCRIBE, P2P, CMD, ANSWER ],
            'protocol': one of [ 1, 2, 3 ] ( PUB/SUB, CONFIG, RPC ),
            'cmd': one of [],
            'args': a list of args for the cmd,
            'node': node identifier in chord
        }
        :param broker: Broker
        :param addr: str
        :param user: User
        :return: None
        """

        # If the length of the blocks prop is 0, the message has not been unwrapped
        if not len(self):
            self.unwrap(self.body)

        # Enqueue each of the blocks of self as EmailMessage instances
        for block in self.blocks:
            block['Subject'] = json.dumps(block.subject, separators=(',', ':'))  # Make it a json for ease of parsing
            block['From'] = f'{user.active_email}'
            block['To'] = addr
            broker.enqueue(block)

            # for addr in addresses:
            # broker.send(addr, user, subject, str(block) + '##NumberOfBlocks##' + str(len(blocks)))


def test():
    m = Message()

    m.add('Hola!!')
    m.add('Hi!!')
    m.add('Bonjour!!')

    logger.info(m)


if __name__ == '__main__':
    test()
