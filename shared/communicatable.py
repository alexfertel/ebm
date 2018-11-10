from shared.message import Message
from shared.block import Block

import json


class Communicatable:
    def send(self, address: str, subject: dict, body: str):
        """
        This method contains the logic for sending an email, which comprises of:
        - Checking the length of the message.
        - Splitting it accordingly in case of being to large.
        - Building the blocks and _blocks identifiers.
        - Building correctly the emails according to the email library
        - Make the subject a json
        - Notiifying the consumer app of the result.
        :param address: email address
        :param subject: str
        :param body: str
        :return: bool
        """
        message = Message()

        while len(msg) > 2.4e+7:
            pass

        json_subject = json.dumps(subject)

    def recv(self):
        """
        This method contains the logic for fetching the next batch of messages
        from the imap server.
        :return: None
        """
        pass
