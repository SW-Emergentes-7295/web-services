from home_configuration.domain.path import Path
from home_configuration.infrastructure.path_repository import PathRepository

class PathCommandService:

    def __init__(self, path_repository: PathRepository):
        self.repository = path_repository
        pass

    def create_path(self, home_id: int, lenght: float, rooms_ids: list):
        return self.repository.createPath(home_id, lenght, rooms_ids)
    
    def update_path(self, id: int, lenght: float):
        return self.repository.updatePath(id, lenght)
    
    def delete_path(self, id: int):
        return self.repository.deletePath(id)