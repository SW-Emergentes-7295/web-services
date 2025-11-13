# iam/domain/user_repository.py
from abc import ABC, abstractmethod
from .user import User


class UserRepository(ABC):

    @abstractmethod
    def save(self, user: User):
        """Guarda un usuario en la base de datos"""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        """Busca un usuario por su email"""
        pass
