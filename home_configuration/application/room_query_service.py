from home_configuration.domain.room import Room
from home_configuration.infrastructure.room_repository import RoomRepository

class RoomQueryService:

    def __init__(self, room_repository: RoomRepository):
        self.repository = room_repository
        pass

    def get_all_rooms(self):
        return self.repository.getAllRooms()
    
    def get_room_by_id(self, room_id: int):
        return self.repository.getRoomById(room_id)