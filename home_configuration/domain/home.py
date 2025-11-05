from datetime import datetime

class Home:

    def __init__(self, id:int, owner_id: int, map: str):
        self.id = id
        self.date = datetime.now()
        self.owner_id = owner_id
        self.map = map
        self.rooms = list()

    def updateHome(self, owner_id: int, map: str, rooms: list):
        self.date = datetime.now()
        self.owner_id = owner_id
        self.map = map
        self.rooms = rooms