import json
import time
import copy
import email

from .block import Block
from .user import User
from .mta import Broker
from .utils import cut

class Message:
    """
    This class is an email wrapper.
    """
    def __init__(self, subject: dict = None, body: str = None):
        self._id = Message.generate_message_id()
        self._subject = subject if subject else {}
        self._body = body if body else ''
        self._blocks = self.unwrap(self.body) if self.body else []

    def __len__(self):
        return len(self._blocks)

    def __repr__(self):
        return f'Message\n\tID: {self._id}\n\tBlocks: {self._blocks}'

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

    def set_subject(self, sbj=None, **kwargs):
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
        block = Block(bid,
                      subject=self.subject.update(
                          {
                              'block_id': bid,
                              'message_id': self.id
                          }),
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
             broker: Broker,
             addresses: list,
             user: User = User('id', 'myemail@test.com', 'usr', 'passw')):
        """
        This methods represents the process of sending this message,
        which is unwrapping it (unwrap method) and enqueueing it.
        This describes a subject:
        subject = {
            'message_id': msg.id,
            'block_id': block.index,
            topic: one of [ REGISTER, LOGIN, PUBLICATION, SUBCRIBE, P2P ],
            protocol: one of [ 1, 2, 3 ] ( PUB/SUB, P2P, CONFIG )
        }
        :param broker: Broker
        :param addresses: list
        :param user: User
        :return: None
        """

        # If the length of the blocks prop is 0, the message has not been unwrapped
        if not len(self):
            self.unwrap(self.body)

        # Enqueue each of the blocks of self as EmailMessage instances
        for block in self.blocks:
            json_subject = json.dumps(block.subject, separators=(',', ':'))  # Make it a json for ease of parsing

            msg = email.message.EmailMessage()
            msg['From'] = f'{user.username}@{user.active_email}'
            msg['Subject'] = json_subject
            msg.set_content(block.text)

            for addr in addresses:
                msg['To'] = addr
                broker.enqueue(msg)
                # broker.send(addr, user, subject, str(block) + '##NumberOfBlocks##' + str(len(blocks)))
