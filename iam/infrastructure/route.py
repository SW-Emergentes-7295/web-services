from flask import Blueprint, request, jsonify
from flasgger import swag_from
from iam.application.register_user_service import RegisterUserService
from iam.domain.user_repository import MySQLUserRepository

iam_bp = Blueprint('iam', __name__)

# 🧠 Instanciamos el repositorio y servicio (inyección manual simple)
user_repository = MySQLUserRepository()
register_user_service = RegisterUserService(user_repository)

@iam_bp.route("/users", methods=["GET"])
@swag_from({
    "tags": ["IAM"],
    "responses": {
        200: {
            "description": "Successful retrieval of user list",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 1},
                        "username": {"type": "string", "example": "johndoe"},
                        "email": {"type": "string", "example": "johndoe@example.com"}
                    }
                }
            }
        }
    }
})
def get_user_list():
    return jsonify([
        {"id": 1, "username": "johndoe", "email": "johndoe@example.com"}
    ])

# 🚀 Nuevo endpoint: registro de usuario
@iam_bp.route("/users/register", methods=["POST"])
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
                    "full_name": {"type": "string", "example": "John Doe"},
                    "email": {"type": "string", "example": "johndoe@example.com"},
                    "phone_number": {"type": "string", "example": "+51987654321"},
                    "password": {"type": "string", "example": "MySecurePass123"}
                },
                "required": ["full_name", "email", "password"]
            }
        }
    ],
    "responses": {
        201: {
            "description": "User registered successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "message": {"type": "string"}
                }
            }
        },
        400: {"description": "Invalid input data"}
    }
})
def register_user():
    try:
        data = request.get_json()
        user_id = register_user_service.execute(data)
        return jsonify({"id": user_id, "message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
