from domain.home import Home
from infrastructure.home_repository import HomeRepository

class HomeCommandService:

    def __init__(self, home_repository: HomeRepository):
        self.repository = home_repository
        pass

    def create_home(self, id: int, owner_id: int, map: str):
        home = Home(id, owner_id, map)
        return self.repository.save(home)