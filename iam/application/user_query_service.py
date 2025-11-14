# iam/application/user_query_service.py
from iam.domain.user_repository import UserRepository

class UserQueryService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def list_users(self):
        return self.user_repository.find_all()

    def get_user_by_id(self, user_id: int):
        return self.user_repository.find_by_id(user_id)
