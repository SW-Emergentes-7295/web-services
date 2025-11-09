class Room:

    def __init__(self, id: int, home_id: int, width: float, height: float, depth: float):
        self.id = id
        self.home_id = home_id
        self.width = width
        self.height = height
        self.depth = depth
    
    def updateRoom(self, width: float, height: float, depth: float):
        self.width = width
        self.height = height
        self.depth = depth

    def to_type_value(self):
        return {
            "id": self.id,
            "home_id": self.home_id,
            "width": self.width,
            "height": self.height,
            "depth": self.depth
        }