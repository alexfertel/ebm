# This file retains the structure of _blocks in order to handle them.
import logging
from message import Message
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MESSAGE')


class Block:
    def __init__(self, identifier, text: str):
        """
        This class represents the structure of an EBM message.
        :param identifier: int | string
        :param text: str
        """
        self._id = identifier  # Must be unique, should represent the place(index) in the block
        self._text = text  # The part of the body that this block carries
        # self._message = message  # Reference to the actual message
        self._message = None  # Should be the containing block
        self._number_of_blocks = 0

    def __repr__(self):
        return f'Block: {self._id} from Message: {self.message.id}'

    def __str__(self):
        return 'Subject:{message_id: %s, block_id: %s} %s', (self.message.id, self._id, self.text)

    @property
    def index(self):
        """
        This is the property exposing the index of this block in its message
        :return: int
        """
        return int(self.id.split('B')[1])

    @property
    def text(self):
        return self._text

    @property
    def message(self):
        """
        This is the property exposing the containing block of this message or -1 in case of not knowing
        :return: int
        """
        return self._message if self._message else -1

    def set_message(self, value):
        """
        This is a wrapper of the setter of the containing message of this block
        :param value: Message
        :return: None
        """
        self._message = value

    @staticmethod
    def generate_block_id(message):
        return message.id + 'B' + str(len(message))

    @staticmethod
    def block_from_imbox_msg(raw_message):
        # TODO: ver si este es en realidad el nombre de la propiedad
        # TODO: no me queda claro como sabemos el orden de los bloques
        info = json.loads(raw_message.subject)
        return Block(info['id_message'] , raw_message.body)



def test():
    from message import Message
    m = Message()

    m.add('Hola!!')

    logger.info(m)
    logger.info(m.blocks[0])
    logger.info(m.blocks[0].text)


if __name__ == '__main__':
    test()
