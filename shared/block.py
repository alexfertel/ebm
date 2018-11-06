# This file retains the structure of blocks in order to handle them.
from .message import Message
import email


class Block:
    def __init__(self):
        self.id = Block.generate_block_id()
        self.messages = []

    @staticmethod
    def generate_block_id():
        """
        Should think of a way to generate block ids in order to keep
        then unique but to be easily mappable to its messages.
        :return: int | string
        """
        return -1

    @staticmethod
    def match_message_with_block(message, blocks):
        pass

    def add(self, message_text):
        Message(Message.generate_message_id(self))
        
