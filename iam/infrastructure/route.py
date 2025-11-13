# iam/infrastructure/route.py

from flask import Blueprint, request, jsonify
from flasgger import swag_from

from iam.infrastructure.user_repository import SQLiteUserRepository
from iam.application.user_command_service import UserCommandService
from iam.application.user_query_service import UserQueryService

iam_bp = Blueprint('iam', __name__)

def init_iam_routes(db_connection):
    user_repository = SQLiteUserRepository(db_connection)
    user_command_service = UserCommandService(user_repository)
    user_query_service = UserQueryService(user_repository)

    # Crear usuario
    @iam_bp.route("/users", methods=["POST"])
    @swag_from({
        "tags": ["IAM"],
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "example": "John Doe"},
                        "email": {"type": "string", "example": "john@example.com"},
                        "phone": {"type": "string", "example": "+51987654321"},
                        "password": {"type": "string", "example": "123456"}
                    }
                }
            }
        ],
        "responses": {
            201: {"description": "Usuario creado exitosamente"},
            400: {"description": "Datos inválidos"}
        }
    })
    def create_user():
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")

        if not all([name, email, password]):
            return jsonify({"error": "name, email y password son requeridos"}), 400

        user = user_command_service.create_user(name, email, phone, password)
        return jsonify(user.to_dict()), 201

    # Listar usuarios
    @iam_bp.route("/users", methods=["GET"])
    @swag_from({
        "tags": ["IAM"],
        "responses": {
            200: {"description": "Lista de usuarios"}
        }
    })
    def list_users():
        users = user_query_service.list_users()
        return jsonify([u.to_dict() for u in users]), 200

    # Obtener usuario por ID
    @iam_bp.route("/users/<int:user_id>", methods=["GET"])
    @swag_from({
        "tags": ["IAM"],
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "type": "integer",
                "required": True,
                "description": "ID del usuario"
            }
        ],
        "responses": {
            200: {"description": "Usuario encontrado"},
            404: {"description": "Usuario no encontrado"}
        }
    })
    def get_user_by_id(user_id):
        user = user_query_service.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify(user.to_dict()), 200

    return iam_bp
