from flask import Blueprint
from flasgger import swag_from

home_configuration_bp = Blueprint('home_configuration', __name__)
@home_configuration_bp.route("/home-status", methods=["GET"])
@swag_from({
    "tags": ["Home Configuration"],
    "responses": {
        200: {
            "description": "Successful retrieval of home configuration status",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "All systems operational"
                    }
                }
            }
        }
    }

})
def get_home_configuration_status():
    return {
        "status": "All systems operational"
    }