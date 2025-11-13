# iam/infrastructure/route.py

from flask import Blueprint, request, jsonify
from flasgger import swag_from
import bcrypt
import jwt
import datetime

from iam.infrastructure.user_repository import SQLiteUserRepository
from iam.application.user_command_service import UserCommandService
from iam.application.user_query_service import UserQueryService

SECRET_KEY = "clave_visual_guide_123"
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
    
    # Login usuario
    @iam_bp.route("/login", methods=["POST"])
    @swag_from({
        "tags": ["IAM"],
        "description": "Inicia sesión y obtiene un token JWT",
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "example": "john@example.com"},
                        "password": {"type": "string", "example": "123456"}
                    }
                }
            }
        ],
        "responses": {
            200: {"description": "Login exitoso. Devuelve token JWT"},
            401: {"description": "Credenciales inválidas"}
        }
    })
    def login():
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "email y password son requeridos"}), 400

        user = user_repository.find_by_email(email)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Verifica contraseña encriptada
        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({"error": "Contraseña incorrecta"}), 401

        # Genera token JWT válido por 2 horas
        payload = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({
            "message": "Login exitoso",
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone
            }
        }), 200

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
