# Message Transfer Agent
# This retains the logic of controlling and managing message correctness
# So, how do you know that a block is part of a message? how do you identify
# a block? Blocks should have ids, and we should keep a dict holding
# currently known message blocks while they're alive.
import email
from .message import Message
from .block import Block


class Broker(Connectible, Communicatable):
    def __init__(self, addr):
        """
        This class represents the message transfer agent type.
        """
        self.messages = {}  # blocks
        self.queue = []  # Block queue

        super().__init__(addr)

    def __str__(self):
        queue = '*' * 25 + ' Queue ' + '*' * 25 + '\n' + f'{self.queue}' + '\n'
        messages = '*' * 25 + ' Queue ' + '*' * 25 + '\n' + f'{self.messages}' + '\n'
        return queue + messages

    def enqueue(self, message):
        self.queue.append(message)

    def dequeue(self):
        return self.queue.pop(0)

    def process(self):
        # The broker received another block, so lets process it and see if it is part of the current message.
        # The client should have used generate_block_id to create the identifier and it should come in the
        # email Subject. Parse the email and get the Subject.
        block = self.dequeue()

        # Parse the subject and get the identifier
        identifier = 'None or some identifier should be here after parsing'

        if identifier:
            incoming_block = Block(identifier, block)
        else:
            incoming_block = Block(Block.generate_block_id(), block)

        # See what message it belongs to, insert it and check the message's lifetime
        Message.match_block_with_message(incoming_block, self.messages)

    def loop(self):
        while True:
            print(self)
