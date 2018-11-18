class User:
    def __init__(self, identifier, address, username, password):
        self._id = identifier
        self._username = username
        self.active_email = address
        self.email_addresses = [address]
        self.__password = password

    @property
    def id(self):
        return self._id

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self.__password

    def __eq__(self, other):
        return self.id == other.id
