class Data:
    def __init__(self):
        self.action:str = ""
        self.data:dict[str, object] = None

    def to_dict(self):
        return {'action': self.action, 'data': self.data}