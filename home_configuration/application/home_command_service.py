from home_configuration.domain.home import Home
from datetime import datetime
from home_configuration.infrastructure.home_repository import HomeRepository

class HomeCommandService:

    def __init__(self, home_repository: HomeRepository):
        self.repository = home_repository
        pass

    def create_home(self, owner_id: int, map: str):
        return self.repository.createHouse(owner_id, datetime.now(), map)
    
    def update_home(self, id: int, owner_id: int, map: str):
        return self.repository.updateHome(id, owner_id,  datetime.now(), map)
    
    def delete_home(self, id: int):
        return self.repository.deleteHome(id)