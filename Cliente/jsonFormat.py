import json

class Data:
    def __init__(self):
        self.action:str = ""
        self.data:dict[str, object] = None

    def to_dict(self):
        return {'action': self.action, 'data': self.data}
    
    @classmethod
    def from_dict(self, dataJson: str):
        data: dict = json.loads(dataJson)
        self.action: str = data['action']
        self.data: dict[str, object] = data['data']