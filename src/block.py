import logging
import json

from email.message import EmailMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('BLOCK')


class Block(EmailMessage):
    """
    This class represents the structure of a block.
    """
    def __init__(self,
                 identifier,
                 subject: dict = None,
                 sent_from: str = None,
                 sent_to: str = None,
                 text: str = None):
        super().__init__()
        self._id = identifier  # Must be unique, should represent the place(index) in the block

        if text:
            self.set_content(text)  # The part of the body that this block carries

        if subject:
            self['Subject'] = json.dumps(subject, separators=(',', ':'))

        if sent_from:
            self['From'] = sent_from

        if sent_to:
            self['To'] = sent_to

        self._message = None  # Should be the containing message

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'Block: {self._id} from Message: {self.message.id}' + '\n\t\t' \
               + f'Subject:{self.subject}'

    def set_message(self, msg):
        self._message = msg

    @property
    def index(self):
        """
        This is the property exposing the index of this block in its message
        :return: int
        """
        return int(self._id.split('B')[1])
        # return int(self._id.split('B')[1].split('T')[1])

    @property
    def text(self):
        return self.get_content()

    @property
    def id(self):
        return self._id

    @property
    def message(self):
        """
        This is the property exposing the containing block of this message or -1 in case of not knowing
        :return: int
        """
        return self._message

    @property
    def subject(self):
        return json.loads(self['Subject'])
        # return {
        #         'message_id': self.message,
        #         'block_id': self._id
        #     }

    @property
    def sent_from(self):
        return self['From']

    @property
    def sent_to(self):
        return self['To']

    @staticmethod
    def generate_block_id(message):
        # Me parece que ya vimos esto y nos dimos cuenta de que no tenia problema
        return message.id + 'B' + str(len(message))  # + 'T' + str(int(time.time() * 10000000))
        # return message.id + 'B' + str(len(message)) + 'T' + str(int(time.time() * 10000000))

    @staticmethod
    def block_from_imbox_msg(imbox_msg):

        try:
            logger.info(f'++++++++++++++Subject from imbox msg {imbox_msg.subject} type: {type(imbox_msg.subject)} ++++++++++++++++++')
            info = json.loads(imbox_msg.subject)
            logger.info('SIIIIIIIIIIIII')
            return Block(info['block_id'],
                         info,
                         imbox_msg.sent_from,
                         imbox_msg.sent_to,
                         imbox_msg.body.plain)
        except:
            logger.info('Invalid')
            return None


def test():
    from message import Message
    m = Message()

    m.add('Hola!!')
    m.add('Hi!!')
    m.add('Bonjour!!')

    logger.info(m)
    # logger.info(m.blocks)
    # logger.info(m.blocks[0])
    # logger.info(m.blocks[0].text)


if __name__ == '__main__':
    # __package__ = 'ebm.src'
    # import sys
    # sys.path.append('/home/alex/Desktop/Alex/Projects/ebm/src')
    test()
