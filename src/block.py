# This file retains the structure of _blocks in order to handle them.
import logging
from message import Message
import json
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('BLOCK')


class Block:
    def __init__(self, identifier, text: str):
        # No entendi esto:
        # def __init__(self, identifier, text: str, number_of_blocks=0):
        """
        This class represents the structure of an EBM message.
        :param identifier: int | string
        :param text: str
        :param number_of_blocks: int
        """
        self._id = identifier  # Must be unique, should represent the place(index) in the block
        self._text = text  # The part of the body that this block carries
        # self._message = message  # Reference to the actual message
        self._message = None  # Should be the containing message
        # No entendi esto:
        # self._number_of_blocks = number_of_blocks

    def __repr__(self):
        return f'Block: {self._id} from Message: {self.message.id}' + '\n' \
               + f'Subject:{{\n\t{self.message.id},\n\t{self.id},\n\t{self.text}\n}}'

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
        # Me parece que ya vimos esto y nos dimos cuenta de que no tenia problema
        return message.id + 'B' + str(len(message))  # + 'T' + str(int(time.time() * 10000000))
        # return message.id + 'B' + str(len(message)) + 'T' + str(int(time.time() * 10000000))

    @staticmethod
    def block_from_imbox_msg(raw_message):
        # TODO: ver si (subject, body) es en realidad el nombre de la propiedad
        # TODO: no me queda claro como sabemos el orden de los bloques
        info = json.loads(raw_message.subject)
        body, number_blocks = raw_message.body.split('##NumberOfBlocks##')
        return Block(info['block_id'], body, int(number_blocks[1]))


def test():
    from message import Message
    m = Message()

    m.add('Hola!!')

    logger.info(m)
    logger.info(m.blocks[0])
    logger.info(m.blocks[0].text)


if __name__ == '__main__':
    test()
