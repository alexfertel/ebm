# Message Transfer Agent
# This retains the logic of controlling and managing message correctness
# So, how do you know that a block is part of a message? how do you identify
# a block? Blocks should have ids, and we should keep a dict holding
# currently known message blocks while they're alive.
import email
from .message import Message
from .block import Block
from .utils import *
from user import User
import time
from threading import Thread


class Broker(Communicatable):
    def __init__(self, addr):
        """
        This class represents the message transfer agent type.
        """
        self.messages = {}  # blocks
        self.queue = []  # Block queue

        super().__init__()
        
        self.th = Thread(target = self.fetch_in, args=(self,))
        self.th.start()


    def __str__(self):
        queue = '*' * 25 + ' Queue ' + '*' * 25 + '\n' + f'{self.queue}' + '\n'
        messages = '*' * 25 + ' Queue ' + '*' * 25 + '\n' + f'{self.messages}' + '\n'
        return queue + messages

    def enqueue(self, block):
        self.queue.append(block)
    
    def enqueue_list(self, blocks: list):
        self.queue.extend(blocks)

    def dequeue(self):
        return self.queue.pop(0)

    def fetch_in(self):
        while True:
            imbox = list(map(lambda x: Block.block_from_imbox_msg(x), self.recv()))
            self.enqueue_list(imbox)
            time.sleep(1)
            
        

    def process(self):
        # The broker received another block, so lets process it and see if it is part of the current message.
        # The client should have used generate_block_id to create the identifier and it should come in the
        # email Subject. Parse the email and get the Subject.

        # Parse the subject and get the identifier
        # identifier = 'None or some identifier should be here after parsing'
        # incoming_block = Block(identifier, block)

        # See what message it belongs to, insert it and check the message's lifetime
        # Message.match_block_with_message(incoming_block, self.messages)

        # TODO: Keep going! :)
        pass

    def loop(self):
        while True:
            print(self)

            # Should start with the synchronization of the imap server,
            # fetching new emails. I think this is of the upmost importance,
            # because new emails could mean errors or p2p messages.
            
            # Process the next item in the queue, the goal should be
            # an item per iteration

            # TODO: Maybe check the status of the replicated servers if this is a server?
            # TODO: Replicate if needed.

            # TODO: Multiple queues for the subscriptions and p2ps?

            # TODO: There is not much more, right?

            if len(self.queue) > 0:
                block = self.dequeue()
                if self.block.message in self.messages:
                    self.message[block.message].push(block)
                else:
                    self.message[block.message] = [block]

                if len(self.message[block.message]) == block._number_of_blocks:
                    completed_message = merge(self.message[block.message])
                    # TODO: este message, hay que empezar a usarlo, pero no se esta teniendo en 
                    # cuenta el orden que debe tener con respecto al resto de msg

    @staticmethod
    def merge(items: list[Blocks]):
        """
        Merge all blocks of the same message
        """
        sort(items, key=lambda x: x.index)
        return ''.join(map(lambda x: x.text, items))

    def send_message(self, address: list, subject: dict, body: str):
        """
            subject = {
                'message_id': msg.id,
                'block_id': block.index
            }
        """
        blocks = cut(body, max_length)

        msg = Message()

        for item in blocks:
            msg.add(item)

        for block in msg.blocks():
            user = User('id','myemail@test.com','usr','passw')
            subject = {
                'message_id': msg.id,
                'block_id': block.index,
                'type': msg.type
            }

            for addr in address:
                self.send(addr, user, subject, str(block)++ '##NumberOfBlocks##' + str(len(blocks))

