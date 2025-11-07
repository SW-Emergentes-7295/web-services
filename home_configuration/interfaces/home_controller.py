from flask import Blueprint, request, jsonify
from flasgger import swag_from
from home_configuration.application.home_command_service import HomeCommandService
from home_configuration.infrastructure.home_repository import HomeRepository

home_repository = HomeRepository()
home_command_service = HomeCommandService(home_repository)
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
    "parameters":[
        {
            "name":"body",
            "in":"body",
            "required": True,
            "schema":{
                "type": "object",
                "properties":{
                    "owner_id": {"type": "int", "example": 0},
                    "map": {"type": "string", "example": "1223sas"},                   
                },
                "required": ["id", "owner_id", "map"]
            }
        }
    ],
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
    data = request.get_json()
    home = home_command_service.create_home(data.get("owner_id"),data.get("map"))
    return jsonify(home.to_type_value()), 200