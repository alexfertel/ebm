import hashlib
import config


class User:
    def __init__(self, address, password):
        self.__id = int(hashlib.sha1(str(address).encode()).hexdigest(), 16) % config.SIZE
        self.active_email = address
        self.__password = password

    @property
    def id(self):
        return self.__id

    @property
    def password(self):
        return self.__password

    def __eq__(self, other):
        return self.id == other.id
