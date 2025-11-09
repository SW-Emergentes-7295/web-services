from home_configuration.domain.path import Path
from home_configuration.infrastructure.path_repository import PathRepository

class PathQueryService:

    def __init__(self, path_repository: PathRepository):
        self.repository = path_repository
        pass

    def get_all_paths(self):
        return self.repository.getAllPaths()
    
    def get_path_by_id(self, path_id: int):
        return self.repository.getPathById(path_id)