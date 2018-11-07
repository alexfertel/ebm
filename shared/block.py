# This file retains the structure of blocks in order to handle them.
import time
import copy
from message import Message
import email


class Block:
    def __init__(self):
        self._id = Block.generate_block_id()
        self._messages = []

    def __len__(self):
        return len(self._messages)

    def __str__(self):
        return f'Block\nID: {self._id}\nMessages: {self._messages}'

    @property
    def id(self):
        return str(self._id)

    @property
    def messages(self):
        return copy.deepcopy(self._messages)

    @staticmethod
    def generate_block_id():
        """
        Should think of a way to generate block ids in order to keep
        them unique but to be easily mappable to its _messages.
        :return: int | string
        """
        return 'b' + str(int(time.time() * 10000000))

    @staticmethod
    def match_message_with_block(message, blocks):
        pass

    def add(self, message_text):
        msg: Message = Message(Message.generate_message_id(self), message_text)
        msg.set_block(self)
        
        self._messages.append(msg)
