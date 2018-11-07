# This file retains the structure of blocks in order to handle them.
import time
import copy
from block import Block
import email


class Message:
    def __init__(self):
        self._id = Message.generate_message_id()
        self._blocks = []

    def __len__(self):
        return len(self._blocks)

    def __str__(self):
        return f'Message\nID: {self._id}\nBlocks: {self._blocks}'

    @property
    def id(self):
        return str(self._id)

    @property
    def blocks(self):
        return copy.deepcopy(self._blocks)

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

    def add(self, block_text):
        block = Block(Block.generate_block_id(self), block_text)
        block.set_message(self)

        self._blocks.append(block)
