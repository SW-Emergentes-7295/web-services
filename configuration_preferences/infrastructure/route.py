from flask import Blueprint
from flasgger import swag_from

configuration_preferences_bp = Blueprint('configuration_preferences', __name__)
@configuration_preferences_bp.route("/settings", methods=["GET"])
@swag_from({
    "tags": ["Configuration Preferences"],
    "responses": {
        200: {
            "description": "Successful retrieval of configuration settings",
            "schema": {
                "type": "object",
                "properties": {
                    "setting1": {
                        "type": "string",
                        "example": "value1"
                    },
                    "setting2": {
                        "type": "boolean",
                        "example": True
                    }
                }
            }
        }
    }
})
def get_configuration_settings():
    return {
        "setting1": "value1",
        "setting2": True
    }