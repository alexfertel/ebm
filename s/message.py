# This file retains the structure of messages in order to handle them.
import email


class Message:
    def __init__(self, identifier, message: email.message.EmailMessage):
        """
        This class represents the structure of an EBM message.
        :param identifier: int | string
        :param message: email.message.EmailMessage
        """
        self._id = identifier  # Must be unique, should represent the place(index) in the block
        self._message = message  # Reference to the actual message
        self._block = None  # Should be the containing block

    def __str__(self):
        return 'Message ' + self._id

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
