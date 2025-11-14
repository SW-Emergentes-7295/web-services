from home_configuration.domain.room import Room
from home_configuration.infrastructure.room_repository import RoomRepository

class RoomCommandService:

    def __init__(self, room_repository: RoomRepository):
        self.repository = room_repository
        pass

    def create_room(self, home_id: int, width: float, height: float, depth: float):
        return self.repository.createRoom(home_id, width, height, depth)
    
    def update_room(self, id: int, width: float, height: float, depth: float):
        return self.repository.updateRoom(id, width, height, depth)
    
    def delete_room(self, id: int):
        return self.repository.deleteRoom(id)