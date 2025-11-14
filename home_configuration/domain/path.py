class Path:

    def __init__(self, id:int, home_id:int, lenght:float, rooms_ids:list):
        self.id = id
        self.home_id = home_id
        self.lenght = lenght
        self.rooms_ids = rooms_ids

    def updatePath(self, lenght: float):
        self.lenght = lenght

    def to_type_value(self):
        return {
            "id": self.id,
            "home_id": self.home_id,
            "lenght": self.lenght,
            "rooms_ids": self.rooms_ids
        }