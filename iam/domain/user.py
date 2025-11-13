# iam/domain/user.py
from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


@dataclass
class User:
    id: str
    full_name: str
    email: str
    phone: str
    password_hash: str
    created_at: datetime

    @staticmethod
    def create(full_name: str, email: str, phone: str, password: str):
        """Crea un nuevo usuario con contraseña hasheada."""
        password_hash = generate_password_hash(password)
        return User(
            id=str(uuid4()),
            full_name=full_name,
            email=email.lower(),
            phone=phone,
            password_hash=password_hash,
            created_at=datetime.utcnow()
        )

    def verify_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
