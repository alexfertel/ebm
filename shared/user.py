class User:
    def __init__(self, identifier, address):
        self._id = identifier
        self.active_email = address
        self.email_addresses = [address]

    @property
    def id(self):
        return self._id

    def __eq__(self, other):
        return self.id == other.id