# Message Transfer Agent
# This retains the logic of controlling and managing message correctness
# So, how do you know that a message is part of a block? how do you identify
# a message? Messages should have ids, and we should keep a dict holding,
# currently known message blocks while they're alive.
import email
from .message import Message
from .block import Block


class Broker:
    def __init__(self):
        self.current_blocks = {}
        self.queue = []

    def process(self, message: email.message.EmailMessage):
        # The broker receives another message, so lets process it and see if it is part of the current queue.
        # The client should have used generate_block_id to create the identifier and it should come in the
        # email Subject. Parse the email and get the Subject.

        # Parse the subject and get the identifier
        identifier = 'None or some identifier should be here after parsing'

        if identifier:
            incoming_message = Message(identifier, message)
        else:
            incoming_message = Message(Block.generate_block_id(), message)

        # See what block it belongs to, insert it and check block's lifetime
        Block.match_message_to_block(incoming_message, self.current_blocks)
