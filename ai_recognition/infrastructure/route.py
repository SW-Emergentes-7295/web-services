from flask import Blueprint
from flasgger import swag_from

ai_recognition_bp = Blueprint('ai_recognition', __name__)
@ai_recognition_bp.route("/example", methods=["POST"])
@swag_from({
    "tags": ["AI Recognition"],
    "parameters": [
        {
            "name": "image",
            "in": "formData",
            "type": "file",
            "required": True,
            "description": "Image file for AI recognition"
        }
    ],
    "responses": {
        200: {
            "description": "Successful recognition",
            "schema": {
                "type": "object",
                "properties": {
                    "result": {
                        "type": "string",
                        "example": "Cat"
                    }
                }
            }
        },
        400: {
            "description": "Invalid input"
        }
    }
})
def example_recognition():
    return {"result": "Cat"}