# Client library to export and use by clients


class EBMC:
    def __init__(self, client_email_addr):
        self.client_email_addr = client_email_addr

    def connect(self, server_addr):
        pass

    def send(self, email, msg):
        pass

    def recv(self):
        pass