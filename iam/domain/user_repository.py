# iam/domain/user_repository.py
from abc import ABC, abstractmethod
from .user import User

class UserRepository(ABC):

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    def find_all(self) -> list[User]:
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> User | None:
        pass
