# iam/application/user_command_service.py
from iam.domain.user import User
from iam.domain.user_repository import UserRepository

class UserCommandService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, name: str, email: str, phone: str, password: str) -> User:
        user = User(None, name, email, phone, password)
        return self.user_repository.save(user)
