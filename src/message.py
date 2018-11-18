# This file retains the structure of blocks in order to handle them.
import time
import copy
import email

from .block import Block


class Message:
    def __init__(self):
        self._id = Message.generate_message_id()
        self._blocks = []
        self._subject = {}

    def __len__(self):
        return len(self._blocks)

    def __str__(self):
        return f'Message\nID: {self._id}\nBlocks: {self._blocks}'

    @property
    def id(self) -> str:
        return str(self._id)

    @property
    def blocks(self) -> list:
        return copy.deepcopy(self._blocks)

    @property
    def subject(self) -> dict:
        return self._subject

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
        pass

    def set_subject(self, sbj=None, **kwargs):
        if sbj:
            self._subject.update(sbj)
        self._subject.update(kwargs)

    def add(self, text: str) -> None:
        """
        Wraps a piece of this Message in a Block.
        :param text: str
        :return: None
        """
        block = Block(Block.generate_block_id(self), text)  # Init a new Block with the text arg nad a new id

        block.set_message(self)  # Set self as the message of the new Block

        self._blocks.append(block)  # Add the new Block to this Message (self) blocks

    def wrap_up(self, body: str, size: int) -> None:
        """
        Builds the blocks of a message. Given a text wrap_up() cuts it 
        in pieces and makes them blocks of self (an instance of Message)
        :param body: str
        :param size: int
        :return: None
        """
        for item in utils.cut(body, size):
            self.add(item)

    def broadcast(self, addresses: list):
        """
        This method builds messages (emails) for each of the addresses of the list
        :param addresses: list
        :return: None
        """

    def send(self, broker: Broker, addresses: list, body: str):
        """
        This methods represents the process of sending this message,
        which is wrapping it up (wrap_up method) and enqueue it.
        This describes a subject:
        subject = {
            'message_id': msg.id,
            'block_id': block.index,
            topic: one of [ REGISTER, LOGIN, PUBLICATION, SUBCRIBE, P2P ],
            protocol: one of [ 1, 2, 3 ] ( PUB/SUB, P2P, CONFIG )
        }
        :param broker: Broker
        :param addresses: list
        :param subject: dict
        :param body: str
        :return: None
        """

        for block in self.blocks:
            user = User('id', 'myemail@test.com', 'usr', 'passw')
            self.subject.update({
                'message_id': msg.id,
                'block_id': block.index,
            })

            for addr in addresses:
                broker.send(addr, user, subject, str(block) + '##NumberOfBlocks##' + str(len(blocks)))
