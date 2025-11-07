from datetime import datetime

class Home:

    def __init__(self, id:int, owner_id: int, date:datetime, map: str):
        self.id = id
        self.date = date
        self.owner_id = owner_id
        self.map = map
        self.rooms = list()

    def updateHome(self, owner_id: int, date:datetime, map: str, rooms: list):
        self.date = date
        self.owner_id = owner_id
        self.map = map
        self.rooms = rooms

    def to_type_value(self):
        return {
            "id": self.id,
            "date": self.date,
            "owner_id": self.owner_id,
            "map": self.map,
            "rooms": self.rooms
        }