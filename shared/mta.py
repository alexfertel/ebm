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
        incoming_block = Block(identifier, block)

        # See what message it belongs to, insert it and check the message's lifetime
        Message.match_block_with_message(incoming_block, self.messages)

        # TODO: Keep going! :)

    def loop(self):
        while True:
            print(self)

            # Should start with the synchronization of the imap server,
            # fetching new emails. I think this is of the upmost importance,
            # because new emails could mean errors or p2p messages.
            self.recv()  # Enqueue the blocks here or do something like:
            # next_batch = self.recv()
            # for block in next_batch:
            #     self.process(block)

            # Process the next item in the queue, the goal should be
            # an item per iteration
            self.process()

            # TODO: Maybe check the status of the replicated servers if this is a server?
            # TODO: Replicate if needed.

            # TODO: Multiple queues for the subscriptions and p2ps?

            # TODO: There is not much more, right?
