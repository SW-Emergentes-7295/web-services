# iam/application/register_user_service.py
from dataclasses import dataclass
from iam.domain.user import User
from iam.domain.user_repository import UserRepository


@dataclass
class RegisterUserRequest:
    full_name: str
    email: str
    phone: str
    password: str


@dataclass
class RegisterUserResponse:
    id: str
    full_name: str
    email: str
    phone: str
    created_at: str


class RegisterUserService:
    """Caso de uso: registrar un nuevo usuario"""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, request: RegisterUserRequest) -> RegisterUserResponse:
        # Verificar si el correo ya existe
        existing = self.repository.find_by_email(request.email)
        if existing:
            raise ValueError("A user with this email already exists")

        # Crear entidad
        user = User.create(
            full_name=request.full_name,
            email=request.email,
            phone=request.phone,
            password=request.password
        )

        # Guardar en repositorio
        self.repository.save(user)

        # Responder
        return RegisterUserResponse(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            created_at=user.created_at.isoformat()
        )
