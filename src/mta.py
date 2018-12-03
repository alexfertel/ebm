# Message Transfer Agent
# This retains the logic of controlling and managing message correctness
# So, how do you know that a block is part of a message? how do you identify
# a block? Blocks should have ids, and we should keep a dict holding
# currently known message blocks while they're alive.
import smtplib
import ssl
import time

from block import Block
from user import User
from threading import Thread
from imbox import Imbox
from email.message import EmailMessage


class Broker:
    def __init__(self, addr):
        """
        This class represents the message transfer agent type.
        """
        super().__init__()

        self.addr = addr
        self.messages = {}  # blocks
        self.queue = []  # Block queue

        self.user = None

        self.start_thread(self.fetch, (self,))

    def __str__(self):
        queue = '*' * 25 + ' Queue ' + '*' * 25 + '\n' + f'{self.queue}' + '\n'
        messages = '*' * 25 + ' Messages ' + '*' * 25 + '\n' + f'{self.messages}' + '\n'
        return queue + messages

    def enqueue(self, block=None, *blocks):
        """
        Enqueues the block or the *blocks into the broker's queue.
        :param block: Block
        :return: None
        """
        if block:
            self.queue.append(block)
        self.queue.extend(*blocks)

    def dequeue(self) -> Block:
        """
        Dequeues the first block from the broker's queue.
        :return: Block
        """
        return self.queue.pop(0)

    def start_thread(self, target: function, args: tuple):
        th = Thread(target=target, args=args)
        th.start()

    def fetch(self):
        while True:
            imbox = list(map(lambda x: Block.block_from_imbox_msg(x), self.recv(self.addr)))
            self.enqueue(imbox)
            time.sleep(1)

    def process(self):
        # The broker received another block, so lets process it and see if it is part of the current message.
        # The client should have used generate_block_id to create the identifier and it should come in the
        # email Subject. Parse the email and get the Subject.
        block = self.dequeue()

        subject = block.subject

        if subject['topic'] == 'CMD':  # It is an RPC command
            # So this is something like n.find_predecessor(id)
            # where this node is n, so if we need to chain a call to another node
            # it would recursively send the RPC call
            # therefore receivng an email with protocol 4 with the answer
            answer = self.user.execute(subject['cmd'], *subject['args'])
            msg = self.mta.build_message(answer, protocol=3, topic='ANSWER')
            self.send(block.sent_from, msg)

        if subject['topic'] == 'ANSWER':  # It is an answer from an RPC command
            # If the node property in the subject equals this node's id then the answer is for this node
            self.user.answer = answer
            return answer

        if block.message in self.messages:
            self.messages[block.message].push(block)
        else:
            self.messages[block.message] = [block]

        # if len(self.messages[block.message]) == len(list(filter(lambda x: x[0] == block.message,
        #                                                         self.messages.items()))[0][0]):
        #     complete_message = Broker.merge(self.messages[block.message])

        # Parse the subject and get the identifier
        # identifier = 'None or some identifier should be here after parsing'
        # incoming_block = Block(identifier, block)

        # See what message it belongs to, insert it and check the message's lifetime
        # Message.match_block_with_message(incoming_block, self.messages)

        pass

    def loop(self):
        while True:
            print(self)

            if len(self.queue) > 0:
                self.process()
            # Should start with the synchronization of the imap server,
            # fetching new emails. I think this is of the upmost importance,
            # because new emails could mean errors or p2p messages.

            # Process the next item in the queue, the goal should be
            # an item per iteration

            # TODO: Check the status of the replicated servers.
            # TODO: Replicate if needed.

            # TODO: Multiple queues for the subscriptions and p2ps?

            # TODO: There is not much more, right?

    @staticmethod
    def merge(items: list) -> str:
        """
        Merge all blocks of the same message
        :param items: list
        :return: str
        """
        items.sort(key=lambda x: x.index)
        return ''.join(map(lambda x: x.text, items))

    @staticmethod
    def send(addr, msg: EmailMessage):
        """
        This method contains the logic for sending an email, which comprises of:
        - Connect to the smtp server
        - Checking the length of the message.
        - Splitting it accordingly in case of being to large.
        - Building the blocks and _blocks identifiers.
        - Building correctly the emails according to the email library
        - Make the subject a json
        - Notiifying the consumer app of the result.

        :param addr: str
        :param msg: Block
        :return: bool
        """
        smtp: smtplib.SMTP = smtplib.SMTP(addr)  # smtp instance
        smtp.set_debuglevel(1)
        smtp.send_message(msg)
        smtp.quit()

    @staticmethod
    def recv(addr, user: User = User('id', 'myemail@test.com', 'usr', 'passw')):
        """
        This method contains the logic for fetching the next batch of messages
        from the imap server.
        :return: list[Block]
        """
        ssl_context = ssl.create_default_context()

        ssl_context.check_hostname = False

        ssl_context.verify_mode = ssl.CERT_NONE

        unread = []
        with Imbox(addr,
                   username=user.username,
                   password=user.password,
                   ssl=True,
                   ssl_context=ssl_context,
                   starttls=False) as imbox:
            for _, message in imbox.messages(unread=True):
                unread.append(message)  # For now just append to the queue

        return unread

    def build_message(self, body: str, protocol: int = 2, topic: str = 'P2P', cmd: str = '', args: list = None):
        """
        subject = {
            'message_id': msg.id,
            'block_id': block.index,
            'topic': one of [ REGISTER, LOGIN, PUBLICATION, SUBCRIBE, P2P, CMD, ANSWER ],
            'protocol': one of [ 1, 2, 3 ] ( PUB/SUB, CONFIG, RPC ),
            'cmd': one of [find_predecessor, find_succesor],
            'args': a list of args for the cmd,
            'node': node identifier in chord,
            'method_answer': 
        }
        :param body: text
        :param protocol: subject.protocol
        :param topic: subject.topic
        :param cmd: subject.cmd
        :param args: subject.args
        :return: Message
        """

        msg = Message(
            body=body,
            subject={
                'topic': topic,
                'protocol': protocol,
                'cmd': cmd,
                'args': args,
                'node': self.identifier
            })

        return msg
