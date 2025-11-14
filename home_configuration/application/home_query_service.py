from home_configuration.domain.home import Home
from datetime import datetime
from home_configuration.infrastructure.home_repository import HomeRepository

class HomeQueryService:

    def __init__(self, home_repository: HomeRepository):
        self.repository = home_repository
        pass

    def get_all_homes(self):
        return self.repository.getAllHomes()

    def get_home_by_id(self, home_id: int):
        return self.repository.getHomeById(home_id)