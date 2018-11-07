# This file retains the structure of _messages in order to handle them.
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MESSAGE')


class Message:
    def __init__(self, identifier, text: str):
        """
        This class represents the structure of an EBM message.
        :param identifier: int | string
        :param text: str
        """
        self._id = identifier  # Must be unique, should represent the place(index) in the block
        self._text = text  # Must be unique, should represent the place(index) in the block
        # self._message = message  # Reference to the actual message
        self._block = None  # Should be the containing block

    def __repr__(self):
        return f'Message: {self._id} from Block: {self.block.id}'

    @property
    def text(self):
        return self._text

    @property
    def block(self):
        """
        This is the property exposing the containing block of this message or -1 in case of not knowing
        :return: int
        """
        return self._block if self._block else -1

    def set_block(self, value):
        """
        This is a wrapper of the setter of the containing block of this message
        :param value: the identifier of the block
        :return: None
        """
        self._block = value

    @staticmethod
    def generate_message_id(block):
        return block.id + 'm' + str(len(block))


def test():
    from block import Block
    b = Block()

    b.add('Hola!!')

    logger.info(b)
    logger.info(b.messages[0])
    logger.info(b.messages[0].text)


if __name__ == '__main__':
    test()
