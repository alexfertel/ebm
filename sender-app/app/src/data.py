class Data(dict):
    def __init__(self, subscribers: list, emails: list, user: str, **kwargs):
        super().__init__(**kwargs)
        self['subscribers'] = subscribers
        self['emails'] = emails
        self['user'] = user

    def to_tuple(self):
        return ('subscribers', self['subscribers']), ('emails', self['emails']), ('user', self['user'])

    def from_tuple(self, tpl: tuple):
        for k, v in tpl:
            self[k] = v
