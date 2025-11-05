from flask import Blueprint
from flasgger import swag_from

home_controller_bp = Blueprint('home_controlller', __name__)

@home_controller_bp.route("/getHomes", methods=["GET"])
@swag_from({
    "tags": ["Home Controller"],
    "responses": {
        200: {
            "description": "Successful retrieval all homes",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Homes"
                    }
                }
            }
        }
    }

})
def get_homes():
    return {
        "home": "yes"
    }

@home_controller_bp.route("/getHomeById", methods=["GET"])
@swag_from({
    "tags": ["Home Controller"],
    "responses": {
        200: {
            "description": "Successful retrieval home",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Home"
                    }
                }
            }
        }
    }

})
def get_home_by_id():
    return {
        "home": "yes"
    }
    

@home_controller_bp.route("/createHome", methods=["POST"])
@swag_from({
    "tags": ["Home Controller"],
    "responses": {
        200: {
            "description": "Successful created home",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Home"
                    }
                }
            }
        }
    }

})
def create_home():
    return {
        "home": "yes"
    }
    