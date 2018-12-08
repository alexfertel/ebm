class Data(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def from_tuple(self, tpl: tuple):
        if tpl:
            for k, v in tpl:
                self[k] = v
            return self
        return None
