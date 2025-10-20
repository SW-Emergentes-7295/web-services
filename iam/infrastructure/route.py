from flask import Blueprint
from flasgger import swag_from

iam_bp = Blueprint('iam', __name__)
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
                        "id": {
                            "type": "integer",
                            "example": 1
                        },
                        "username": {
                            "type": "string",
                            "example": "johndoe"
                        },
                        "email": {
                            "type": "string",
                            "example": "johndoe@example.com"
                        }
                    }
                }
            }
        }
    }
})
def get_user_list():
    return [
        {"id": 1, "username": "johndoe", "email": "johndoe@example.com"}
    ]