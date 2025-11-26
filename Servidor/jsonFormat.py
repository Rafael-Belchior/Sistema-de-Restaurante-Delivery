import json

class Data:
    def __init__(self, action: str = "", data: dict[str, object] = {}):
        self.action:str = action
        self.data:dict[str, object] = data

    def to_dict(self):
        return {'action': self.action, 'data': self.data}
    
    @classmethod
    def from_dict(self, dataJson: str):
        data: dict = json.loads(dataJson)
        self.action: str = data['action']
        self.data: dict[str, object] = data['data']